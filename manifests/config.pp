# == Class: ceph_collectd::config
#
# This class handles configuration of the ceph_collectd plugin.
#
# === Authors
#
# Micha Krause <micha@noris.net>
#
# === Copyright
#
# Copyright 2015 Micha Krause, unless otherwise noted.
#
class ceph_collectd::config {
  collectd::plugin::exec { 'ceph':
    exec  => ['/usr/local/bin/ceph_collect.py'],
    user  => $::ceph_collectd::user,
    group => $::ceph_collectd::group,
  }
}
