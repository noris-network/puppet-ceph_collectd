# == Class: ceph_collectd::install
#
# This class handles installation of the ceph_collectd plugin.
#
# === Authors
#
# Micha Krause <micha@noris.net>
#
# === Copyright
#
# Copyright 2015 Micha Krause, unless otherwise noted.
#
class ceph_collectd::install {
  file { '/usr/local/bin/ceph_collect.py':
    ensure  => file,
    mode    => '0755',
    source  => "puppet:///modules/${module_name}/ceph_collect.py",
  }
}
