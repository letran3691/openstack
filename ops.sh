#!/usr/bin/bash


printf "======================================Create key ssh======================================\n"
sleep 2
ssh-keygen -q -t rsa -f ~/.ssh/id_rsa -N ''

systemctl stop firewalld && systemctl disable firewalld
systemctl stop NetworkManager && systemctl disable NetworkManager
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config


requirements(){
printf "======================================install packet requirements=============================\n"
sleep 3
# Pre-Requirements
yum -y install centos-release-openstack-queens epel-release
curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash
yum -y install MariaDB-server
systemctl enable mariadb
systemctl start mariadb
mysql_secure_installation <<EOF

y
$rootsql
$rootsql
y
y
y
y
EOF
printf "======================================install rabbitmq memcached==============================\n"
sleep 2
yum --enablerepo=epel -y install rabbitmq-server memcached
systemctl start rabbitmq-server memcached
systemctl enable rabbitmq-server memcached
rabbitmqctl add_user openstack $pass_rabbitmq
rabbitmqctl set_permissions openstack ".*" ".*" ".*"
}
keytone (){

printf "======================================Identity keytone=========================================\n"
sleep 2
################ Configure Keystone#1

mysql -uroot -p123456 -e "create database keystone;"
mysql -uroot -p123456 -e "grant all privileges on keystone.* to keystone@'localhost' identified by '"$pass_user_sql"';"
mysql -uroot -p123456 -e "grant all privileges on keystone.* to keystone@'%' identified by '"$pass_user_sql"';"
mysql -uroot -p123456 -e "flush privileges;"

yum --enablerepo=centos-openstack-queens,epel -y install openstack-keystone openstack-utils python-openstackclient httpd mod_wsgi

#vi /etc/keystone/keystone.conf
token_conf='/etc/keystone/keystone.conf'
sed -i "s/\#memcache_servers = localhost:11211/memcache_servers = $controller:11211/g" $token_conf
sed -i "s/\#connection = <None>/connection = mysql+pymysql:\/\/keystone:$pass_user_sql@$controller\/keystone/g" $token_conf
sed -i "s/\#provider = fernet/provider = fernet/g"  $token_conf
su -s /bin/bash keystone -c "keystone-manage db_sync"
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone


keystone-manage bootstrap --bootstrap-password $pass_admin \
--bootstrap-admin-url http://$controller:5000/v3/ \
--bootstrap-internal-url http://$controller:5000/v3/ \
--bootstrap-public-url http://$controller:5000/v3/ \
--bootstrap-region-id RegionOne

ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/
systemctl enable httpd
systemctl start httpd


#Configure Keystone#2

cat > "keystonerc" <<END
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=$pass_admin
export OS_AUTH_URL=http://$controller:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export PS1='[\u@\h \W(keystone)]\$ '
END

chmod 600 ~/keystonerc

source ~/keystonerc

source keystonerc && openstack project create --domain default --description "Service Project" service
source keystonerc && openstack project list
}

