#!/usr/bin/python3.6

import sys,os,time,fileinput,subprocess

print('Chuan bi cho qua trinh cai dat va cau hinh.\n'.upper())

print('\t\t\tcanh bao chu y phan network tranh nham lan'.upper())
time.sleep(3)

print('Mang mangager.')
time.sleep(3)
ip_controller = input('Nhap ip controller node: ')
ip_compute = input('Nhap ip compute node: ')
ip_stogare = input('Nhap ip storage node: ')

print('\nDinh dang netmask: 8, 16, 24')
netmask = input('Nhap sunetmask: ')
gw = input('Nhap gateway: ')


print('\nNhap dai mang cap cho VM. VD: 10.0.0.0/24')
time.sleep(3)
vmnet = input('Nhap dai mang vm: ')
vm_gw = input('Nhap gateway vm: ')
vm_dns = "8.8.8.8"

print('\nNhap dai mang cap floating IP. Co the la dai local hoac public(neu co).')
time.sleep(3)
float_ip = input('Nhap dai floating IP: ')
float_start = input('IP cap phat tu: ')
float_end = input('Den IP: ')
float_gw = input('Nhap gateway ra net cua local hoac public(neu co): ')
float_dns = '8.8.8.8'

hn_controller = input('\nNhap hostname controller node: ')
hn_compute = input('Nhap hostname compute node: ')
hn_storage = input('Nhap hostname storage node: ')

rabbitmq_user = 'openstack'
pass_rabbitmq = input('\nNhap password RabbitMQ: ')
pass_admin = input('Nhap password admin: ')
rootsql = input('Nhap password root sql: ')
pass_user_sql = input('Nhap password user sql: ')
pass_project_user = input('Nhap password project user: ')



with open('info','w+') as info:
    info.write('''Thong tin cau hinh.
                \nip controller: '''+ip_controller+'''
                \nip compute: '''+ip_compute+'''
                \nip storage: '''+ip_stogare+'''
                \nhostname controller: '''+hn_controller+'''
                \nhostname compute: '''+hn_compute+'''
                \nhostname storage: '''+hn_storage+'''
                \nrabbitmq_user: openstack
               \nPassword RabbitMQ: ''' +pass_rabbitmq+'''
               \nPassword admin: '''+pass_admin+'''
                \npassword root sql :'''+rootsql+'''
                \nPassword user services: '''+pass_user_sql+'''
                \npassword project user: '''+pass_project_user+'''
                \nDai mang vm: '''+vmnet+'''
                \nGateway vm: '''+vm_gw+'''
                \nDNS VM: '''+vm_dns+'''
                \nDai floating IP: '''+float_ip+'''
                \nIP cap phat tu: '''+float_start+'''
                \nDen IP: '''+float_end+'''
                \nGateway float IP: '''+float_gw+'''
                \nDNS floating : ''' +float_dns)

    info.close()


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


##############################    COPY PRIVATE KEY   ###################################################################
os.system('ssh root@'+ip_compute+' mkdir /root/.ssh')
os.system('ssh-copy-id -i /root/.ssh/id_rsa.pub root@'+ip_compute)
# os.system('ssh-copy-id -i /root/.ssh/id_rsa.pub root@'+ip_stogare)

############################### get network interface ##################################################################

inf_ = os.popen('ls /sys/class/net/').read().split('\n')
#print(inf_)
time.sleep(3)
inf1 =inf_[1]

os.system('ssh root@'+ip_compute+' ls /sys/class/net/ > /root/openstack/compute/infacer')
#os.system('ssh root@'+ip_stogare+' ls /sys/class/net/ > /root/openstack/storage/infacer')

################################## disable firewalld ###################################################################

os.system('ssh root@'+ip_compute+' systemctl stop firewalld')
os.system('ssh root@'+ip_compute+' systemctl disable firewalld')

os.system(str("ssh root@"+ip_compute+" sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"))
os.system(str("ssh root@"+ip_compute+" sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"))


print('\nChuan bi hoan tat - bat dau cai dat va cau hinh'.upper())
time.sleep(3)
########################################################################################################################

#os.system('yum -y install centos-release-openstack-queens epel-release && yum -y install  python36 python36-devel python36-setuptools')
os.system(str("sed -i -e 's/enabled=1/enabled=0/g' /etc/yum.repos.d/CentOS-OpenStack-queens.repo "))


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

