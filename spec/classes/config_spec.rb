require 'spec_helper'
describe 'ceph_collectd::config' do

  let (:facts) {{ :osfamily => 'Debian' }}
  let(:pre_condition) {'class { "ceph_collectd": user => "nagios", group => "nagios" }' }

  context 'with defaults for all parameters' do
    it { should contain_collectd__plugin__exec('ceph').with( {'user' => 'nagios', 'group' => 'nagios' } ) }
  end
end
