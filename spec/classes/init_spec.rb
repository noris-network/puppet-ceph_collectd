require 'spec_helper'
describe 'ceph_collectd' do

  let (:params) {{ :user => 'nagios', :group => 'nagios' }}
  let (:facts)  {{ :osfamily => 'debian' }}

  context 'with defaults for all parameters' do
    it { should contain_class('ceph_collectd') }
    it { should contain_class('ceph_collectd::install') }
    it { should contain_class('ceph_collectd::config') }
  end
end