os.system('rabbitmqctl add_user '+rabbitmq_user +' '+ pass_rabbitmq)
os.system('rabbitmqctl set_permissions '+rabbitmq_user+' ".*" ".*" ".*"')

print('\nInstall RabbitMQ, Memcached done')
time.sleep(2)
######################### Add a User and Database on MariaDB for Keystone ##############################################

###### print("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"") ##### debug sql

print('\nAdd a User and Database on MariaDB for Keystone')

time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database keystone;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'%' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

print('Add a User and Database on MariaDB for Keystone done ')
time.sleep(2)
########################## 	Install Keystone ###########################################################################

print('\nInstall Keystone')

time.sleep(2)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-keystone openstack-utils python-openstackclient httpd mod_wsgi')

token_conf='/etc/keystone/keystone.conf'
subprocess.call(["sed","--in-place",r"s/\#memcache_servers = localhost:11211/\nmemcache_servers = "+ip_controller+":11211/g",token_conf])
subprocess.call(["sed","--in-place",r"s/\#connection = <None>/\nconnection = mysql+pymysql:\/\/keystone:"+pass_user_sql+"@"+ip_controller+"\/keystone/g",token_conf])
subprocess.call(['sed','--in-place',r's/\#bind =/\nprovider = fernet\n\n#bind =/',token_conf])

os.system('su -s /bin/bash keystone -c "keystone-manage db_sync"')
os.system('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone')
os.system('keystone-manage credential_setup --keystone-user keystone --keystone-group keystone')

os.system("keystone-manage bootstrap --bootstrap-password "+pass_admin+" --bootstrap-admin-url http://"+ip_controller+":5000/v3/ --bootstrap-internal-url http://"+ip_controller+":5000/v3/ --bootstrap-public-url http://"+ip_controller+":5000/v3/ --bootstrap-region-id RegionOne")
os.system('ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/')
os.system('systemctl start httpd')
os.system('systemctl enable httpd')

print('\nInstall Keystone done')
time.sleep(2)
###############################  Create and Load environment variables file ############################################

print('\nEnvironment variables file')

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

print('\nCreate Projects')

time.sleep(2)

os.system('source /root/keystonerc && openstack project create --domain default --description "Service Project" service ')


print('\nconfirm settings')
time.sleep(2)
os.system('source /root/keystonerc && openstack project list ')

############################ Add users and others for Glance in Keystone ###############################################

print('\nAdd Glance keytone')
time.sleep(2)

print('\nadd glance user (set in service project)')
time.sleep(2)
os.system("source /root/keystonerc && openstack user create --domain default --project service --password "+pass_project_user+" glance")
os.system("source /root/keystonerc && openstack role add --project service --user glance admin")

print('\nadd service entry for glance')
time.sleep(2)
os.system('source /root/keystonerc && openstack service create --name glance --description "OpenStack Image service" image')

print('\nadd endpoint for glance (public)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image public http://'+ip_controller+':9292')

print('\nadd endpoint for glance (internal)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image internal http://'+ip_controller+':9292')

print('\nadd endpoint for glance (admin)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image admin http://'+ip_controller+':9292')

########################## Add a User and Database on MariaDB for Glance ###############################################

print('\nCreate Glance database')
time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database glance;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on glance.* to glance@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on glance.* to glance@'%' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

############################### Install Glance #########################################################################
print("\nInstall Glance")
time.sleep(2)

os.system("yum --enablerepo=centos-openstack-queens,epel -y install openstack-glance")

############################# config Glance ############################################################################
os.system('mv /etc/glance/glance-api.conf /etc/glance/glance-api.conf.org ')
os.system('cp /root/openstack/controller/glance-api.conf /etc/glance/')
glance_api ='/etc/glance/glance-api.conf'

subprocess.call(['sed','--in-place',r's/pass_user_sql/'+pass_user_sql+'/g',glance_api])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',glance_api])
subprocess.call(['sed','--in-place',r's/pass_project_user/'+pass_project_user+'/g',glance_api])


os.system('mv /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.org ')
os.system('cp /root/openstack/controller/glance-registry.conf /etc/glance/')
glance_registry='/etc/glance/glance-registry.conf'

