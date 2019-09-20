#!/usr/bin/env bash
# Pre-Requirements
yum -y install centos-release-openstack-queens
yum --enablerepo=centos-openstack-queens -y install mariadb-server
systemctl enable mariadb
systemctl start mariadb
yum --enablerepo=epel -y install rabbitmq-server memcached
systemctl start rabbitmq-server memcached
systemctl enable rabbitmq-server memcached
rabbitmqctl add_user openstack password
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
__________________________________________________________________________________________________

################ Configure Keystone#1

mysql -uroot -p123456 -e "create database keystone;"
mysql -uroot -p123456 -e "grant all privileges on keystone.* to keystone@'localhost' identified by 'password';"
mysql -uroot -p123456 -e "grant all privileges on keystone.* to keystone@'%' identified by 'password';"
mysql -uroot -p123456 -e "flush privileges;"
yum --enablerepo=centos-openstack-queens,epel -y install openstack-keystone openstack-utils python-openstackclient httpd mod_wsgi

vi /etc/keystone/keystone.conf

#memcache_servers = localhost:11211 >> memcache_servers = 192.168.100.10:11211
#connection = <None> >> connection = mysql+pymysql://keystone:password@192.168.100.10/keystone
#provider = fernet >> provider = fernet
su -s /bin/bash keystone -c "keystone-manage db_sync"
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone

export controller=192.168.100.10

keystone-manage bootstrap --bootstrap-password adminpassword \
--bootstrap-admin-url http://$controller:5000/v3/ \
--bootstrap-internal-url http://$controller:5000/v3/ \
--bootstrap-public-url http://$controller:5000/v3/ \
--bootstrap-region-id RegionOne

ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
systemctl enable httpd
systemctl start httpd
---------------------------------------------------------------------------------------

#Configure Keystone#2

cat > "keystonerc" <<END
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=adminpassword
export OS_AUTH_URL=http://192.168.100.10:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export PS1='[\u@\h \W(keystone)]\$ '
END

chmod 600 ~/keystonerc

source ~/keystonerc

openstack project create --domain default --description "Service Project" service
openstack project list

----------------------------------------------------------------------------------------------

#Configure Glance

openstack user create --domain default --project service --password servicepassword glance
openstack role add --project service --user glance admin
openstack service create --name glance --description "OpenStack Image service" image
export controller=192.168.100.10
openstack endpoint create --region RegionOne image public http://$controller:9292
openstack endpoint create --region RegionOne image internal http://$controller:9292
openstack endpoint create --region RegionOne image admin http://$controller:9292

mysql -uroot -p123456 -e "create database glance;"
mysql -uroot -p123456 -e "grant all privileges on glance.* to glance@'localhost' identified by 'password';"
mysql -uroot -p123456 -e "grant all privileges on glance.* to glance@'%' identified by 'password';"
mysql -uroot -p123456 -e "flush privileges;"

yum --enablerepo=centos-openstack-queens,epel -y install openstack-glance


vi /etc/glance/glance-api.conf
cat > "/etc/glance/glance-api.conf" <<END
# create new
[DEFAULT]
bind_host = 0.0.0.0

