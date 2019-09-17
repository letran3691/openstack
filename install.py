#!/usr/bin/python3.6

import sys,os,time,fileinput,subprocess

print('Chuan bi cho qua trinh cai dat va cau hinh .'.upper())
time.sleep(3)
ip_controller = input('Nhap ip controller node: ')
ip_compute = input('Nhap ip compute node: ')
ip_stogare = input('Nhap ip storage node: ')

hn_controller = input('\nNhap hostname controller node: ')
hn_compute = input('Nhap hostname compute node: ')
hn_storage = input('Nhap hostname storage node: ')

memcache_user = 'openstack'
pass_memcache = input('\nNhap password memcache: ')
pass_admin = input('Nhap password admin: ')
rootsql = input('Nhap password root sql: ')
pass_user_service = input('Nhap password user services: ')



############################ create key ssh ############################################################################

print('\nCreate key ssh')

time.sleep(2)

os.system("ssh-keygen -q -t rsa -f ~/.ssh/id_rsa -N ''")

print('\nCreate key ssh done!!!')
time.sleep(2)

os.system('systemctl stop firewalld')
os.system('systemctl disable firewalld')

os.system(str("sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"))
os.system(str("sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"))

########################################################################################################################

#os.system('yum -y install centos-release-openstack-queens epel-release && yum -y install  python36 python36-devel python36-setuptools ')
#os.system(str("sed -i -e 's/enabled=1/enabled=0/g' /etc/yum.repos.d/CentOS-OpenStack-queens.repo "))

# install Mariadb
#os.system('yum --enablerepo=centos-openstack-queens -y install mariadb-server')

##############################    COPY PRIVATE KEY   ###################################################################

# os.system('ssh-copy-id -i /root/.ssh/id_rsa.pub root@'+ip_compute)
# os.system('ssh-copy-id -i /root/.ssh/id_rsa.pub root@'+ip_stogare)

############################## INSTALL MARIADB #########################################################################

print('\nBegin install Mariadb\n')
time.sleep(2)
os.system('curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash')
os.system('yum -y install MariaDB-server')

server_conf='/etc/my.cnf.d/server.cnf'
subprocess.call(["sed","--in-place",r"s/\[mysqld]/[mysqld]\ncharacter-set-server=utf8/g",server_conf])

os.system('systemctl start mariadb.service')
os.system('systemctl enable mariadb.service')
os.system('''mysql_secure_installation <<EOF

            y'''
            +rootsql
            +rootsql
            +'''
            y
            y
            y
            y
            EOF''')

print('\nBegin install Mariadb done\n')
################################# 	Install RabbitMQ, Memcached ########################################################

print('Install RabbitMQ, Memcached')

time.sleep(2)

os.system('yum --enablerepo=epel -y install rabbitmq-server memcached')
os.system('systemctl start rabbitmq-server memcached')
os.system('systemctl enable rabbitmq-server memcached')

os.system('rabbitmqctl add_user '+memcache_user +' '+ pass_memcache)
os.system('rabbitmqctl set_permissions '+memcache_user+' ".*" ".*" ".*"')

print('Install RabbitMQ, Memcached done')
time.sleep(2)
######################### Add a User and Database on MariaDB for Keystone ##############################################

###### print("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"") ##### debug sql

print('Add a User and Database on MariaDB for Keystone')

time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database keystone;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'%' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

print('Add a User and Database on MariaDB for Keystone done ')
time.sleep(2)
########################## 	Install Keystone ###########################################################################

print('Install Keystone')

time.sleep(2)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-keystone openstack-utils python-openstackclient httpd mod_wsgi')

token_conf='/etc/keystone/keystone.conf'
subprocess.call(["sed","--in-place",r"s/\#memcache_servers = localhost:11211/\nmemcache_servers = "+ip_controller+":11211/g",token_conf])
subprocess.call(["sed","--in-place",r"s/\#connection = <None>/\nconnection = mysql+pymysql:\/\/keystone:"+pass_user_service+"@"+ip_controller+"\/keystone/g",token_conf])
subprocess.call(['sed','--in-place',r's/\#bind =/\nprovider = fernet\n\n#bind =/',token_conf])

os.system('su -s /bin/bash keystone -c "keystone-manage db_sync"')
os.system('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone')
os.system('keystone-manage credential_setup --keystone-user keystone --keystone-group keystone')

os.system("keystone-manage bootstrap --bootstrap-password "+pass_admin+" --bootstrap-admin-url http://"+ip_controller+":5000/v3/ --bootstrap-internal-url http://"+ip_controller+":5000/v3/ --bootstrap-public-url http://"+ip_controller+":5000/v3/ --bootstrap-region-id RegionOne")
os.system('ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/')
os.system('systemctl start httpd')
os.system('systemctl enable httpd')