subprocess.call(['sed','--in-place',r's/pass_user_sql/'+pass_user_sql+'/g',glance_registry])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',glance_registry])
subprocess.call(['sed','--in-place',r's/pass_project_user/'+pass_project_user+'/g',glance_registry])



print('\nPhan quyen file Glance ')
time.sleep(2)
os.system('chmod 640 /etc/glance/glance-api.conf /etc/glance/glance-registry.conf ')
os.system('chown root:glance /etc/glance/glance-api.conf /etc/glance/glance-registry.conf')
os.system('su -s /bin/bash glance -c "glance-manage db_sync"')

print('\nRestart servicer glance')
time.sleep(2)
os.system('systemctl start openstack-glance-api openstack-glance-registry ')
os.system('systemctl enable openstack-glance-api openstack-glance-registry ')

################################### Compute Service (Nova) #############################################################

print('\nAdd nova user project')
time.sleep(2)
os.system("source /root/keystonerc && openstack user create --domain default --project service --password "+pass_project_user+" nova")
os.system("source /root/keystonerc && openstack role add --project service --user nova admin")

print('\nadd placement user project')
time.sleep(2)
os.system("source /root/keystonerc && openstack user create --domain default --project service --password "+pass_project_user+" placement")
os.system("source /root/keystonerc && openstack role add --project service --user placement admin")

print('\nadd service entry for nova')
time.sleep(2)
os.system('source /root/keystonerc && openstack service create --name nova --description "OpenStack Compute service" compute')

print('\nadd service entry for placement')
time.sleep(2)
os.system('source /root/keystonerc && openstack service create --name placement --description "OpenStack Compute Placement service" placement')

print('\nadd endpoint for nova (public)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute public http://'+ip_controller+':8774/v2.1/%\(tenant_id\)s')

print('\nadd endpoint for nova (internal)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute internal http://'+ip_controller+':8774/v2.1/%\(tenant_id\)s')


print('\nadd endpoint for nova (admin)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute admin http://'+ip_controller+':8774/v2.1/%\(tenant_id\)s')


print('\nadd endpoint for placement (public)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement public http://'+ip_controller+':8778')

print('\nadd endpoint for placement (internal)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement internal http://'+ip_controller+':8778')

print('\nadd endpoint for placement (admin)')
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement admin http://'+ip_controller+':8778')

########################## Add a User and Database on MariaDB for Nova ###############################################

print('\nCreate nova, nova_api, nova_placement, nova_cell0 database')
time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova.* to nova@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova.* to nova@'%' identified by"' \'' +pass_user_sql+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_api;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_api.* to nova@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_api.* to nova@'%' identified by"' \'' +pass_user_sql+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_placement;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_placement.* to nova@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_placement.* to nova@'%' identified by"' \'' +pass_user_sql+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_cell0;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_cell0.* to nova@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_cell0.* to nova@'%' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

##################################### Install Nova and config services #################################################
print('\nInstall Nova services\n')
time.sleep(3)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova')

print('\nConfig Nova')
time.sleep(2)

###################################### config nova node controller #####################################################
os.system('mv /etc/nova/nova.conf /etc/nova/nova.conf.org')
os.system('cp /root/openstack/controller/nova.conf /etc/nova/')
con_nova_conf = '/etc/nova/nova.conf'

subprocess.call(['sed','--in-place',r's/pass_rabbitmq/'+pass_rabbitmq+'/g',con_nova_conf])
subprocess.call(['sed','--in-place',r's/pass_user_sql/'+pass_user_sql+'/g',con_nova_conf])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',con_nova_conf])
subprocess.call(['sed','--in-place',r's/pass_project_user/'+pass_project_user+'/g',con_nova_conf])


print('\nPhan quyen nova')
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

print('\nshow status')
time.sleep(2)
os.system('source /root/keystonerc && openstack compute service list')

############################## NODE compute ############################################################################

print('\nCai dat va cau hinh node compute'.upper())
time.sleep(3)

os.system('ssh root@'+ip_compute+' yum -y install centos-release-openstack-queens epel-release && yum -y install qemu-kvm libvirt virt-install')
os.system('ssh root@'+ip_compute+' sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo')
os.system('ssh root@'+ip_compute+' yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova-compute')
os.system('ssh root@'+ip_compute+' systemctl restart libvirtd; systemctl enable libvirtd')