[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/

[database]
# MariaDB connection info
connection = mysql+pymysql://glance:password@192.168.100.10/glance

# keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://192.168.100.10:5000/v3
auth_url = http://192.168.100.10:5000/v3
memcached_servers = 192.168.100.10:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = servicepassword

[paste_deploy]
flavor = keystone
END

vi /etc/glance/glance-registry.conf

cat > "/etc/glance/glance-registry.conf" <<END
# create new
[DEFAULT]
bind_host = 0.0.0.0

[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/

[database]
# MariaDB connection info
connection = mysql+pymysql://glance:password@192.168.100.10/glance

# keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://192.168.100.10:5000/v3
auth_url = http://192.168.100.10:5000/v3
memcached_servers = 192.168.100.10:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = servicepassword

[paste_deploy]
flavor = keystone
END

chmod 640 /etc/glance/glance-api.conf /etc/glance/glance-registry.conf
chown root:glance /etc/glance/glance-api.conf /etc/glance/glance-registry.conf
su -s /bin/bash glance -c "glance-manage db_sync"
systemctl start openstack-glance-api openstack-glance-registry
systemctl enable openstack-glance-api openstack-glance-registry

----------------------------------------------------------------------------------------
####Configure Nova#1
openstack user create --domain default --project service --password servicepassword nova
openstack role add --project service --user nova admin
openstack user create --domain default --project service --password servicepassword placement
openstack role add --project service --user placement admin
openstack service create --name nova --description "OpenStack Compute service" compute
openstack service create --name placement --description "OpenStack Compute Placement service" placement

export controller=192.168.100.10
openstack endpoint create --region RegionOne compute public http://$controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute internal http://$controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne compute admin http://$controller:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region RegionOne placement public http://$controller:8778
openstack endpoint create --region RegionOne placement internal http://$controller:8778
openstack endpoint create --region RegionOne placement admin http://$controller:8778


mysql -u root -p123456 -e "create database nova;"
mysql -u root -p123456 -e "grant all privileges on nova.* to nova@'localhost' identified by 'password';"
mysql -u root -p123456 -e "grant all privileges on nova.* to nova@'%' identified by 'password';"
mysql -u root -p123456 -e "create database nova_api;"
mysql -u root -p123456 -e "grant all privileges on nova_api.* to nova@'localhost' identified by 'password';"
mysql -u root -p123456 -e "grant all privileges on nova_api.* to nova@'%' identified by 'password';"
mysql -u root -p123456 -e "create database nova_placement;"
mysql -u root -p123456 -e "grant all privileges on nova_placement.* to nova@'localhost' identified by 'password';"
mysql -u root -p123456 -e "grant all privileges on nova_placement.* to nova@'%' identified by 'password';"
mysql -u root -p123456 -e "create database nova_cell0;"
mysql -u root -p123456 -e "grant all privileges on nova_cell0.* to nova@'localhost' identified by 'password';"
mysql -u root -p123456 -e "grant all privileges on nova_cell0.* to nova@'%' identified by 'password';"
mysql -u root -p123456 -e "flush privileges;"
-----------------------------------------------------------------------------------------------

#########Configure Nova#2
yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova

vi /etc/nova/nova.conf
cat > "/etc/nova/nova.conf" << END
# create new
[DEFAULT]
# define own IP
my_ip = 192.168.100.10
state_path = /var/lib/nova
enabled_apis = osapi_compute,metadata
log_dir = /var/log/nova
# RabbitMQ connection info
transport_url = rabbit://openstack:password@192.168.100.10

[api]
auth_strategy = keystone

# Glance connection info
[glance]
api_servers = http://192.168.100.10:9292/v3

[oslo_concurrency]
lock_path = $state_path/tmp

# MariaDB connection info
[api_database]
connection = mysql+pymysql://nova:password@192.168.100.10/nova_api

[database]
connection = mysql+pymysql://nova:password@192.168.100.10/nova

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://192.168.100.10:5000/v3
auth_url = http://192.168.100.10:5000/v3
memcached_servers = 192.168.100.10:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = servicepassword

[placement]
auth_url = http://192.168.100.10:5000/v3
os_region_name = RegionOne
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = placement
password = servicepassword

[placement_database]
connection = mysql+pymysql://nova:password@192.168.100.10/nova_placement

[wsgi]
api_paste_config = /etc/nova/api-paste.ini

# LIBVIRT
[libvirt]
virt_type=qemu


END

chgrp nova /etc/nova/nova.conf
chmod 640 /etc/nova/nova.conf

vi /etc/httpd/conf.d/00-nova-placement-api.conf
# add near line 15
  <Directory /usr/bin>
    Require all granted
  </Directory>

su -s /bin/bash nova -c "nova-manage api_db sync"
su -s /bin/bash nova -c "nova-manage cell_v2 map_cell0"
su -s /bin/bash nova -c "nova-manage db sync"
su -s /bin/bash nova -c "nova-manage cell_v2 create_cell --name cell1"

systemctl restart httpd
chown nova. /var/log/nova/nova-placement-api.log

for service in api consoleauth conductor scheduler novncproxy; do
systemctl start openstack-nova-$service
systemctl enable openstack-nova-$service
done

openstack compute service list

############################################# nova ALL IN ONE################################################

yum -y install qemu-kvm libvirt virt-install
systemctl start libvirtd
systemctl enable libvirtd

yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova-compute

vi /etc/nova/nova.conf

# add follows (enable VNC)
cat >> /etc/nova/nova.conf << END


[vnc]
enabled = True
server_listen = 0.0.0.0
server_proxyclient_address = 192.168.100.10
novncproxy_base_url = http://192.168.100.10:6080/vnc_auto.html
END

systemctl start openstack-nova-compute
systemctl enable openstack-nova-compute

su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"
openstack compute service list

---------------------------------------------------------------------------------

##############Configure Neutron#1
openstack user create --domain default --project service --password servicepassword neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking service" network
export controller=192.168.100.10
openstack endpoint create --region RegionOne network public http://$controller:9696
openstack endpoint create --region RegionOne network internal http://$controller:9696
openstack endpoint create --region RegionOne network admin http://$controller:9696

mysql -u root -p123456 -e "create database neutron_ml2;"
mysql -u root -p123456 -e "grant all privileges on neutron_ml2.* to neutron@'localhost' identified by 'password';"
mysql -u root -p123456 -e "grant all privileges on neutron_ml2.* to neutron@'%' identified by 'password';"
mysql -u root -p123456 -e "flush privileges;"

############################################## neutron ALL IN ONE ######################################
yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch

vi /etc/neutron/neutron.conf
cat > "/etc/neutron/neutron.conf" << END
# create new
[DEFAULT]
core_plugin = ml2
service_plugins = router
auth_strategy = keystone
state_path = /var/lib/neutron
dhcp_agent_notification = True
allow_overlapping_ips = True
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
# RabbitMQ connection info
transport_url = rabbit://openstack:password@192.168.100.10

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://192.168.100.10:5000/v3
auth_url = http://192.168.100.10:5000/v3
memcached_servers = 192.168.100.10:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = servicepassword

# MariaDB connection info
[database]
connection = mysql+pymysql://neutron:password@192.168.100.10/neutron_ml2

# Nova connection info
[nova]
auth_url = http://192.168.100.10:5000/v3
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = servicepassword

[oslo_concurrency]
lock_path = $state_path/tmp

END

chmod 640 /etc/neutron/neutron.conf
chgrp neutron /etc/neutron/neutron.conf

vi /etc/neutron/l3_agent.ini
#interface_driver = <None> >> interface_driver = openvswitch

vi /etc/neutron/dhcp_agent.ini
#interface_driver = <None> >> interface_driver = openvswitch
#dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq >> dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
#enable_isolated_metadata = fale >> enable_isolated_metadata = true

vi /etc/neutron/metadata_agent.ini
#nova_metadata_host = 127.0.0.1 >> nova_metadata_host = 192.168.100.10
#metadata_proxy_shared_secret = >> metadata_secret
#memcache_servers = localhost:11211 >> memcache_servers = 192.168.100.10:11211

vi /etc/neutron/plugins/ml2/ml2_conf.ini
#type_drivers = local,flat,vlan,gre,vxlan,geneveb >> type_drivers = local,flat,vlan,gre,vxlan,geneve
#tenant_network_types = local >> tenant_network_types = vxlan
#mechanism_drivers = >> mechanism_drivers = openvswitch,l2population
#extension_drivers = >> extension_drivers = port_security


vi /etc/neutron/plugins/ml2/openvswitch_agent.ini
#firewall_driver = <None> >> firewall_driver = openvswitch
#enable_security_group = true >> enable_security_group = true
#enable_ipset = true >> enable_ipset = true


vi /etc/nova/nova.conf
# add follows into [DEFAULT] section
use_neutron = True
linuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver
firewall_driver = nova.virt.firewall.NoopFirewallDriver
vif_plugging_is_fatal = True
vif_plugging_timeout = 300

# add follows to the end : Neutron auth info
# the value of metadata_proxy_shared_secret is the same with the one in metadata_agent.ini
[neutron]
auth_url = http://192.168.100.10:5000/v3
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = servicepassword
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata_secret

systemctl start openvswitch
systemctl enable openvswitch
ovs-vsctl add-br br-int

ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"

for service in server dhcp-agent l3-agent metadata-agent openvswitch-agent; do
systemctl start neutron-$service
systemctl enable neutron-$service
done

systemctl restart openstack-nova-api openstack-nova-compute
openstack network agent list

------------------------------------------------------------------------------------
#####Configure Networking(FLAT)

ovs-vsctl add-br br-ens37
ovs-vsctl add-port br-ens37 ens37

vi /etc/neutron/plugins/ml2/ml2_conf.ini
#flat_networks = * >> flat_networks = physnet1

vi /etc/neutron/plugins/ml2/openvswitch_agent.ini
#bridge_mappings = >> bridge_mappings = physnet1:br-ens37

systemctl restart neutron-openvswitch-agent

-----------------------------------------------------------------------------------------
###########Configure Horizon

yum --enablerepo=centos-openstack-queens,epel -y install openstack-dashboard

vi /etc/openstack-dashboard/local_settings

ALLOWED_HOSTS = ['horizon.example.com', 'localhost'] >> ALLOWED_HOSTS = ['192.168.100.10', 'localhost']

# line 64: uncomment like follows
OPENSTACK_API_VERSIONS = {
#    "data-processing": 1.1,
    "identity": 3,
    "volume": 2,
    "compute": 2,
}

#OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = False >> OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
#OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default' >> OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

# line 167,168: change and add Memcache server
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '192.168.100.10:11211',
    },
}