glance (){

printf "======================================config image service (glance)============================\n"
sleep 2
#Configure Glance

source keystonerc && openstack user create --domain default --project service --password $pass_project_user glance
source keystonerc && openstack role add --project service --user glance admin
source keystonerc && openstack service create --name glance --description "OpenStack Image service" image

source keystonerc && openstack endpoint create --region RegionOne image public http://$controller:9292
source keystonerc && openstack endpoint create --region RegionOne image internal http://$controller:9292
source keystonerc && openstack endpoint create --region RegionOne image admin http://$controller:9292

mysql -uroot -p123456 -e "create database glance;"
mysql -uroot -p123456 -e "grant all privileges on glance.* to glance@'localhost' identified by '"$pass_user_sql"';"
mysql -uroot -p123456 -e "grant all privileges on glance.* to glance@'%' identified by '"$pass_user_sql"';"
mysql -uroot -p123456 -e "flush privileges;"

printf "======================================Install glance=============================================\n"
sleep 2
yum --enablerepo=centos-openstack-queens,epel -y install openstack-glance


#vi /etc/glance/glance-api.conf
cat > "/etc/glance/glance-api.conf" <<END
# create new
[DEFAULT]
bind_host = 0.0.0.0

[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
debug = true


[database]
# MariaDB connection info
connection = mysql+pymysql://glance:$pass_user_sql@$controller/glance

# keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://$controller:5000
auth_url = http://$controller:5000
memcached_servers = $controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = $pass_project_user

[paste_deploy]
flavor = keystone


END

#vi /etc/glance/glance-registry.conf

cat > "/etc/glance/glance-registry.conf" <<END
# create new
[DEFAULT]
bind_host = 0.0.0.0

[glance_store]
stores = file,http
default_store = file
filesystem_store_datadir = /var/lib/glance/images/
debug = true

[database]
# MariaDB connection info
connection = mysql+pymysql://glance:$pass_user_sql@$controller/glance

# keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://$controller:5000
auth_url = http://$controller:5000
memcached_servers = $controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = glance
password = $pass_project_user

[paste_deploy]
flavor = keystone

END

chmod 640 /etc/glance/glance-api.conf /etc/glance/glance-registry.conf
chown root:glance /etc/glance/glance-api.conf /etc/glance/glance-registry.conf
su -s /bin/bash glance -c "glance-manage db_sync"
systemctl start openstack-glance-api openstack-glance-registry
systemctl enable openstack-glance-api openstack-glance-registry

}
nova_Keystone (){
printf "======================================nova_service keytone==============================================\n"
sleep 2

####Configure Nova#1
source keystonerc && openstack user create --domain default --project service --password $pass_project_user nova
source keystonerc && openstack role add --project service --user nova admin
source keystonerc && openstack user create --domain default --project service --password $pass_project_user placement
source keystonerc && openstack role add --project service --user placement admin
source keystonerc && openstack service create --name nova --description "OpenStack Compute service" compute
source keystonerc && openstack service create --name placement --description "OpenStack Compute Placement service" placement

source keystonerc && openstack endpoint create --region RegionOne compute public http://$controller:8774/v2.1/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne compute internal http://$controller:8774/v2.1/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne compute admin http://$controller:8774/v2.1/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne placement public http://$controller:8778
source keystonerc && openstack endpoint create --region RegionOne placement internal http://$controller:8778
source keystonerc && openstack endpoint create --region RegionOne placement admin http://$controller:8778


mysql -u root -p123456 -e "create database nova;"
mysql -u root -p123456 -e "grant all privileges on nova.* to nova@'localhost' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "grant all privileges on nova.* to nova@'%' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "create database nova_api;"
mysql -u root -p123456 -e "grant all privileges on nova_api.* to nova@'localhost' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "grant all privileges on nova_api.* to nova@'%' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "create database nova_placement;"
mysql -u root -p123456 -e "grant all privileges on nova_placement.* to nova@'localhost' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "grant all privileges on nova_placement.* to nova@'%' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "create database nova_cell0;"
mysql -u root -p123456 -e "grant all privileges on nova_cell0.* to nova@'localhost' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "grant all privileges on nova_cell0.* to nova@'%' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "flush privileges;"

}

nova_install_conf(){
printf "======================================Install Nova services========================================\n"
sleep 2

yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova

cat > "/etc/nova/nova.conf" << END
# create new
[DEFAULT]
# define own IP
my_ip = $controller
state_path = /var/lib/nova
enabled_apis = osapi_compute,metadata
log_dir = /var/log/nova
# RabbitMQ connection info
transport_url = rabbit://openstack:$pass_rabbitmq@$controller
debug = true

#neutron


[api]
auth_strategy = keystone

# Glance connection info
[glance]
api_servers = http://$controller:9292

[oslo_concurrency]
lock_path = \$state_path/tmp

# MariaDB connection info
[api_database]
connection = mysql+pymysql://nova:$pass_user_sql@$controller/nova_api

[database]
connection = mysql+pymysql://nova:$pass_user_sql@$controller/nova

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://$controller:5000
auth_url = http://$controller:5000
memcached_servers = $controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = nova
password = $pass_project_user

[placement]
auth_url = http://$controller:5000
os_region_name = RegionOne
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = placement
password = $pass_project_user

[placement_database]
connection = mysql+pymysql://nova:$pass_user_sql@$controller/nova_placement

[wsgi]
api_paste_config = /etc/nova/api-paste.ini

# LIBVIRT
[libvirt]
virt_type=qemu


END

chgrp nova /etc/nova/nova.conf
chmod 640 /etc/nova/nova.conf

cp -f /root/openstack/controller/00-nova-placement-api.conf /etc/httpd/conf.d/

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

}
############################################# nova ALL IN ONE################################################
nova_compute(){

printf "======================================Install libvirt and nova-compute===========================\n"
sleep 2


yum -y install qemu-kvm libvirt virt-install
systemctl start libvirtd
systemctl enable libvirtd

yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova-compute

cat >> /etc/nova/nova.conf << END


[vnc]
enabled = True
server_listen = 0.0.0.0
server_proxyclient_address = $controller
novncproxy_base_url = http://$controller:6080/vnc_auto.html


END

printf "============================restart and enable nova-compute=====================================\n "
sleep 2
systemctl start openstack-nova-compute
systemctl enable openstack-nova-compute

su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"
openstack compute service list
}

neutron_Keystone(){
printf "======================================neutron_Keystone======================================\n"
sleep 2

source keystonerc && openstack user create --domain default --project service --password $pass_project_user neutron
source keystonerc && openstack role add --project service --user neutron admin
source keystonerc && openstack service create --name neutron --description "OpenStack Networking service" network
source keystonerc && openstack endpoint create --region RegionOne network public http://$controller:9696
source keystonerc && openstack endpoint create --region RegionOne network internal http://$controller:9696
source keystonerc && openstack endpoint create --region RegionOne network admin http://$controller:9696

mysql -u root -p123456 -e "create database neutron_ml2;"
mysql -u root -p123456 -e "grant all privileges on neutron_ml2.* to neutron@'localhost' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "grant all privileges on neutron_ml2.* to neutron@'%' identified by '"$pass_user_sql"';"
mysql -u root -p123456 -e "flush privileges;"

}
############################################## neutron ALL IN ONE ######################################
neutron_server_all(){
printf "======================================Install neutron server======================================\n"
sleep 2
yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch

#vi /etc/neutron/neutron.conf
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
transport_url = rabbit://openstack:$pass_rabbitmq@$controller
debug = true

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://$controller:5000
auth_url = http://$controller:5000
memcached_servers = $controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = $pass_project_user

# MariaDB connection info
[database]
connection = mysql+pymysql://neutron:$pass_user_sql@$controller/neutron_ml2

# Nova connection info
[nova]
auth_url = http://$controller:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = $pass_project_user

[oslo_concurrency]
lock_path = \$state_path/tmp

END

chmod 640 /etc/neutron/neutron.conf
chgrp neutron /etc/neutron/neutron.conf

    l3_ini='/etc/neutron/l3_agent.ini'
sed -i "s/\#interface_driver = <None>/interface_driver = openvswitch/g" $l3_ini

dhcp_ini='/etc/neutron/dhcp_agent.ini'
sed -i "s/\#interface_driver = <None>/interface_driver = openvswitch/g" $dhcp_ini
sed -i "s/\#dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq/dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq\n\nenable_isolated_metadata = true/g" $dhcp_ini

metadata_ini='/etc/neutron/metadata_agent.ini'
sed -i "s/\#nova_metadata_host = 127.0.0.1/nova_metadata_host = $controller/g" $metadata_ini
sed -i "s/\#metadata_proxy_shared_secret =/metadata_proxy_shared_secret = metadata_secret/g" $metadata_ini
sed -i "s/\#memcache_servers = localhost:11211/memcache_servers = $controller:11211/g" $metadata_ini

ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
sed -i "s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g" $ml2_ini
sed -i "s/\#tenant_network_types = local/tenant_network_types = vxlan/g" $ml2_ini
sed -i "s/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g" $ml2_ini
sed -i "s/\#extension_drivers =/extension_drivers = port_security/g" $ml2_ini


openvswitch_ini='/etc/neutron/plugins/ml2/openvswitch_agent.ini'
sed -i "s/\#firewall_driver = <None>/firewall_driver = openvswitch/g" $openvswitch_ini
sed -i "s/\#enable_security_group = true/enable_security_group = true/g" $openvswitch_ini
sed -i "s/\#enable_ipset = true/enable_ipset = true/g" $openvswitch_ini

con_nova_conf='/etc/nova/nova.conf'
sed -i "s/\#neutron/use_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver\nvif_plugging_is_fatal = True\nvif_plugging_timeout = 300/g" $con_nova_conf

cat >> "/etc/nova/nova.conf" << END
[neutron]
auth_url = http://$controller:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = $pass_project_user
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata_secret


END

systemctl start openvswitch
systemctl enable openvswitch
ovs-vsctl add-br br-int

ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"

printf "================================restart neutron service================================\n "

for service in server dhcp-agent l3-agent metadata-agent openvswitch-agent; do
systemctl start neutron-$service
systemctl enable neutron-$service
done

printf "================================restart nova service================================"
sleep 2
#systemctl restart neutron-server neutron-metadata-agent
#systemctl enable neutron-server neutron-metadata-agent
systemctl restart openstack-nova-api
systemctl restart openstack-nova-compute
source keystonerc && openstack network agent list

source keystonerc &&openstack security group rule create --protocol icmp --ingress default
source keystonerc &&openstack security group rule create --protocol tcp --dst-port 22:22 default

}

neutron_server_control(){
printf "=================================Install neutron server controller=======================\n"
sleep 2

yum -y install centos-release-openstack-queens epel-release
sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo
yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2

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
transport_url = rabbit://openstack:$pass_rabbitmq@$controller
debug = true

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://$controller:5000
auth_url = http://$controller:5000
memcached_servers = $controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = $pass_project_user

# MariaDB connection info
[database]
connection = mysql+pymysql://neutron:$pass_user_sql@$controller/neutron_ml2

# Nova connection info
[nova]
auth_url = http://$controller:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = $pass_project_user

[oslo_concurrency]
lock_path = \$state_path/tmp

END

chmod 640 /etc/neutron/neutron.conf  && chgrp neutron /etc/neutron/neutron.conf

metadata_ini_con='/etc/neutron/metadata_agent.ini'
sed -i "s/\#nova_metadata_host = 127.0.0.1/nova_metadata_host = $controller/g" $metadata_ini_con
sed -i "s/\#metadata_proxy_shared_secret =/metadata_proxy_shared_secret = metadata_secret/g" $metadata_ini_con
sed -i "s/\#memcache_servers = localhost:11211/memcache_servers = $controller:11211/g" $metadata_ini_con

ml2_ini_control='/etc/neutron/plugins/ml2/ml2_conf.ini'
sed -i "s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g" $ml2_ini_control
sed -i "s/\#tenant_network_types = local/tenant_network_types = vxlan/g" $ml2_ini_control
sed -i "s/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g" $ml2_ini_control
sed -i "s/\#extension_drivers =/extension_drivers = port_security/g" $ml2_ini_control


con_nova_conf='/etc/nova/nova.conf'
sed -i "s/\#neutron/use_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver/g" $con_nova_conf

cat >> "/etc/nova/nova.conf" << END
[neutron]
auth_url = http://$controller:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = $pass_project_user
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata_secret


END


ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"
printf "======================================restart service=======================================\n"
systemctl restart neutron-server neutron-metadata-agent
systemctl enable neutron-server neutron-metadata-agent
systemctl restart openstack-nova-api openstack-nova-compute

}


network_node(){

printf "==================install and config netron service on NETWORK NODE=====================\n"
sleep 2
ssh root@$network "yum -y install centos-release-openstack-queens epel-release"
ssh root@$network "sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo"
ssh root@$network "yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch"

net_neutron="/root/openstack/network/neutron.conf"
sed -i "s/controller/$controller/g" $net_neutron
sed -i "s/pass_rabbitmq/$pass_rabbitmq/g" $net_neutron
sed -i "s/pass_project_user/$pass_project_user/g" $net_neutron

ssh root@$network "sed -i 's/\#interface_driver = <None>/interface_driver = openvswitch/g' /etc/neutron/l3_agent.ini"

ssh root@$network "sed -i 's/\#interface_driver = <None>/interface_driver = openvswitch/' /etc/neutron/dhcp_agent.ini"
ssh root@$network "sed -i 's/\#dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq/dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq\n\nenable_isolated_metadata = true/g' /etc/neutron/dhcp_agent.ini"


ssh root@$network "sed -i 's/\#nova_metadata_host = 127.0.0.1/nova_metadata_host = $controller/g' /etc/neutron/metadata_agent.ini"
ssh root@$network "sed -i 's/\#metadata_proxy_shared_secret =/metadata_proxy_shared_secret = metadata_secret/g' /etc/neutron/metadata_agent.ini"
ssh root@$network "sed -i 's/\#memcache_servers = localhost:11211/memcache_servers = $controller:11211/g' /etc/neutron/metadata_agent.ini"


ssh root@$network "sed -i 's/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\#tenant_network_types = local/tenant_network_types = vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\#extension_drivers =/extension_drivers = port_security/g' /etc/neutron/plugins/ml2/ml2_conf.ini"

ssh root@$network "sed -i 's/\#firewall_driver = <None>/firewall_driver = openvswitch/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$network "sed -i 's/\#enable_security_group = true/enable_security_group = true/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$network "sed -i 's/\#enable_ipset = true/enable_ipset = true/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"

scp /root/openstack/network/neutron.conf root@$network:/etc/neutron/

ssh root@$network "ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini"
ssh root@$network "systemctl start openvswitch && systemctl enable openvswitch"
ssh root@$network "ovs-vsctl add-br br-int"
ssh root@$network "for service in dhcp-agent l3-agent metadata-agent openvswitch-agent; do
systemctl start neutron-\$service
systemctl enable neutron-\$service
done"

printf "======================================install and config netron service done===================\n"

}

compute_node(){
printf "===============================Install libvirt and nova-compute node=====================\n"
sleep 2
ssh root@$compute "yum -y install centos-release-openstack-queens epel-release"
ssh root@$compute "sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo"
ssh root@$compute "yum -y install qemu-kvm libvirt virt-install"
ssh root@$compute "systemctl start libvirtd && systemctl enable libvirtd"


ssh root@$compute "yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova-compute"

com_nova='/root/openstack/compute/nova.conf'
sed -i "s/compute/$compute/g" $com_nova
sed -i "s/pass_rabbitmq/$pass_rabbitmq/g" $com_nova
sed -i "s/controller/$controller/g" $com_nova
sed -i "s/pass_project_user/$pass_project_user/g" $com_nova

scp /root/openstack/compute/nova.conf root@$compute:/etc/nova/

ssh root@$compute "chmod 640 /etc/nova/nova.conf"
ssh root@$compute "chgrp nova /etc/nova/nova.conf"

printf "======================restart openstack-nova-compute and discovery host======================\n "

ssh root@$compute "systemctl restart openstack-nova-compute"
ssh root@$compute "systemctl restart openstack-nova-compute"

su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"
source keystonerc && openstack compute service list

printf "======================================Install neutron, openvswitch=========================\n"
sleep 2
ssh root@$compute "yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch"

com_neutron='/root/openstack/compute/neutron.conf'
sed -i "s/controller/$controller/g" $com_neutron
sed -i "s/pass_rabbitmq/$pass_rabbitmq/g" $com_neutron
sed -i "s/pass_project_user/$pass_project_user/g" $com_neutron


ssh root@$compute "sed -i 's/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\#tenant_network_types = local/tenant_network_types = vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\#extension_drivers =/extension_drivers = port_security/g' /etc/neutron/plugins/ml2/ml2_conf.ini"


ssh root@$compute "sed -i 's/\#firewall_driver = <None>/firewall_driver = openvswitch/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$compute "sed -i 's/\#enable_security_group = true/enable_security_group = true/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$compute "sed -i 's/\#enable_ipset = true/enable_ipset = true/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"


com_nova_config='/root/openstack/compute/nova.conf'
sed -i "s/\#neutron/use_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver\nvif_plugging_is_fatal = True\nvif_plugging_timeout = 300/g" $com_nova_config

cat >> "/root/openstack/compute/nova.conf" << END
[neutron]
auth_url = http://$controller:5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = $pass_project_user
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata_secret


END

ssh root@$compute "chmod 640 /etc/neutron/neutron.conf"
ssh root@$compute "chgrp neutron /etc/neutron/neutron.conf"

printf "======================================transfer to compute node==========================\n"
sleep 2
scp /root/openstack/compute/neutron.conf root@$compute:/etc/neutron
scp /root/openstack/compute/nova.conf root@$compute:/etc/nova/

printf "======================================start and enale service============================\n"
sleep 2
ssh root@$compute "ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini"
ssh root@$compute "systemctl start openvswitch && systemctl enable openvswitch"
ssh root@$compute "ovs-vsctl add-br br-int"
ssh root@$compute "systemctl restart openstack-nova-compute && systemctl enable openstack-nova-compute"
ssh root@$compute "systemctl start neutron-openvswitch-agent && systemctl enable neutron-openvswitch-agent"

printf "===============================Install libvirt and nova-compute node done=====================\n"

}

cinder_controller (){
printf "===============================Configure Cinder (Control Node)==========================\n"
sleep 2

source keystonerc && openstack user create --domain default --project service --password $pass_project_user cinder
source keystonerc && openstack role add --project service --user cinder admin
source keystonerc && openstack service create --name cinderv2 --description "OpenStack Block Storage" volumev2
source keystonerc && openstack service create --name cinderv3 --description "OpenStack Block Storage" volumev3

source keystonerc && openstack endpoint create --region RegionOne volumev2 public http://$controller:8776/v2/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne volumev2 internal http://$controller:8776/v2/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne volumev2 admin http://$controller:8776/v2/%\(tenant_id\)s

source keystonerc && openstack endpoint create --region RegionOne volumev3 public http://$controller:8776/v3/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne volumev3 internal http://$controller:8776/v3/%\(tenant_id\)s
source keystonerc && openstack endpoint create --region RegionOne volumev3 admin http://$controller:8776/v3/%\(tenant_id\)s

mysql -uroot -p$rootsql -e "create database cinder;"
mysql -uroot -p$rootsql -e "grant all privileges on cinder.* to cinder@'localhost' identified by '"$pass_user_sql"';"
mysql -uroot -p$rootsql -e "grant all privileges on cinder.* to cinder@'%' identified by '"$pass_user_sql"';"
mysql -uroot -p$rootsql -e "flush privileges;"

printf "===============================Install Cinder Service ==============================="
#controller
sleep 2
yum --enablerepo=centos-openstack-queens,epel -y install openstack-cinder


cat > "/etc/cinder/cinder.conf" << END
# create new
[DEFAULT]
# define own IP address
my_ip = $controller
log_dir = /var/log/cinder
state_path = /var/lib/cinder
auth_strategy = keystone
# RabbitMQ connection info
transport_url = rabbit://openstack:$pass_rabbitmq@$controller
debug = true

# MariaDB connection info
[database]
connection = mysql+pymysql://cinder:$pass_user_sql@$controller/cinder

# Keystone auth info
[keystone_authtoken]
www_authenticate_uri = http://$controller:5000
auth_url = http://$controller:5000
memcached_servers = $controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = cinder
password = $pass_project_user

[oslo_concurrency]
lock_path = \$state_path/tmp


END

chmod 640 /etc/cinder/cinder.conf  && chgrp cinder /etc/cinder/cinder.conf
printf "======================================sync db cinder======================================\n"
sleep 2
su -s /bin/bash cinder -c "cinder-manage db sync"

printf "======================================restart and enable service==========================\n"
sleep 2
systemctl start openstack-cinder-api openstack-cinder-scheduler
systemctl enable openstack-cinder-api openstack-cinder-scheduler

printf "======================================show status volume=================================\n"
sleep 7
source keystonerc && openstack volume service list


}


storage_node (){
printf "=====================Install and configure Cinder (Storage Node) use LVM ================\n"
# storage node
sleep 2

ssh root@$storage "yum -y install centos-release-openstack-queens epel-release"
ssh root@$storage "sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo"
ssh root@$storage "yum --enablerepo=centos-openstack-queens,epel -y install openstack-cinder python2-crypto targetcli lvm2"

cinder="/root/openstack/storage/cinder.conf"
sed -i "s/storage/$storage/g" $cinder
sed -i "s/pass_rabbitmq/$pass_rabbitmq/g" $cinder
sed -i "s/controller/$controller/g" $cinder
sed -i "s/pass_user_sql/$pass_user_sql/g" $cinder
sed -i "s/pass_project_user/$pass_project_user/g" $cinder

scp /root/openstack/storage/cinder.conf root@$storage:/etc/cinder/

ssh root@$storage "chmod 640 /etc/cinder/cinder.conf && chgrp cinder /etc/cinder/cinder.conf "

printf "=============================start and enable service cinder==============================\n"
sleep 2
ssh root@$storage "systemctl start openstack-cinder-volume  && systemctl enable openstack-cinder-volume"


################################### config disk lvm

printf "=============================format partition=============================\n"
sleep 2
dev=$(ssh root@$storage "fdisk -l | grep sdb | cut -f 1 -d ':' | cut -f 2 -d ' '")

ssh root@$storage "fdisk $dev <<EOF

n
p




w

EOF"


printf "=============================convert partion to lvm=============================\n"
sleep 2

ssh root@$storage "fdisk $dev <<EOF

t
8e
w

EOF"

printf "=============================create group and volume data=============================\n"
sleep 2
ssh root@$storage "pvcreate "$dev"1"
ssh root@$storage "vgcreate -s 32M vg-data "$dev"1"

#size=$(ssh root@$storage "fdisk -l | grep sdb | cut -f 3 -d ' ' | cut -f 1 -d '.'")
#
#lvm=$(expr $size - 2)
#
#ssh root@$storage "lvcreate -L " $lvm"G -n lv-data vg-data"


cinder_lvm="/root/openstack/storage/cinder.conf"
sed -i "s/#lvm/enabled_backends = lvm/g" $cinder_lvm

cat >> "/root/openstack/storage/cinder.conf" << END

# add follows to the end
[lvm]
iscsi_helper = lioadm
# volume group name just created
volume_group = vg-data
# IP address of Storage Node
iscsi_ip_address = $storage
volume_driver = cinder.volume.drivers.lvm.LVMVolumeDriver
volumes_dir = \$state_path/volumes
iscsi_protocol = iscsi


END


scp /root/openstack/storage/cinder.conf root@$storage:/etc/cinder/

echo "export OS_VOLUME_API_VERSION=2" >> /root/keystonerc

printf "=================================restart cinder-volume service=============================\n"
sleep 2
ssh root@$storage "systemctl restart openstack-cinder-volume "



#####cinder compute node

cinder_nova='/root/openstack/compute/nova.conf'
cat >> "/root/openstack/compute/nova.conf" << END


[cinder]
os_region_name = RegionOne


END

scp /root/openstack/compute/nova.conf root@$compute:/etc/nova/

printf "=====================================openstack-nova-compute===================================\n"
sleep 2
ssh root@$compute "systemctl restart openstack-nova-compute "

ssh root@$storage "reboot"

}


horizon_install(){

printf "======================================horizon_install======================================\n"
sleep 2

yum --enablerepo=centos-openstack-queens,epel -y install openstack-dashboard

cp -f /root/openstack/controller/local_settings /etc/openstack-dashboard/
local_settings='/etc/openstack-dashboard/local_settings'
sed -i "s/ALLOWED_HOSTS = \['horizon.example.com', 'localhost']/ALLOWED_HOSTS = ['$controller', 'localhost']/g" $local_settings
sed -i "s/\'LOCATION': '$controller:11211',/\   	'LOCATION': '$controller:11211',/g" $local_settings
sed -i "s/OPENSTACK_HOST = \"127.0.0.1\"/OPENSTACK_HOST = \"$controller\"/g" $local_settings

dashboard_conf='/etc/httpd/conf.d/openstack-dashboard.conf'
sed -i "s/WSGISocketPrefix run\/wsgi/WSGISocketPrefix run\/wsgi\nWSGIApplicationGroup %{GLOBAL}/g" $dashboard_conf

printf "======================================Restart httpd======================================\n"
systemctl restart httpd

}

vxlan_all(){
printf "======================================config vxlan======================================\n"

all_ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
sed -i "s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g" $all_ml2_ini
sed -i "s/\#tenant_network_types = local/tenant_network_types = vxlan/g" $all_ml2_ini
sed -i "s/\#flat_networks = \*/flat_networks = physnet1/g" $all_ml2_ini
sed -i "s/\[ml2_type_vxlan]/\[ml2_type_vxlan]\n\#ranges =/g" $all_ml2_ini
sed -i "s/\#ranges =/\nvni_ranges = 1:1000/" $all_ml2_ini

inf=$(ls /sys/class/net/ | awk "{ if (NR == 3) print \$0}")
echo $inf
ovs-vsctl add-br br-$inf
ovs-vsctl add-port br-$inf $inf

all_openvswitch_ini='/etc/neutron/plugins/ml2/openvswitch_agent.ini'
sed -i "s/\[agent]/\[agent]\ntunnel_types = vxlan\nl2_population = True\nprevent_arp_spoofing = True/g" $all_openvswitch_ini
sed -i "s/\#local_ip = <None>/local_ip = $controller/g" $all_openvswitch_ini
sed -i "s/\#bridge_mappings =/bridge_mappings = physnet1:br-ens37/g" $all_openvswitch_ini

printf "======================================restart service=====================================\n"
sleep 2
systemctl restart neutron-server
for service in dhcp-agent l3-agent metadata-agent openvswitch-agent; do
systemctl restart neutron-$service
done
systemctl restart neutron-openvswitch-agent

printf "======================================config VXLAN done=================================\n"

}

vxlan_con(){
printf "======================================config vxlan controller============================\n"
con_ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
sed -i "s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g" $con_ml2_ini
sed -i "s/\#flat_networks = \*/flat_networks = physnet1/g" $con_ml2_ini
sed -i "s/\#tenant_network_types = local/tenant_network_types = vxlan/g" $con_ml2_ini
sed -i "s/\[ml2_type_vxlan]/\[ml2_type_vxlan]\n\#ranges =/g" $con_ml2_ini
sed -i "s/\#ranges =/\nvni_ranges = 1:1000/" $con_ml2_ini

systemctl restart neutron-server

 printf "==================================config VXLAN on controller done=======================\n"

}

vxlan_net(){
printf "======================================config vxlan network================================\n"

inf=$(ssh root@$network "ls /sys/class/net/ | awk '{ if (NR == 3) print \$0}'")
echo $inf
ssh root@$network "ovs-vsctl add-br br-$inf"
ssh root@$network "ovs-vsctl add-port br-$inf $inf"


ssh root@$network "sed -i 's/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\#flat_networks = \*/flat_networks = physnet1/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\#tenant_network_types = local/tenant_network_types = vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\[ml2_type_vxlan]/\[ml2_type_vxlan]\n\#ranges =/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$network "sed -i 's/\#ranges =/\nvni_ranges = 1:1000/' /etc/neutron/plugins/ml2/ml2_conf.ini"

ssh root@$network "sed -i 's/\[agent]/\[agent]\ntunnel_types = vxlan\nl2_population = True\nprevent_arp_spoofing = True/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$network "sed -i 's/\#local_ip = <None>/local_ip = $network/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$network "sed -i 's/\#bridge_mappings =/bridge_mappings = physnet1:br-ens37/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"

ssh root@$network "systemctl restart neutron-openvswitch-agent"

printf "============================config VXLAN on Network done and reboot==========================\n"

ssh root@$network "reboot"

}

vxlan_com(){

printf "======================================config vxlan compute===================================\n"

ssh root@$compute "sed -i 's/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\#tenant_network_types = local/tenant_network_types = vxlan/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\#flat_networks = \*/flat_networks = physnet1/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\[ml2_type_vxlan]/\[ml2_type_vxlan]\n\#ranges =/g' /etc/neutron/plugins/ml2/ml2_conf.ini"
ssh root@$compute "sed -i 's/\#ranges =/\nvni_ranges = 1:1000/' /etc/neutron/plugins/ml2/ml2_conf.ini"

ssh root@$compute "sed -i 's/\[agent]/\[agent]\ntunnel_types = vxlan\nl2_population = True\nprevent_arp_spoofing = True/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"
ssh root@$compute "sed -i 's/\#local_ip = <None>/local_ip = $compute/g' /etc/neutron/plugins/ml2/openvswitch_agent.ini"


ssh root@$compute "systemctl restart neutron-openvswitch-agent"

printf "=================================config VXLAN on Computer done and reboot=====================\n"

ssh root@$compute "reboot"


}

key_private(){

printf "======================================key_private=============================================\n"
sleep 2

source /root/keystonerc && openstack keypair create --public-key /root/.ssh/id_rsa.pub mykey

}

options=("INSTALLL 1 NODE)" "INSTALL 2 NODE (CONTROLLER-COMPUTE)" "INSTALL 3 NODE (CONTROLLER-NETWORK-COMPUTE)" "INSTALL 3 NODE (CONTROLLER-COMPUTE-STORAGE(LVM-BackEnds))" "INSTALL 3 NODE (CONTROLLER-COMPUTE-STORAGE(NFS-BackEnds))" "INSTALL 3 NODE (CONTROLLER-COMPUTE-STORAGE(Multi-BackEnds))" ) # End Options

printf "==============================================================================================\n"
printf "                                  Menu\n"
printf "===============================================================================================\n"
PS3="
$prompt"
select opt in "${options[@]}" "THOAT"; do

    case "$REPLY" in
	    1 )
	        echo "Enter IP Controller node: "
            read controller

            echo "Enter password admin: "
            read pass_admin

            userabbitmq='openstack'
            echo "Enter passwork rabbitmq:"
            read pass_rabbitmq

            echo "Enter password root sql:"
            read rootsql

            echo "Enter password user sql:"
            read pass_user_sql

            echo "Enter password user service:"
            read pass_project_user


	        requirements
	        keytone
	        glance
	        nova_Keystone
	        nova_install_conf
	        nova_compute
	        neutron_Keystone
	        neutron_server_all
	        horizon_install
	        vxlan_all
	        key_private
	        cat >"info" << END