############################## config nova node compute ################################################################
os.system('ssh root@'+ip_compute+' mv /etc/nova/nova.conf /etc/nova/nova.conf.org')
com_nova_conf = '/root/openstack/compute/nova.conf'

subprocess.call(['sed','--in-place',r's/ip_compute/'+ip_compute+'/g',com_nova_conf])
subprocess.call(['sed','--in-place',r's/pass_rabbitmq/'+pass_rabbitmq+'/g',com_nova_conf])
subprocess.call(['sed','--in-place',r's/pass_project_user/'+pass_project_user+'/g',com_nova_conf])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',com_nova_conf])

print('\ntransfer file nova.conf to compute node'.upper())
time.sleep(2)
os.system('scp /root/openstack/compute/nova.conf root@'+ip_compute+':/etc/nova/')
os.system('ssh root@'+ip_compute+' chmod 640 /etc/nova/nova.conf')
os.system('ssh root@'+ip_compute+' chgrp nova /etc/nova/nova.conf')

############################## Start Nova Compute Service on node compute ##############################################
os.system('ssh root@'+ip_compute+' systemctl restart openstack-nova-compute; systemctl enable openstack-nova-compute')

############################## discover Compute Nodes ##################################################################
print('\nDiscover Compute Node')
time.sleep(2)
os.system('source /root/keystonerc && su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"')

print('\nshow status')
time.sleep(2)
os.system('source /root/keystonerc && openstack compute service list')

################################## Network Service (Neutron) ###########################################################

print('\nAdd user or service for Neutron on Keystone Server'.title())
time.sleep(2)

print('\nadd neutron user (set in service project)'.title())
time.sleep(2)
os.system('source /root/keystonerc && openstack user create --domain default --project service --password '+pass_project_user+' neutron')
os.system('source /root/keystonerc && openstack role add --project service --user neutron admin')

print('\nadd service entry for neutron'.title())
time.sleep(2)
os.system('source /root/keystonerc && openstack service create --name neutron --description "OpenStack Networking service" network')

print('\nadd endpoint for neutron (public)'.title())
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network public http://'+ip_controller+':9696')

print('\nadd endpoint for neutron (internal)'.title())
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network internal http://'+ip_controller+':9696')

print('\nadd endpoint for neutron (admin)'.title())
time.sleep(2)
os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network admin http://'+ip_controller+':9696')

############################################## Add a User and Database on MariaDB for Neutron ##########################
print('Add a User and Database on MariaDB for Neutron'.title())
time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database neutron_ml2;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on neutron_ml2.* to neutron@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on neutron_ml2.* to neutron@'%' identified by"' \'' +pass_user_sql+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

########################################## Install neutron service #####################################################
print('\nInstall neutron service'.title())
time.sleep(2)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch')

####################################### config neutron ##################################################################
print('Config neutron'.title())
time.sleep(2)

os.system('mv /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org')
os.system('cp /root/openstack/controller/neutron.conf /etc/neutron/')
neutron = '/etc/neutron/neutron.conf'

subprocess.call(['sed','--in-place',r's/pass_rabbitmq/'+pass_rabbitmq+'/g',neutron])
subprocess.call(['sed','--in-place',r's/pass_user_sql/'+pass_user_sql+'/g',neutron])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',neutron])
subprocess.call(['sed','--in-place',r's/pass_project_user/'+pass_project_user+'/g',neutron])


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
subprocess.call(["sed","--in-place",r"s/\#nova_metadata_host = 127.0.0.1/nova_metadata_host = " +ip_controller+"/g",metadata_ini])
subprocess.call(["sed","--in-place",r"s/\#metadata_proxy_shared_secret =/metadata_proxy_shared_secret = metadata_secret/g",metadata_ini])
subprocess.call(["sed","--in-place",r"s/\#memcache_servers = localhost:11211/memcache_servers =" +ip_controller+":11211/g",metadata_ini])

ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
subprocess.call(["sed","--in-place",r"s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g",ml2_ini])
subprocess.call(["sed","--in-place",r"s/\#tenant_network_types = local/tenant_network_types = vxlan/g",ml2_ini])
subprocess.call(["sed","--in-place",r"s/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g",ml2_ini])
subprocess.call(["sed","--in-place",r"s/\#extension_drivers =/extension_drivers = port_security/g",ml2_ini])