# line 189: change OPENSTACK_HOST to your own one
OPENSTACK_HOST = "192.168.100.10"
OPENSTACK_KEYSTONE_URL = "http://%s:5000/v3" % OPENSTACK_HOST
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "admin"

 vi /etc/httpd/conf.d/openstack-dashboard.conf
 # near line 4: add
 WSGIApplicationGroup %{GLOBAL}

 systemctl restart httpd


 ######## BO QUA Configure Neutron#3 (Control Node) NEU control, network cung host
 ######## BO QUA   Configure Neutron#4 (Network Node)  NEU control, network cung host
  ######## BO QUA Configure Neutron#5 (Compute Node) NEU control, network,compute cung host

--------------------------------------- Neutron Network (VXLAN)


########	Change settings on Control Node.
vi /etc/neutron/plugins/ml2/ml2_conf.ini

#vni_ranges =  >> vni_ranges = 1:1000

systemctl restart neutron-server

############## 	Change settings on Network Node.

 ovs-vsctl add-br br-eth1
 ovs-vsctl add-port br-eth1 eth1

vi /etc/neutron/plugins/ml2/ml2_conf.ini
# line 235: add
[ml2_type_vxlan]
vni_ranges = 1:1000


vi /etc/neutron/plugins/ml2/openvswitch_agent.ini
#tunnel_types = >> tunnel_types = vxlan
#l2_population = false >> l2_population = True
prevent_arp_spoofing = True
#local_ip = <None> >> local_ip = 192.168.100.10
#bridge_mappings = >> bridge_mappings = physnet1:br-ens37