ip controller: $controller
user: admin
pass admin: $pass_admin
pass root sql: $rootsql
pass user sql: $pass_user_sql
pass user service: $pass_project_user
user RabbitMQ: openstack
pass RabbitMQ: $pass_rabbitmq
Link dashboard http//$controller/dashboard
domain: default
user: admin
password: $pass_admin
END
	         printf "\nLink dashboard http://$controller/dashboard user: admin password: $pass_admin\n"
	         reboot;;
	    2 )
            echo "Enter IP Controller node: "
            read controller

             echo "Enter IP Compute node: "
            read compute

            echo "Enter password admin: "
            read pass_admin

            userabbitmq='openstack'
            echo "Enter passwork rabbitmq:"
            read pass_rabbitmq

            echo "Enter password root sql:"
            read rootsql

            echo "Enter password user sql:"
            read pass_user_sql

            echo "Enter password user service:"
            read pass_project_user

            printf "======================================transfer key ssh====================================\n"
            sleep 2

            ssh-copy-id -i /root/.ssh/id_rsa.pub root@$compute
            ssh root@$compute "systemctl stop firewalld && systemctl disable firewalld"
            ssh root@$compute "systemctl stop NetworkManager && systemctl disable NetworkManager"
            ssh root@$compute "sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"
            ssh root@$compute "sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"

	        requirements
	        keytone
	        glance
	        nova_Keystone
	        nova_install_conf
	        nova_compute
	        neutron_Keystone
	        neutron_server_all
	        horizon_install
	        compute_node
	        vxlan_all
            vxlan_com
            key_private

            cat >"info" << END