print('Install Keystone done')
time.sleep(2)
###############################  Create and Load environment variables file ############################################

print('environment variables file')

time.sleep(2)

os.system('''cat > "/root/keystonerc" <<END
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD='''+pass_admin+'''
export OS_AUTH_URL=http://'''+ip_controller+''':5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export PS1='[\\u@\h \W(keystone)]\$ '

END''')

os.system('chmod 600 /root/keystonerc')
os.system('source /root/keystonerc')
#os.system('echo "source /root/keystonerc " >> /root/.bash_profile')

############################## Create Projects #########################################################################

print('Create Projects')

time.sleep(2)

os.system('source /root/keystonerc && openstack project create --domain default --description "Service Project" service ')
os.system('source /root/keystonerc && openstack project list ')

############################ Add users and others for Glance in Keystone ###############################################

print('Add Glance keytone')
time.sleep(2)

os.system("source /root/keystonerc && openstack user create --domain default --project service --password "+pass_user_service+" glance")
os.system("source /root/keystonerc && openstack role add --project service --user glance admin")
os.system('source /root/keystonerc && openstack service create --name glance --description "OpenStack Image service" image')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image public http://'+ip_controller+':9292')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image internal http://'+ip_controller+':9292')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image admin http://'+ip_controller+':9292')

########################## Add a User and Database on MariaDB for Glance ###############################################

print('Create Glance database')
time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database glance;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on glance.* to glance@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on glance.* to glance@'%' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

############################### Install Glance #########################################################################
print("Install Glance")
time.sleep(2)

os.system("yum --enablerepo=centos-openstack-queens,epel -y install openstack-glance")
os.system('mv /etc/glance/glance-api.conf /etc/glance/glance-api.conf.org ')

############################# config Glance ############################################################################

glance_api ='/root/openstack/controller/glance-api.conf'
subprocess.call(['sed','--in-place',r's/pass_user_service/'+pass_user_service+'/g',glance_api])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',glance_api])
os.system('cp /root/openstack/controller/glance-api.conf /etc/glance/')

os.system('mv /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.org ')
subprocess.call(['sed','--in-place',r's/pass_user_service/'+pass_user_service+'/g',glance_api])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',glance_api])
os.system('cp /root/openstack/controller/glance-registry.conf /etc/glance/')


print('phan quyen file Glance ')
time.sleep(2)
os.system('chmod 640 /etc/glance/glance-api.conf /etc/glance/glance-registry.conf ')
os.system('chown root:glance /etc/glance/glance-api.conf /etc/glance/glance-registry.conf')
os.system('su -s /bin/bash glance -c "glance-manage db_sync"')

print('restart servicer glance')
time.sleep(2)
os.system('systemctl start openstack-glance-api openstack-glance-registry ')
os.system('systemctl enable openstack-glance-api openstack-glance-registry ')

################################### Compute Service (Nova) #############################################################


os.system("source /root/keystonerc && openstack user create --domain default --project service --password "+pass_user_service+" nova")
os.system("source /root/keystonerc && openstack role add --project service --user nova admin")
os.system("source /root/keystonerc && openstack user create --domain default --project service --password "+pass_user_service+" placement")
os.system("source /root/keystonerc && openstack role add --project service --user placement admin")
os.system('source /root/keystonerc && openstack service create --name nova --description "OpenStack Compute service" compute')
os.system('source /root/keystonerc && openstack service create --name placement --description "OpenStack Compute Placement service" placement')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute public http://'+ip_controller+':8774/v2.1/%\(tenant_id\)s')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute internal http://'+ip_controller+':8774/v2.1/%\(tenant_id\)s')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement public http://'+ip_controller+':8778')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement internal http://'+ip_controller+':8778')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement admin http://'+ip_controller+':8778')

########################## Add a User and Database on MariaDB for Nova ###############################################

print('Create nova, nova_api, nova_placement, nova_cell0 database')
time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova.* to nova@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova.* to nova@'%' identified by"' \'' +pass_user_service+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_api;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_api.* to nova@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_api.* to nova@'%' identified by"' \'' +pass_user_service+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_placement;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_placement.* to nova@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_placement.* to nova@'%' identified by"' \'' +pass_user_service+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_cell0;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_cell0.* to nova@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_cell0.* to nova@'%' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

##################################### Install Nova and config services #################################################
print('Install Nova services')
time.sleep(2)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova')