for service in dhcp-agent l3-agent metadata-agent openvswitch-agent; do
systemctl restart neutron-$service
done

###############	Change settings on Compute Node.

vi /etc/neutron/plugins/ml2/openvswitch_agent.ini
#tunnel_types = >> tunnel_types = vxlan
#l2_population = false >> l2_population = True
prevent_arp_spoofing = True
#local_ip = <None> >> local_ip = 192.168.100.10


openstack router create router01
openstack network create internal --provider-network-type vxlan

openstack subnet create sub-inter --network internal \
> --subnet-range 10.0.0.0/24 --gateway 10.0.0.1 \
> --dns-nameserver 8.8.8.8

openstack router add subnet router01 sub-inter
openstack network create \
> --provider-physical-network physnet1 \
> --provider-network-type flat --external external
openstack subnet create sub-inter --network external --subnet-range 192.168.1.0/24 --allocation-pool start=192.168.1.200,end=192.168.1.230 --gateway 192.168.1.1 --dns-nameserver 8.8.8.8 --no-dhcp
openstack router set router01 --external-gateway external

openstack network list
openstack project list

netID=$(openstack network list | grep internal | awk '{ print $2 }')
prjID=$(openstack project list | grep admin | awk '{ print $2 }')
openstack network rbac create --target-project $prjID --type network --action access_as_shared $netID

































