ip controller: $controller
ip compute: $compute
user: admin
pass admin: $pass_admin
pass root sql: $rootsql
pass user sql: $pass_user_sql
pass user service: $pass_project_user
user RabbitMQ: openstack
pass RabbitMQ: $pass_rabbitmq
Link dashboard http//$controller/dashboard
domain: default
user: admin
password: $pass_admin
END
	         printf "\nLink dashboard http://$controller/dashboard user: admin password: $pass_admin\n"
	         reboot;;
	    3 )
            echo "Enter IP Controller node: "
            read controller

            echo "Enter IP Network node: "
            read network

            echo "Enter IP Compute node: "
            read compute

            echo "Enter password admin: "
            read pass_admin

            userabbitmq='openstack'
            echo "Enter passwork rabbitmq:"
            read pass_rabbitmq

            echo "Enter password root sql:"
            read rootsql

            echo "Enter password user sql:"
            read pass_user_sql

            echo "Enter password user service:"
            read pass_project_user

	        printf "======================================transfer key ssh====================================\n"
            sleep 2

            ssh-copy-id -i /root/.ssh/id_rsa.pub root@$compute
            ssh root@$compute "systemctl stop firewalld && systemctl disable firewalld"
            ssh root@$compute "systemctl stop NetworkManager && systemctl disable NetworkManager"
            ssh root@$compute "sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"
            ssh root@$compute "sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"

            ssh-copy-id -i /root/.ssh/id_rsa.pub root@$network
            ssh root@$network "systemctl stop firewalld && systemctl disable firewalld"
            ssh root@$network "systemctl stop NetworkManager && systemctl disable NetworkManager"
            ssh root@$network "sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"
            ssh root@$network "sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"

	        requirements
            keytone
            glance
            nova_Keystone
            nova_install_conf
            nova_compute
            neutron_Keystone
            neutron_server_control
            network_node
            horizon_install
            compute_node
            vxlan_con
            vxlan_net
            vxlan_com
            key_private

            cat >"info" << END