print('Config Nova')
time.sleep(2)

###################################### config nova node controller #####################################################
os.system('mv /etc/nova/nova.conf /etc/nova/nova.conf.org')

con_nova_conf = '/root/openstack/controller/nova.conf'
subprocess.call(['sed','--in-place',r's/pass_user_service/'+pass_user_service+'/g',con_nova_conf])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',con_nova_conf])
os.system('cp /root/openstack/controller/nova.conf /etc/glance/')

print('Phan quyen nova')
time.sleep(2)
os.system('chmod 640 /etc/nova/nova.conf')
os.system('chgrp nova /etc/nova/nova.conf')

os.system('cp -f /root/openstack/controller/00-nova-placement-api.conf /etc/httpd/conf.d/')

################################# 	Add Data into Database and start Nova services #####################################

os.system('su -s /bin/bash nova -c "nova-manage api_db sync"')
os.system('su -s /bin/bash nova -c "nova-manage cell_v2 map_cell0"')
os.system('su -s /bin/bash nova -c "nova-manage db sync"')
os.system('su -s /bin/bash nova -c "nova-manage cell_v2 create_cell --name cell1"')
os.system('systemctl restart httpd')
os.system('chown nova. /var/log/nova/nova-placement-api.log')

os.system('''for service in api consoleauth conductor scheduler novncproxy; do
systemctl start openstack-nova-$service
systemctl enable openstack-nova-$service
done''')
os.system('source /root/keystonerc && openstack compute service list')

############################## NODE compute ############################################################################

print('Cai dat va cau hinh node compute'.upper())
time.sleep(3)

os.system('ssh root@'+ip_compute+' yum -y install centos-release-openstack-queens epel-release')
os.system('ssh root@'+ip_compute+' sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo')
os.system('ssh root@'+ip_compute+' yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova-compute')

############################## config nova node compute ################################################################
os.system('ssh root@'+ip_compute+' mv /etc/nova/nova.conf /etc/nova/nova.conf.org')
com_nova_conf = '/root/openstack/compute/nova.conf'
subprocess.call(['sed','--in-place',r's/ip_compute/'+ip_compute+'/g',com_nova_confnova_conf])
subprocess.call(['sed','--in-place',r's/pass_user_service/'+pass_user_service+'/g',com_nova_confnova_conf])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',com_nova_confnova_conf])
os.system('scp /root/openstack/compute/nova.conf root@'+ip_compute+':/etc/nova/')
os.system('ssh root@'+ip_compute+' chmod 640 /etc/nova/nova.conf')
os.system('ssh root@'+ip_compute+' chgrp nova /etc/nova/nova.conf')

############################## Start Nova Compute Service on node compute ##############################################
os.system('ssh root@'+ip_compute+' systemctl restart openstack-nova-compute; systemctl enable openstack-nova-compute')

############################## discover Compute Nodes ##################################################################
print('discover Compute Node')
time.sleep(2)
os.system('source /root/keystonerc && su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"')
os.system('source /root/keystonerc && openstack compute service list')

################################## Network Service (Neutron) ###########################################################

print('Add user or service for Neutron on Keystone Server'.title())
time.sleep(3)
os.system('source /root/keystonerc && openstack user create --domain default --project service --password '+pass_user_service+' neutron')
os.system('source /root/keystonerc && openstack role add --project service --user neutron admin')
os.system('source /root/keystonerc && openstack service create --name neutron --description "OpenStack Networking service" network')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network public http://'+ip_controller+':9696')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network internal http://'+ip_controller+':9696')
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network admin http://'+ip_controller+':9696')

############################################## Add a User and Database on MariaDB for Neutron ##########################
print('Add a User and Database on MariaDB for Neutron'.title())
time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database neutron_ml2;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on neutron_ml2.* to neutron@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on neutron_ml2.* to neutron@'%' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

########################################## Install neutron service #####################################################
print('Install neutron service'.title())
time.sleep(2)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch')

####################################### config neutro ##################################################################
print('Config neutron'.title())
time.sleep(2)

os.system('mv /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org')

neutron = '/root/openstack/controller/neutron.conf'
subprocess.call(['sed','--in-place',r's/pass_user_service/'+pass_user_service+'/g',neutron])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',neutron])
os.system('cp /root/openstack/controller/neutron.conf /etc/neutron/')

###################################### phan quyen ######################################################################
os.system('chmod 640 /etc/neutron/neutron.conf')
os.system('chgrp neutron /etc/neutron/neutron.conf')