openvswitch_ini='/etc/neutron/plugins/ml2/openvswitch_agent.ini'
subprocess.call(["sed","--in-place",r"s/\#firewall_driver = <None>/firewall_driver = openvswitch/g",openvswitch_ini])
subprocess.call(["sed","--in-place",r"s/\#enable_security_group = true/enable_security_group = true/g",openvswitch_ini])
subprocess.call(["sed","--in-place",r"s/\#enable_ipset = true/enable_ipset = true/g",openvswitch_ini])


subprocess.call(["sed","--in-place",r"s/\[DEFAULT]/\[DEFAULT]\nuse_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver\nvif_plugging_is_fatal = True\nvif_plugging_timeout = 300\n/g",con_nova_conf])


with open('/etc/nova/nova.conf', 'a+') as nova:
    nova.write('''\n[neutron]\nauth_url = http://'''+ip_controller+''':5000
                \nauth_type = password
                \nproject_domain_name = default
                \nuser_domain_name = default
                \nregion_name = RegionOne
                \nproject_name = service
                \nusername = neutron
                \npassword = '''+pass_project_user+'''
                \nservice_metadata_proxy = True
                \nmetadata_proxy_shared_secret = metadata_secret''')
    nova.close()

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
print('\nInstall Horizon.'.upper())
time.sleep(3)
os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-dashboard')

os.system('mv /etc/openstack-dashboard/local_settings /etc/openstack-dashboard/local_settings.org')
os.system('cp /root/openstack/controller/local_settings /etc/openstack-dashboard/')

dashboard='/etc/openstack-dashboard/local_settings'
subprocess.call(["sed","--in-place",r"s/ALLOWED_HOSTS = \['horizon.example.com', 'localhost']/ALLOWED_HOSTS = ['"+ip_controller+"', 'localhost']/",dashboard])
subprocess.call(["sed","--in-place",r"s/\   	    'LOCATION': '192.168.100.10:11211',/\   	    'LOCATION': '"+ip_controller+":11211',/g",dashboard])
subprocess.call(["sed","--in-place",r"s/OPENSTACK_HOST = \"127.0.0.1\"/OPENSTACK_HOST = \""+ip_controller+"\"/g",dashboard])


dashboard_conf='/etc/httpd/conf.d/openstack-dashboard.conf'
subprocess.call(["sed","--in-place",r"s/WSGISocketPrefix run\/wsgi/WSGISocketPrefix run\/wsgi\nWSGIApplicationGroup %{GLOBAL}/g",dashboard_conf])
os.system('systemctl restart httpd')


############################################ NETWORK COMPUTE NODE ######################################################
print('\nInstall neutron on compute node\n')
time.sleep(3)

os.system("ssh root@"+ip_compute+ " yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch")
os.system("ssh root@"+ip_compute+ " mv /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org ")
os.system("cp /root/openstack/compute/neutron.conf /root/openstack/compute/neutron.conf.org")

com_neutron='/root/openstack/compute/neutron.conf'
subprocess.call(['sed','--in-place',r's/pass_rabbitmq/'+pass_rabbitmq+'/g',com_neutron])
subprocess.call(['sed','--in-place',r's/ip_controller/'+ip_controller+'/g',com_neutron])
subprocess.call(['sed','--in-place',r's/pass_project_user/'+pass_project_user+'/g',com_neutron])
os.system("scp /root/openstack/compute/neutron.conf root@"+ip_compute+":/etc/neutron/")
os.system('ssh root@'+ip_compute+ ' chmod 640 /etc/neutron/neutron.conf')
os.system('ssh root@'+ip_compute+ ' chgrp neutron /etc/neutron/neutron.conf')

print('\nconfig ml2.ini\n')
time.sleep(2)
os.system("ssh root@"+ip_compute+ " mv /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugins/ml2/ml2_conf.ini.org ")
os.system('cp /root/openstack/compute/ml2_conf.ini /root/openstack/compute/ml2_conf.ini.org')
os.system("scp /root/openstack/compute/ml2_conf.ini root@"+ip_compute+":/etc/neutron/plugins/ml2/")

