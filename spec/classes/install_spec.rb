require 'spec_helper'
describe 'ceph_collectd::install' do

  context 'with defaults for all parameters' do
    it { should contain_file('/usr/local/bin/ceph_collect.py') }
  end
end
