# == Class: ceph_collectd
#
# This class configures a collectd-plugin to gather various Statistics about
# a Ceph cluster.
#
# === Parameter
#
# [*user*]
#  User to run the collectd-plugin script, this user must have access to the
#  ceph.conf and keyring files.
#
# === Examples
#
#  class { 'ceph_collectd':
#    user => 'nagios'
#  }
#
# === Authors
#
# Micha Krause <micha@noris.net>
#
# === Copyright
#
# Copyright 2015 Micha Krause, unless otherwise noted.
#
class ceph_collectd ($user,$group) {
  include ceph_collectd::install
  include ceph_collectd::config
}