print('\nopenvswitch.ini\n')
time.sleep(2)
os.system("ssh root@"+ip_compute+ " mv /etc/neutron/plugins/ml2/openvswitch_agent.ini /etc/neutron/plugins/ml2/openvswitch_agent.ini.org ")
os.system('cp /root/openstack/compute/openvswitch_agent.ini /root/openstack/compute/openvswitch_agent.ini.org')
os.system("scp /root/openstack/compute/openvswitch_agent.ini root@"+ip_compute+":/etc/neutron/plugins/ml2/")


subprocess.call(["sed","--in-place",r"s/\[DEFAULT]/\[DEFAULT]\nuse_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver\nvif_plugging_is_fatal = True\nvif_plugging_timeout = 300\n/g",com_nova_conf])


with open('/root/openstack/compute/nova.conf', 'a+') as nova:
    nova.write('''\n[neutron]\nauth_url = http://'''+ip_controller+''':5000
                \nauth_type = password
                \nproject_domain_name = default
                \nuser_domain_name = default
                \nregion_name = RegionOne
                \nproject_name = service
                \nusername = neutron
                \npassword = '''+pass_project_user+'''
                \nservice_metadata_proxy = True
                \nmetadata_proxy_shared_secret = metadata_secret''')
    nova.close()

os.system('scp  /root/openstack/compute/nova.conf root@'+ip_compute+':/etc/nova/')

os.system('ssh root@'+ip_compute+' ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini')
os.system('ssh root@'+ip_compute+' systemctl start openvswitch')
os.system('ssh root@'+ip_compute+' systemctl enable openvswitch')
os.system('ssh root@'+ip_compute+' ovs-vsctl add-br br-int')
os.system('ssh root@'+ip_compute+' systemctl restart openstack-nova-compute')
os.system('ssh root@'+ip_compute+' systemctl start neutron-openvswitch-agent')
os.system('ssh root@'+ip_compute+' systemctl enable neutron-openvswitch-agent ')


########################### Neutron Network (FLAT) #####################################################################

print('Neutron Network (FLAT)')
time.sleep(3)

##############################  Neutron Network (FLAT) controller ######################################################
os.system('ovs-vsctl add-br br-'+inf1)
os.system('ovs-vsctl add-port br-'+inf1+' '+inf1)

subprocess.call(["sed","--in-place",r"s/\#flat_networks = \*/flat_networks = physnet1/g",ml2_ini])

subprocess.call(["sed","--in-place",r"s/\#bridge_mappings =/bridge_mappings = physnet1:"+inf1+"/g",openvswitch_ini])

os.system('systemctl restart neutron-openvswitch-agent ')


print('\nNeutron Network (FLAT) controller \n')
time.sleep(2)
##############################  Neutron Network (FLAT) compute #########################################################

with open('/root/openstack/compute/infacer') as f1:
    inf_com = f1.read()
    inf_com=inf_com.split('\n')

os.system('ssh root@'+ip_compute+' ovs-vsctl add-br br-'+inf_com[1])
os.system('ssh root@'+ip_compute+' ovs-vsctl add-port br-'+inf_com[1]+' '+inf_com[1])

com_ml2_ini='/root/openstack/compute/ml2_conf.ini'
subprocess.call(["sed","--in-place",r"s/\#flat_networks = \*/flat_networks = physnet1/g",com_ml2_ini])

com_openvswitch_ini='/root/openstack/compute/openvswitch_agent.ini'
subprocess.call(["sed","--in-place",r"s/\#bridge_mappings =/bridge_mappings = physnet1:"+inf1+"/g",com_openvswitch_ini])

os.system('scp  /root/openstack/compute/ml2_conf.ini root@'+ip_compute+':/etc/neutron/plugins/ml2/')

os.system('scp  /root/openstack/compute/openvswitch_agent.ini root@'+ip_compute+':/etc/neutron/plugins/ml2/')

os.system('ssh root@'+ip_compute+' systemctl restart neutron-openvswitch-agent ')

print('\nNeutron Network (FLAT) compute\n')
time.sleep(2)
##############################  Neutron Network (VXLAN) controller #####################################################

print('\nNeutron Network (VXLAN) controller\n')