l3_ini='/etc/neutron/l3_agent.ini'
subprocess.call(["sed","--in-place",r"s/\#interface_driver = <None>/interface_driver = openvswitch/g",l3_ini])

dhcp_ini='/etc/neutron/dhcp_agent.ini'
subprocess.call(["sed","--in-place",r"s/\#interface_driver = <None>/interface_driver = openvswitch/g",dhcp_ini])
subprocess.call(["sed","--in-place",r"s/\#dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq/dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq/g",dhcp_ini])
subprocess.call(["sed","--in-place",r"s/\#enable_isolated_metadata = false/enable_isolated_metadata = true/g",dhcp_ini])

metadata_ini='/etc/neutron/metadata_agent.ini'
subprocess.call(["sed","--in-place",r"s/\#nova_metadata_host = 127.0.0.1/nova_metadata_host =" +ip_controller+"/g",metadata_ini])
subprocess.call(["sed","--in-place",r"s/\#metadata_proxy_shared_secret =/metadata_proxy_shared_secret = metadata_secret/g",metadata_ini])
subprocess.call(["sed","--in-place",r"s/\#memcache_servers = localhost:11211/memcache_servers =" +ip_controller+":11211/g",metadata_ini])

ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
subprocess.call(["sed","--in-place",r"s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g",ml2_ini])
subprocess.call(["sed","--in-place",r"s/\#tenant_network_types = local/tenant_network_types =/g",ml2_ini])
subprocess.call(["sed","--in-place",r"s/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g",ml2_ini])
subprocess.call(["sed","--in-place",r"s/\#extension_drivers =/extension_drivers = port_security/g",ml2_ini])

openvswitch_ini='/etc/neutron/plugins/ml2/openvswitch_agent.ini'
subprocess.call(["sed","--in-place",r"s/\#firewall_driver = <None>/firewall_driver = openvswitch/g",openvswitch_ini])
subprocess.call(["sed","--in-place",r"s/\#enable_security_group = true/enable_security_group = true/g",openvswitch_ini])
subprocess.call(["sed","--in-place",r"s/\#enable_ipset = true/enable_ipset = true/g",openvswitch_ini])

ect_nova_conf='/etc/nova/nova.conf'
subprocess.call(["sed","--in-place",r"s/\[DEFAULT]/\[DEFAULT]\nuse_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver\nvif_plugging_is_fatal = True\nvif_plugging_timeout = 300\n/g",ect_nova_conf])

with open('/etc/nova/nova.conf', 'a+') as nova:
    nova.write('''\n[neutron]\nauth_url = http://'''+ip_controller+''':5000
                \nauth_type = password\nproject_domain_name = default
                \nuser_domain_name = default
                \nregion_name = RegionOne
                \nproject_name = service
                \nusername = neutron
                \npassword = '''+pass_user_service+'''
                \nservice_metadata_proxy = True
                \nmetadata_proxy_shared_secret = metadata_secret''')

################################ 	Start Neutron services #############################################################
print('Start Neutron services')
time.sleep(2)
os.system('systemctl start openvswitch && systemctl enable openvswitch')
os.system('ovs-vsctl add-br br-int')
os.system('ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
os.system('source /root/keystonerc && su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"')

os.system('''for service in server dhcp-agent l3-agent metadata-agent openvswitch-agent; do 
            systemctl start neutron-$service 
            systemctl enable neutron-$service 
            done''')
os.system('systemctl restart openstack-nova-api openstack-nova-compute')

os.system('source /root/keystonerc && openstack network agent list')

##################################### Configure Horizon ################################################################
print('Install Horizon.'.upper())
time.sleep(3)
os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-dashboard')

dashboard='/root/openstack/controller/local_settings'
subprocess.call(["sed","--in-place",r"s/\#ALLOWED_HOSTS = ['horizon.example.com', 'localhost']/ALLOWED_HOSTS = ['"+ip_controller+"', 'localhost']/g",dashboard])
subprocess.call(["sed","--in-place",r"s/\   	    'LOCATION': '192.168.100.10:11211',/\   	    'LOCATION': '"+ip_controller+":11211']/g",dashboard])
subprocess.call(["sed","--in-place",r"s/OPENSTACK_HOST = \"192.168.100.10\"/OPENSTACK_HOST = \""+ip_controller+"\"/g",dashboard])

dashboard_conf='/etc/httpd/conf.d/openstack-dashboard.conf'
subprocess.call(["sed","--in-place",r"s/WSGISocketPrefix run\/wsgi/WSGISocketPrefix run\/wsgi\nWSGIApplicationGroup %{GLOBAL}/g",dashboard_conf])
os.system('systemctl restart httpd')






























