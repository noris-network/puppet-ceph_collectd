#!/usr/bin/python -u

import pprint
from time import sleep
from socket import getfqdn
from json import loads
from commands import getoutput
import string
from re import sub

fqdn=getfqdn()

pp = pprint.PrettyPrinter(indent=4)

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
	osd_df = loads(getoutput('ceph osd df --format=json 2>/dev/null | sed "s/-nan/0/g"'))
	po_data = loads(sub(r'-inf','0',getoutput('ceph osd pool stats --format=json 2>/dev/null')))
	state_stats = get_pg_states(pg_data['pg_stats'])
	totaliops=un2zero(st_data['pgmap'],'write_op_per_sec')+un2zero(st_data['pgmap'],'read_op_per_sec')
	degraded=un2zero(st_data['pgmap'],'degraded_objects')
	missplaced=un2zero(st_data['pgmap'],'misplaced_objects')
	osdmap=st_data['osdmap']['osdmap']

	pools={}

	for pg in pg_data['pg_stats']:
		pgid=pg['pgid']
		pool=int(pgid.split(".")[0])
		if pools.has_key(pool):
			pools[pool] += 1
		else:
			pools[pool] = 1
		if "backfilling" in pg['state']:
			for osd in pg['up']:
				if osd not in pg['acting']:
					print "PUTVAL \"" + fqdn + "/ceph/gauge-osd_" + str(osd) + "_backfill\" interval=10 N:%d" % osd
		if "deep" in pg['state']:
			for osd in pg['acting']:
				print "PUTVAL \"" + fqdn + "/ceph/gauge-osd_" + str(osd) + "_deepscrubs\" interval=10 N:%d" % osd
		elif "scrubbing" in pg['state']:
                        for osd in pg['acting']:
				print "PUTVAL \"" + fqdn + "/ceph/gauge-osd_" + str(osd) + "_scrubs\" interval=10 N:%d" % osd

	for pool in po_data:
		iops=un2zero(pool['client_io_rate'],'read_op_per_sec') + un2zero(pool['client_io_rate'],'write_op_per_sec')
		bw=un2zero(pool['client_io_rate'],'read_bytes_sec') + un2zero(pool['client_io_rate'],'write_bytes_sec')
		print "PUTVAL \"" + fqdn + "/ceph/gauge-pool_" + pool['pool_name'].replace(".","_") + "_iops\" interval=10 N:%d" % iops
		print "PUTVAL \"" + fqdn + "/ceph/gauge-pool_" + pool['pool_name'].replace(".","_") + "_bw\" interval=10 N:%d" % bw
		print "PUTVAL \"" + fqdn + "/ceph/gauge-pool_" + pool['pool_name'].replace(".","_") + "_pgs\" interval=10 N:%d" % pools[pool['pool_id']]

	for pool in df_data['pools']:
		print "PUTVAL \"" + fqdn + "/ceph/gauge-pool_" + pool['name'].replace(".","_") + "_objects\" interval=10 N:%d" % un2zero(pool['stats'],'objects')
		print "PUTVAL \"" + fqdn + "/ceph/df-pool_" + pool['name'].replace(".","_") + "\" interval=10 N:%d:%d" % (un2zero(pool['stats'],'bytes_used'),df_data['stats']['total_avail_bytes']/3)

	print "PUTVAL \"" + fqdn + "/ceph/gauge-osds_total\" interval=10 N:%d" % osdmap['num_osds']
	print "PUTVAL \"" + fqdn + "/ceph/gauge-osds_in\" interval=10 N:%d" % osdmap['num_in_osds']
	print "PUTVAL \"" + fqdn + "/ceph/gauge-osds_up\" interval=10 N:%d" % osdmap['num_up_osds']
	print "PUTVAL \"" + fqdn + "/ceph/df-total\" interval=10 N:%d:%d" % (df_data['stats']['total_used_bytes'],df_data['stats']['total_avail_bytes'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-total_objects\" interval=10 N:%d" % df_data['stats']['total_objects']
	print "PUTVAL \"" + fqdn + "/ceph/gauge-degraded_objects\" interval=10 N:%d" % degraded
	print "PUTVAL \"" + fqdn + "/ceph/gauge-missplaced_objects\" interval=10 N:%d" % missplaced
	print "PUTVAL \"" + fqdn + "/ceph/gauge-total_pgs\" interval=10 N:%d" % len(pg_data['pg_stats'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-backfilling_pgs\" interval=10 N:%d" % int(state_stats['wait_backfill'] + state_stats['backfilling'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-recovering_pgs\" interval=10 N:%d" % int(state_stats['recovery_wait'] + state_stats['recovering'])
	print "PUTVAL \"" + fqdn + "/ceph/gauge-total_iops\" interval=10 N:%d" % totaliops
	print "PUTVAL \"" + fqdn + "/ceph/bytes-recovery_bps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'recovering_bytes_per_sec')
	print "PUTVAL \"" + fqdn + "/ceph/bytes-rps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'read_bytes_sec')
	print "PUTVAL \"" + fqdn + "/ceph/bytes-wps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'write_bytes_sec')
	print "PUTVAL \"" + fqdn + "/ceph/gauge-recovery_objps\" interval=10 N:%d" % un2zero(st_data['pgmap'],'recovering_objects_per_sec')
	disks=[]
	for disk in osd_df['nodes']:
		disks.append(disk['utilization'])
	disks.sort()
	print "PUTVAL \"" + fqdn + "/ceph/gauge-osd_df\" interval=10 N:%d" % int(disks[-1]*1000)

	sleep(4)