subprocess.call(["sed","--in-place",r"s/\#vni_ranges =/vni_ranges = 1:1000/g",ml2_ini])

subprocess.call(["sed","--in-place",r"s/\#tunnel_types =/tunnel_types = vxlan/g",openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#tunnel_types =/tunnel_types = vxlan/g",openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#l2_population = false/l2_population = True/g",openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#extensions =/\#extensions =\nprevent_arp_spoofing = True/g",openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#local_ip = <None>/\local_ip = "+ip_controller+"/g",openvswitch_ini])

os.system('systemctl restart neutron-server ')

os.system('for service in dhcp-agent l3-agent metadata-agent openvswitch-agent; do systemctl restart neutron-$service done')

print('\nNeutron Network (VXLAN) controller done\n')
time.sleep(2)
##############################  Neutron Network (VXLAN) compute ######################################################


subprocess.call(["sed","--in-place",r"s/\#flat_networks = \*/flat_networks = physnet1/g",com_ml2_ini])

subprocess.call(["sed","--in-place",r"s/\#vni_ranges =/vni_ranges = 1:1000/g",com_ml2_ini])

subprocess.call(["sed","--in-place",r"s/\#tunnel_types =/tunnel_types = vxlan/g",com_openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#l2_population = false/l2_population = True/g",com_openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#extensions =/\#extensions =\nprevent_arp_spoofing = True/g",com_openvswitch_ini])

subprocess.call(["sed","--in-place",r"s/\#local_ip = <None>/local_ip = "+ip_compute+"/g",com_openvswitch_ini])

os.system('ssh root@'+ip_compute+' systemctl restart neutron-openvswitch-agent')


print('\nNeutron Network (VXLAN) compute done')
time.sleep(2)
###################################### Create network #################################################################

print('\n Create router')
time.sleep(2)
os.system('source /root/keystonerc && openstack router create router1')

print('\n Create internal network')
time.sleep(2)
os.system('source /root/keystonerc && openstack network create internal --provider-network-type vxlan')

print('\n Create subet internal')
time.sleep(2)
os.system('source /root/keystonerc && openstack subnet create sub-inter --network internal --subnet-range '+vmnet+' --gateway '+vm_gw+' --dns-nameserver '+vm_dns)

print('\n add router to subet internal')
time.sleep(2)
os.system('source /root/keystonerc && openstack router add subnet router1 sub-inter')

print('\n Create network external')
time.sleep(2)
os.system('source /root/keystonerc && openstack network create --provider-physical-network physnet1 --provider-network-type flat --external external')

print('\n Create subnet external')
time.sleep(2)
os.system('source /root/keystonerc && openstack subnet create sub-exter --network external --subnet-range '+float_ip+' --allocation-pool start='+float_start+',end='+float_end+' --gateway ' +float_gw+' --dns-nameserver '+float_dns+' --no-dhcp')

print('\n add router to external')
time.sleep(2)
os.system('source /root/keystonerc && openstack router set router1 --external-gateway external')

time.sleep(2)
os.system("source /root/keystonerc && rbacID=$(openstack network rbac list | grep network | awk '{print $2}')")


print('\n show network rbac  ')
time.sleep(2)
os.system('source /root/keystonerc && openstack network rbac show $rbacID')

print('\n list network')
time.sleep(2)
os.system('source /root/keystonerc && openstack network list')

print('\n list  project')
time.sleep(2)
os.system('source /root/keystonerc && openstack project list')

print('\n network rbac create')
time.sleep(2)
os.system("source /root/keystonerc && netID=$(openstack network list | grep internal | awk '{ print $2 }')")
os.system("source /root/keystonerc && prjID=$(openstack project list | grep admin | awk '{ print $2 }')")
os.system("source /root/keystonerc && openstack network rbac create --target-project $prjID --type network --action access_as_shared $netID")

print('\n list flavor')
time.sleep(2)
os.system("source /root/keystonerc && openstack flavor list")

print('\n list network')
time.sleep(2)
os.system("source /root/keystonerc && openstack network list")

print('\n create groupsecurity')
time.sleep(2)
os.system("source /root/keystonerc && openstack security group create secgroup1")

print('\n Create private key')
time.sleep(2)
os.system("source /root/keystonerc && openstack keypair create --public-key /root/.ssh/id_rsa.pub mykey")



