ip controller: $controller
ip network: $network
ip compute: $compute
user: admin
pass admin: $pass_admin
pass root sql: $rootsql
pass user sql: $pass_user_sql
pass user service : $pass_project_user
user RabbitMQ: openstack
pass RabbitMQ: $pass_rabbitmq
Link dashboard http//$controller/dashboard
domain: default
user: admin
password: $pass_admin
END
             printf "\nLink dashboard http://$controller/dashboard user: admin password: $pass_admin\n"
             reboot;;
		    # End Menu

		4 )
            echo "Enter IP Controller node: "
            read controller

            echo "Enter IP Network node: "
            read storage

            echo "Enter IP Compute node: "
            read compute

            echo "Enter password admin: "
            read pass_admin

            userabbitmq='openstack'
            echo "Enter passwork rabbitmq:"
            read pass_rabbitmq

            echo "Enter password root sql:"
            read rootsql

            echo "Enter password user sql:"
            read pass_user_sql

            echo "Enter password user service:"
            read pass_project_user

            printf "======================================transfer key ssh====================================\n"
            sleep 2

            ssh-copy-id -i /root/.ssh/id_rsa.pub root@$compute
            ssh root@$compute "systemctl stop firewalld && systemctl disable firewalld"
            ssh root@$compute "systemctl stop NetworkManager && systemctl disable NetworkManager"
            ssh root@$compute "sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"
            ssh root@$compute "sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"

            ssh-copy-id -i /root/.ssh/id_rsa.pub root@$storage
            ssh root@$storage "systemctl stop firewalld && systemctl disable firewalld"
            ssh root@$storage "systemctl stop NetworkManager && systemctl disable NetworkManager"
            ssh root@$storage "sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"
            ssh root@$storage "sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"

		    requirements
	        keytone
	        glance
	        nova_Keystone
	        nova_install_conf
	        nova_compute
	        neutron_Keystone
	        neutron_server_all
	        horizon_install
	        compute_node
	        cinder_controller
	        storage_node
	        vxlan_all
            vxlan_com
            key_private


            cat >"info" << END
ip config: $controller
ip compute: $compute
ip storage: $storage
user: admin
pass admin: $pass_admin
pass root sql: $rootsql
pass user sql: $pass_user_sql
pass service keytone: $pass_project_user
user RabbitMQ: openstack
pass RabbitMQ: $pass_rabbitmq
Link dashboard http//$controller/dashboard
domain: default
user: admin
password: $pass_admin
END
            printf "\nLink dashboard http://$controller/dashboard user: admin password: $pass_admin\n"
            reboot;;
        5 ) exit;;
        6 ) exit;;

	    $(( ${#options[@]}+1 )) ) printf "\nChao tam biet!\nLink dashboard http://$controller/dashboard user: admin password: $pass_admin\n\n" ; break;;
	    *) echo "Ban nhap sai, vui long nhap theo so thu tu tren danh sach";continue;;


    esac

done










