#!/usr/bin/python -u

from time import sleep
from socket import getfqdn
from json import loads
from commands import getoutput
import string
from re import sub

fqdn=getfqdn()

def get_pg_states(pg_data_pg_stats):
  state_stats = {
    "active" : 0,
    "clean" : 0,
    "crashed" : 0,
    "creating" : 0,
    "degraded" : 0,
    "down" : 0,
    "stale" : 0,
    "inconsistent" : 0,
    "peering" : 0,
    "repair" : 0,
    "replay" : 0,
    "scanning" : 0,
    "scrubbing" : 0,
    "scrubq" : 0,
    "splitting" : 0,
    "stray" : 0,
    "inactive" : 0,
    "remapped" : 0,
    "deep" : 0,
    "backfilling" : 0,
    "recovering" : 0,
    "wait_backfill" : 0,
    "recovery_wait" : 0,
  }
  for pg in pg_data_pg_stats:
    state = pg["state"]
    slist = string.split(state, "+")
    for s in slist:
      if s in state_stats:
        state_stats[s] += 1
  return state_stats

def un2zero (di,key):
	if di.has_key(key):
		return int(di[key])
	else:
		return 0

while True:
	df_data = loads(getoutput('ceph df detail --format=json 2>/dev/null'))
        pg_data = loads(getoutput('ceph pg  dump --format=json 2>/dev/null'))
	st_data = loads(getoutput('ceph -s --format=json 2>/dev/null'))
	osd_perf = loads(getoutput('ceph osd perf --format=json 2>/dev/null'))
	po_data = loads(sub(r'-inf','0',getoutput('ceph osd pool stats --format=json 2>/dev/null')))
	state_stats = get_pg_states(pg_data['pg_stats'])
	iops=un2zero(st_data['pgmap'],'op_per_sec')
	degraded=un2zero(st_data['pgmap'],'degraded_objects')

	for pool in po_data:
		print "PUTVAL \"" + fqdn + "/ceph/gauge-pool-" + pool['pool_name'] + "-iops\" interval=10 N:%d" % un2zero(pool['client_io_rate'],'op_per_sec')
		print "PUTVAL \"" + fqdn + "/ceph/bytes-pool-" + pool['pool_name'] + "-rps\" interval=10 N:%d" % un2zero(pool['client_io_rate'],'read_bytes_sec')
		print "PUTVAL \"" + fqdn + "/ceph/bytes-pool-" + pool['pool_name'] + "-wps\" interval=10 N:%d" % un2zero(pool['client_io_rate'],'write_bytes_sec')
	for pool in df_data['pools']:
		print "PUTVAL \"" + fqdn + "/ceph/gauge-pool-" + pool['name'] + "-objects\" interval=10 N:%d" % un2zero(pool['stats'],'objects')
		print "PUTVAL \"" + fqdn + "/ceph/df-pool-" + pool['name'] + "\" interval=10 N:%d:%d" % (un2zero(pool['stats'],'bytes_used'),df_data['stats']['total_avail_bytes']/3)

	print "PUTVAL \"" + fqdn + "/ceph/df-total\" interval=10 N:%d:%d" % (df_data['stats']['total_used_bytes'],df_data['stats']['total_avail_bytes'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-total-objects\" interval=10 N:%d" % df_data['stats']['total_objects']
	print "PUTVAL \"" + fqdn + "/ceph/gauge-degraded-objects\" interval=10 N:%d" % degraded
	print "PUTVAL \"" + fqdn + "/ceph/gauge-total-pgs\" interval=10 N:%d" % len(pg_data['pg_stats'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-backfilling-pgs\" interval=10 N:%d" % int(state_stats['wait_backfill'] + state_stats['backfilling'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-recovering-pgs\" interval=10 N:%d" % int(state_stats['recovery_wait'] + state_stats['recovering'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-total-iops\" interval=10 N:%d" % iops
	print "PUTVAL \"" + fqdn + "/ceph/bytes-recovery-bps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'recovering_bytes_per_sec')
	print "PUTVAL \"" + fqdn + "/ceph/bytes-rps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'read_bytes_sec')
	print "PUTVAL \"" + fqdn + "/ceph/bytes-wps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'write_bytes_sec')
	print "PUTVAL \"" + fqdn + "/ceph/gauge-recovery-objps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'recovering_objects_per_sec')
	max_apply_latency=0
	max_commit_latency=0
	for osd in osd_perf['osd_perf_infos']:
		if max_apply_latency < osd['perf_stats']['apply_latency_ms']:
			max_apply_latency = osd['perf_stats']['apply_latency_ms']
		if max_commit_latency < osd['perf_stats']['commit_latency_ms']:
                        max_commit_latency = osd['perf_stats']['commit_latency_ms']
		print "PUTVAL \"" + fqdn + "/ceph/latency-apply-%d\" interval=10 N:%d" % (osd['id'], osd['perf_stats']['apply_latency_ms'])
		print "PUTVAL \"" + fqdn + "/ceph/latency-commit-%d\" interval=10 N:%d" % (osd['id'], osd['perf_stats']['commit_latency_ms'])
	print "PUTVAL \"" + fqdn + "/ceph/latency-apply-max\" interval=10 N:%d" % osd['perf_stats']['apply_latency_ms']
	print "PUTVAL \"" + fqdn + "/ceph/latency-commit-max\" interval=10 N:%d" % osd['perf_stats']['commit_latency_ms']
	sleep(10)
