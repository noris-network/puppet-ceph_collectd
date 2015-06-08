# ceph_collectd

#### Table of Contents

1. [Overview](#overview)
2. [Module Description - What the module does and why it is useful](#module-description)
3. [Setup - The basics of getting started with ceph_collectd](#setup)
    * [What ceph_collectd affects](#what-ceph_collectd-affects)
    * [Setup requirements](#setup-requirements)
    * [Beginning with ceph_collectd](#beginning-with-ceph_collectd)
4. [Usage - Configuration options and additional functionality](#usage)
5. [Reference - An under-the-hood peek at what the module is doing and how](#reference)
5. [Limitations - OS compatibility, etc.](#limitations)
6. [Development - Guide for contributing to the module](#development)

## Overview

This module installes a collectd plugin to collect statistics about ceph.

## Setup

### What ceph_collectd affects

The module will install a python script to /usr/local/sbin, which collects
data from a ceph cluster.
This script is run by collectd, the pdxcat/collectd module is used to
configure this in collectd.

### Setup Requirements

The pdxcat/collectd module should be initialized.

### Beginning with ceph_collectd

```puppet
include collectd

class {'ceph_collectd':
  user  => 'nagios'
  group => 'nagios'
}
```

### Parameters

* user: the collectd plugin has to run as a non privileged user on your system, you can choose this user here.
* group: see user
