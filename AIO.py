#!/usr/bin/python3.6

import sys,os,time,fileinput,subprocess

print('Chuan bi cho qua trinh cai dat va cau hinh.\n'.upper())

print('\t\t\tcanh bao chu y phan network tranh nham lan'.upper())
time.sleep(3)

print('Mang mangager.')
time.sleep(3)

ip_controller = input('Nhap ip controller node: ')
print('\nDinh dang netmask: 8, 16, 24')
netmask = input('Nhap sunetmask: ')
gw = input('Nhap gateway: ')

user = 'admin'
pass_admin = input('\nNhap password admin: ')
rabbitmq_user = 'openstack'
pass_rabbitmq = input('Nhap password RabbitMQ: ')
rootsql = input('Nhap password root sql: ')
pass_user_sql = input('Nhap password user sql: ')
pass_project_user = input('Nhap password project user: ')

with open('/root/info','w+') as info:
    info.write('''Thong tin cau hinh.
                \nip controller: '''+ip_controller+'''
                \nrabbitmq_user: openstack
                \nPassword RabbitMQ: ''' +pass_rabbitmq+'''
                \npassword root sql :'''+rootsql+'''
                \nPassword user services: '''+pass_user_sql+'''
                \npassword project user: '''+pass_project_user+'''
                \nhttp://'''+ip_controller+'''/dashboard'''+'''
                \nDomain: default
                \nUser: admin
                \nPassword admin: '''+pass_admin)

    info.close()

print('\nCreate key ssh')

time.sleep(2)

os.system("ssh-keygen -q -t rsa -f ~/.ssh/id_rsa -N ''")

print('\nCreate key ssh done!!!')
time.sleep(2)

os.system('systemctl stop firewalld')
os.system('systemctl disable firewalld')

os.system(str("sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"))
os.system(str("sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"))

inf_ = os.popen('ls /sys/class/net/').read().split('\n')
#print(inf_)
time.sleep(3)
inf1 =inf_[1]

print('\nChuan bi hoan tat - bat dau cai dat va cau hinh'.upper())
time.sleep(3)

########################################################################################################

                                ####basic
def requirements ():
    #os.system('yum -y install centos-release-openstack-queens epel-release')
    os.system('curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | sudo bash')
    os.system('yum -y install MariaDB-server')

    server_conf = '/etc/my.cnf.d/server.cnf'
    subprocess.call(["sed", "--in-place", r"s/\[mysqld]/[mysqld]\ncharacter-set-server=utf8/g", server_conf])
    os.system('systemctl enable mariadb && systemctl start mariadb')


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

    ############################################################################################################
    print('Install and config rabbitmq, memcache')
    time.sleep(2)

    os.system('yum --enablerepo=epel -y install rabbitmq-server memcached')
    os.system("systemctl start rabbitmq-server memcached && systemctl enable rabbitmq-server memcached")

    os.system("rabbitmqctl add_user openstack " +pass_rabbitmq)
    os.system('rabbitmqctl set_permissions openstack ".*" ".*" ".*"')

    print('\nInstall and config rabbitmq, memcache done')
    time.sleep(2)

###################################### keytone ########################################################################

###### print("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"") ##### debug sql
def keytone():

    print('\nAdd a User and Database on MariaDB for Keystone')
    time.sleep(2)

    os.system("mysql -uroot -p"+rootsql+ " -e \"create database keystone;\"")
    os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'localhost' identified by"' \'' +pass_user_sql+'\''';\"')
    os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'%' identified by"' \'' +pass_user_sql+'\''';\"')
    os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

    print('Add a User and Database on MariaDB for Keystone done ')
    time.sleep(2)

    print("Install keytone")
    time.sleep(2)
    os.system("yum --enablerepo=centos-openstack-queens,epel -y install openstack-keystone openstack-utils python-openstackclient httpd mod_wsgi")


    print("\nConfig keytone")
    time.sleep(2)

    token_conf='/etc/keystone/keystone.conf'
    subprocess.call(["sed","--in-place",r"s/\#admin_token = <None>/admin_token = ADMIN/g",token_conf])
    subprocess.call(["sed","--in-place",r"s/\#memcache_servers = localhost:11211/memcache_servers = "+ip_controller+":11211/g",token_conf])
    subprocess.call(["sed","--in-place",r"s/\#connection = <None>/connection = mysql+pymysql:\/\/keystone:"+pass_user_sql+"@"+ip_controller+"\/keystone/g",token_conf])
    subprocess.call(['sed','--in-place',r's/\#provider = fernet/provider = fernet/g',token_conf])

    os.system('su -s /bin/bash keystone -c "keystone-manage db_sync"')
    os.system('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone')
    os.system('keystone-manage credential_setup --keystone-user keystone --keystone-group keystone')
    os.system("keystone-manage bootstrap --bootstrap-password "+pass_admin+" --bootstrap-admin-url http://"+ip_controller+":5000/v3/ --bootstrap-internal-url http://"+ip_controller+":5000/v3/ --bootstrap-public-url http://"+ip_controller+":5000/v3/ --bootstrap-region-id RegionOne")
    os.system("ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/")

    print("\nstart and enable httpd")
    time.sleep(2)
    os.system('systemctl enable httpd && systemctl start httpd')

    print('\nInstall Keystone done')
    time.sleep(2)

######################################################################################################################


    print('\nEnvironment variables file')

    time.sleep(2)

    with open("/root/keystonerc", 'w') as boot:
        boot.write('''export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=''' + pass_admin + '''
export OS_AUTH_URL=http://''' + ip_controller + ''':5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export PS1='[\\u@\h \W(keystone)]\$ ' ''')

    os.system('chmod 600 /root/keystonerc')
    os.system('source /root/keystonerc')

    os.system('chmod 600 /root/keystonerc')
    os.system('source /root/keystonerc')

    print('\nCreate Projects')

    time.sleep(2)

    os.system('source /root/keystonerc && openstack project create --domain default --description "Service Project" service ')

    print('\nconfirm settings')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack project list ')

#######################################################################################################################

def glance():
    print('\nAdd Glance keytone')
    time.sleep(2)

    print('\nadd glance user (set in service project)')
    time.sleep(2)
    os.system("source /root/keystonerc && openstack user create --domain default --project service --password " + pass_project_user + " glance")
    os.system("source /root/keystonerc && openstack role add --project service --user glance admin")

    print('\nadd service entry for glance')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack service create --name glance --description "OpenStack Image service" image')

    print('\nadd endpoint for glance (public)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image public http://' + ip_controller + ':9292')

    print('\nadd endpoint for glance (internal)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image internal http://' + ip_controller + ':9292')

    print('\nadd endpoint for glance (admin)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne image admin http://' + ip_controller + ':9292')

    ########################## Add a User and Database on MariaDB for Glance ###############################################

    print('\nCreate Glance database')
    time.sleep(2)

    os.system("mysql -uroot -p" + rootsql + " -e \"create database glance;\"")
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on glance.* to glance@'localhost' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on glance.* to glance@'%' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"flush privileges;\"")

    ############################### Install Glance #########################################################################
    print("\nInstall Glance")
    time.sleep(2)

    os.system("yum --enablerepo=centos-openstack-queens,epel -y install openstack-glance")

    ############################# config Glance ############################################################################
    print('\nGlance api config')
    time.sleep(2)
    os.system('mv /etc/glance/glance-api.conf /etc/glance/glance-api.conf.org ')
    os.system('cp /root/openstack/controller/glance-api.conf /etc/glance/')
    glance_api = '/etc/glance/glance-api.conf'

    subprocess.call(['sed', '--in-place', r's/pass_user_sql/' + pass_user_sql + '/g', glance_api])
    subprocess.call(['sed', '--in-place', r's/ip_controller/' + ip_controller + '/g', glance_api])
    subprocess.call(['sed', '--in-place', r's/pass_project_user/' + pass_project_user + '/g', glance_api])

    print('\nGlance registry config')
    time.sleep(2)
    os.system('mv /etc/glance/glance-registry.conf /etc/glance/glance-registry.conf.org ')
    os.system('cp /root/openstack/controller/glance-registry.conf /etc/glance/')
    glance_registry = '/etc/glance/glance-registry.conf'

    subprocess.call(['sed', '--in-place', r's/pass_user_sql/' + pass_user_sql + '/g', glance_registry])
    subprocess.call(['sed', '--in-place', r's/ip_controller/' + ip_controller + '/g', glance_registry])
    subprocess.call(['sed', '--in-place', r's/pass_project_user/' + pass_project_user + '/g', glance_registry])

    print('\nPhan quyen file Glance ')
    time.sleep(2)
    os.system('chmod 640 /etc/glance/glance-api.conf /etc/glance/glance-registry.conf ')
    os.system('chown root:glance /etc/glance/glance-api.conf /etc/glance/glance-registry.conf')
    os.system('su -s /bin/bash glance -c "glance-manage db_sync"')

    print('\nRestart servicer glance')
    time.sleep(2)
    os.system('systemctl start openstack-glance-api openstack-glance-registry ')
    os.system('systemctl enable openstack-glance-api openstack-glance-registry ')

#######################################################################################################################

def nova_Keystone():
    print('\nAdd nova user project')
    time.sleep(2)
    os.system("source /root/keystonerc && openstack user create --domain default --project service --password " + pass_project_user + " nova")
    os.system("source /root/keystonerc && openstack role add --project service --user nova admin")

    print('\nadd placement user project')
    time.sleep(2)
    os.system("source /root/keystonerc && openstack user create --domain default --project service --password " + pass_project_user + " placement")
    os.system("source /root/keystonerc && openstack role add --project service --user placement admin")

    print('\nadd service entry for nova')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack service create --name nova --description "OpenStack Compute service" compute')

    print('\nadd service entry for placement')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack service create --name placement --description "OpenStack Compute Placement service" placement')

    print('\nadd endpoint for nova (public)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute public http://' + ip_controller + ':8774/v2.1/%\(tenant_id\)s')

    print('\nadd endpoint for nova (internal)')
    time.sleep(2)
    os.system( 'source /root/keystonerc && openstack endpoint create --region RegionOne compute internal http://' + ip_controller + ':8774/v2.1/%\(tenant_id\)s')

    print('\nadd endpoint for nova (admin)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne compute admin http://' + ip_controller + ':8774/v2.1/%\(tenant_id\)s')

    print('\nadd endpoint for placement (public)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement public http://' + ip_controller + ':8778')

    print('\nadd endpoint for placement (internal)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement internal http://' + ip_controller + ':8778')

    print('\nadd endpoint for placement (admin)')
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne placement admin http://' + ip_controller + ':8778')

    print('\nCreate nova, nova_api, nova_placement, nova_cell0 database')
    time.sleep(2)

    os.system("mysql -uroot -p" + rootsql + " -e \"create database nova;\"")
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova.* to nova@'localhost' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova.* to nova@'%' identified by"' \'' + pass_user_sql + '\''';\"')

    os.system("mysql -uroot -p" + rootsql + " -e \"create database nova_api;\"")
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova_api.* to nova@'localhost' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova_api.* to nova@'%' identified by"' \'' + pass_user_sql + '\''';\"')

    os.system("mysql -uroot -p" + rootsql + " -e \"create database nova_placement;\"")
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova_placement.* to nova@'localhost' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova_placement.* to nova@'%' identified by"' \'' + pass_user_sql + '\''';\"')

    os.system("mysql -uroot -p" + rootsql + " -e \"create database nova_cell0;\"")
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova_cell0.* to nova@'localhost' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on nova_cell0.* to nova@'%' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"flush privileges;\"")
########################################################################################################################

def nova_install_conf():
    print('\nInstall Nova services\n')
    time.sleep(3)
    os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova')

    print('\nConfig nova')
    time.sleep(2)
    os.system('mv /etc/nova/nova.conf /etc/nova/nova.conf.org')
    os.system('cp /root/openstack/controller/nova.conf /etc/nova/')
    con_nova_conf = '/etc/nova/nova.conf'

    subprocess.call(['sed', '--in-place', r's/pass_rabbitmq/' + pass_rabbitmq + '/g', con_nova_conf])
    subprocess.call(['sed', '--in-place', r's/pass_user_sql/' + pass_user_sql + '/g', con_nova_conf])
    subprocess.call(['sed', '--in-place', r's/ip_controller/' + ip_controller + '/g', con_nova_conf])
    subprocess.call(['sed', '--in-place', r's/pass_project_user/' + pass_project_user + '/g', con_nova_conf])

    print('\nPhan quyen nova')
    time.sleep(2)
    os.system('chmod 640 /etc/nova/nova.conf')
    os.system('chgrp nova /etc/nova/nova.conf')

    os.system('cp -f /root/openstack/controller/00-nova-placement-api.conf /etc/httpd/conf.d/')

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
    os.system('source /root/keystonerc && nova-manage cell_v2 discover_hosts --verbose')

#######################################################################################################################

def nova_compute():
    print("\nInstall libvirt")
    time.sleep(2)
    os.system("yum -y install qemu-kvm libvirt virt-install")
    os.system('systemctl start libvirtd && systemctl enable libvirtd')

    print("\nInstall nova-compute")
    time.sleep(2)
    os.system("yum --enablerepo=centos-openstack-queens,epel -y install openstack-nova-compute")


    with open("/etc/nova/nova.conf",'a+') as nova:
        nova.write('''\n\n
[vnc]
enabled = True
server_listen = 0.0.0.0
server_proxyclient_address = '''+ip_controller+'''
novncproxy_base_url = http://'''+ip_controller+''':6080/vnc_auto.html\n\n''')

    os.system("systemctl start openstack-nova-compute && systemctl enable openstack-nova-compute")

    os.system('su -s /bin/bash nova -c "nova-manage cell_v2 discover_hosts"')
    os.system('source /root/keystonerc && openstack compute service list')

#######################################################################################################################

def neutron_Keystone():
    print('\nAdd user or service for Neutron on Keystone Server'.title())
    time.sleep(2)

    print('\nadd neutron user (set in service project)'.title())
    time.sleep(2)
    os.system('source /root/keystonerc && openstack user create --domain default --project service --password ' + pass_project_user + ' neutron')
    os.system('source /root/keystonerc && openstack role add --project service --user neutron admin')

    print('\nadd service entry for neutron'.title())
    time.sleep(2)
    os.system('source /root/keystonerc && openstack service create --name neutron --description "OpenStack Networking service" network')

    print('\nadd endpoint for neutron (public)'.title())
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network public http://' + ip_controller + ':9696')

    print('\nadd endpoint for neutron (internal)'.title())
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network internal http://' + ip_controller + ':9696')

    print('\nadd endpoint for neutron (admin)'.title())
    time.sleep(2)
    os.system('source /root/keystonerc && openstack endpoint create --region RegionOne network admin http://' + ip_controller + ':9696')

    print('Add a User and Database on MariaDB for Neutron'.title())
    time.sleep(2)
    os.system("mysql -uroot -p" + rootsql + " -e \"create database neutron_ml2;\"")
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on neutron_ml2.* to neutron@'localhost' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"grant all privileges on neutron_ml2.* to neutron@'%' identified by"' \'' + pass_user_sql + '\''';\"')
    os.system("mysql -uroot -p" + rootsql + " -e \"flush privileges;\"")


def neutron_server():
    print("\ninstall neutron")
    time.sleep(2)
    os.system("yum --enablerepo=centos-openstack-queens,epel -y install openstack-neutron openstack-neutron-ml2 openstack-neutron-openvswitch")

    print('Config neutron'.title())
    time.sleep(2)

    os.system('mv /etc/neutron/neutron.conf /etc/neutron/neutron.conf.org')
    os.system('cp /root/openstack/controller/neutron.conf /etc/neutron/')
    neutron = '/etc/neutron/neutron.conf'

    subprocess.call(['sed', '--in-place', r's/pass_rabbitmq/' + pass_rabbitmq + '/g', neutron])
    subprocess.call(['sed', '--in-place', r's/pass_user_sql/' + pass_user_sql + '/g', neutron])
    subprocess.call(['sed', '--in-place', r's/ip_controller/' + ip_controller + '/g', neutron])
    subprocess.call(['sed', '--in-place', r's/pass_project_user/' + pass_project_user + '/g', neutron])

    os.system('chmod 640 /etc/neutron/neutron.conf')
    os.system('chgrp neutron /etc/neutron/neutron.conf')

    l3_ini = '/etc/neutron/l3_agent.ini'
    subprocess.call(["sed", "--in-place", r"s/\#interface_driver = <None>/interface_driver = openvswitch/g", l3_ini])

    dhcp_ini = '/etc/neutron/dhcp_agent.ini'
    subprocess.call(["sed", "--in-place", r"s/\#interface_driver = <None>/interface_driver = openvswitch/g", dhcp_ini])
    subprocess.call(["sed", "--in-place",r"s/\#dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq/dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq/g",dhcp_ini])
    subprocess.call(["sed", "--in-place", r"s/\#enable_isolated_metadata = false/enable_isolated_metadata = true/g", dhcp_ini])

    metadata_ini = '/etc/neutron/metadata_agent.ini'
    subprocess.call(["sed", "--in-place", r"s/\#nova_metadata_host = 127.0.0.1/nova_metadata_host = " +ip_controller+ "/g",metadata_ini])
    subprocess.call(["sed", "--in-place", r"s/\#metadata_proxy_shared_secret =/metadata_proxy_shared_secret = metadata_secret/g",metadata_ini])
    subprocess.call(["sed", "--in-place",r"s/\#memcache_servers = localhost:11211/memcache_servers = " + ip_controller + ":11211/g",metadata_ini])

    ml2_ini = '/etc/neutron/plugins/ml2/ml2_conf.ini'
    subprocess.call(["sed", "--in-place",r"s/\#type_drivers = local,flat,vlan,gre,vxlan,geneve/type_drivers = flat,vlan,gre,vxlan/g",ml2_ini])
    subprocess.call(["sed", "--in-place", r"s/\#tenant_network_types = local/tenant_network_types = vxlan/g", ml2_ini])
    subprocess.call(["sed", "--in-place", r"s/\#mechanism_drivers =/mechanism_drivers = openvswitch,l2population/g", ml2_ini])
    subprocess.call(["sed", "--in-place", r"s/\#extension_drivers =/extension_drivers = port_security/g", ml2_ini])

    openvswitch_ini = '/etc/neutron/plugins/ml2/openvswitch_agent.ini'
    subprocess.call(["sed", "--in-place", r"s/\#firewall_driver = <None>/firewall_driver = openvswitch/g", openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#enable_security_group = true/enable_security_group = true/g", openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#enable_ipset = true/enable_ipset = true/g", openvswitch_ini])

    con_nova_conf = '/etc/nova/nova.conf'
    subprocess.call(["sed", "--in-place",r"s/\#neutron/\nuse_neutron = True\nlinuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\nfirewall_driver = nova.virt.firewall.NoopFirewallDriver\nvif_plugging_is_fatal = True\nvif_plugging_timeout = 300\n/g",con_nova_conf])

    with open('/etc/nova/nova.conf', 'a+') as nova:
        nova.write('''\n\n\n[neutron]
auth_url = http://''' + ip_controller + ''':5000
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = ''' + pass_project_user + '''
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata_secret''')
        nova.close()
    os.system('systemctl start openvswitch && systemctl enable openvswitch')

    os.system("ovs-vsctl add-br br-int")
    os.system("ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini")
    os.system('su -s /bin/bash neutron -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugin.ini upgrade head"')
    os.system('''for service in server dhcp-agent l3-agent metadata-agent openvswitch-agent; do
    systemctl start neutron-$service
    systemctl enable neutron-$service
    done''')

    os.system('systemctl restart openstack-nova-api openstack-nova-compute')

    os.system('openstack network agent list')

def horizon_install():
    print("\ninstall horizon")
    time.sleep(2)
    os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-dashboard')

    os.system('mv /etc/openstack-dashboard/local_settings /etc/openstack-dashboard/local_settings.org')
    os.system('cp /root/openstack/controller/local_settings /etc/openstack-dashboard/')

    dashboard = '/etc/openstack-dashboard/local_settings'
    subprocess.call(["sed", "--in-place",r"s/ALLOWED_HOSTS = \['horizon.example.com', 'localhost']/ALLOWED_HOSTS = ['" + ip_controller + "', 'localhost']/",dashboard])
    subprocess.call(["sed", "--in-place",r"s/\   	    'LOCATION': '192.168.100.10:11211',/\   	    'LOCATION': '" + ip_controller + ":11211',/g",dashboard])
    subprocess.call( ["sed", "--in-place", r"s/OPENSTACK_HOST = \"127.0.0.1\"/OPENSTACK_HOST = \"" + ip_controller + "\"/g",dashboard])

    dashboard_conf = '/etc/httpd/conf.d/openstack-dashboard.conf'
    subprocess.call(["sed", "--in-place",r"s/WSGISocketPrefix run\/wsgi/WSGISocketPrefix run\/wsgi\nWSGIApplicationGroup %{GLOBAL}/g",dashboard_conf])

    print('\nRestart httpd')
    time.sleep(2)
    os.system('systemctl restart httpd')

def config_vxlan_control():

    com_ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
    subprocess.call(["sed", "--in-place", r"s/\[ml2_type_vxlan]/\[ml2_type_vxlan]\nvni_ranges = 1:1000/g", com_ml2_ini])
    print("\nrestart neutron server")
    time.sleep(2)
    os.system('systemctl restart neutron-server')

def config_vxlan_network():

    os.system('ovs-vsctl add-br br-'+inf1)
    os.system('ovs-vsctl add-port br-'+inf1+' '+inf1)

    print('1')
    net_ml2_ini='/etc/neutron/plugins/ml2/ml2_conf.ini'
    subprocess.call(["sed", "--in-place", r"s/\#flat_networks = \*/flat_networks = physnet1/g", net_ml2_ini])
    subprocess.call(["sed", "--in-place", r"s/\[ml2_type_vxlan]/\[ml2_type_vxlan]\nvni_ranges = 1:1000/g", net_ml2_ini])

    net_openvswitch_ini='/etc/neutron/plugins/ml2/openvswitch_agent.ini'
    subprocess.call(["sed","--in-place",r"s/\#bridge_mappings =/bridge_mappings = physnet1:"+inf1+"/g",net_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#tunnel_types =/tunnel_types = vxlan/g", net_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#l2_population = false/l2_population = True/g", net_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#extensions =/\#extensions =\nprevent_arp_spoofing = True/g", net_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#local_ip = <None>/local_ip = " + ip_controller + "/g", net_openvswitch_ini])

    os.system('systemctl restart neutron-openvswitch-agent')

    os.system('''for service in dhcp-agent l3-agent metadata-agent openvswitch-agent; do
    systemctl restart neutron-$service
    done''')

def conf_vxlan_compute():
    com_openvswitch_ini='/etc/neutron/plugins/ml2/openvswitch_agent.ini'
    subprocess.call(["sed", "--in-place", r"s/\#tunnel_types =/tunnel_types = vxlan/g", com_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#l2_population = false/l2_population = True/g", com_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#extensions =/\#extensions =\nprevent_arp_spoofing = True/g", com_openvswitch_ini])
    subprocess.call(["sed", "--in-place", r"s/\#local_ip = <None>/local_ip = " + ip_controller + "/g", com_openvswitch_ini])
    os.system('systemctl restart neutron-openvswitch-agent')

def key_private():
    print('\n Create private key')
    time.sleep(2)
    os.system("source /root/keystonerc && openstack keypair create --public-key /root/.ssh/id_rsa.pub mykey")


n = ''
while n != 'q':
    print('\n+ {:-<6} + {:-^15} + '.format('', ''))
    print('| {:<20} | '.format('please enter your option'.title()))
    print('| {:<24} | '.format('[1]enter Install ALL IN ONE: '))
    print('| {:<25} '.format('[2]enter 2 Node Controll-Compute: '))
    print('| {:<25} '.format('[3]enter 3 Node Controll-Network-Compute: '))
    print('| {:<25} '.format('[4]enter 3 Node Controll-Compute-Storage: '))
    print('| {:<25} '.format('[q]enter q to exit: '))
    print('+ {:-<6} + {:-^15} + '.format('', ''))
    n = input('\nenter option: '.title())

    if n == '1':
        requirements()
        keytone()
        glance()
        nova_Keystone()
        nova_install_conf()
        nova_compute()
        neutron_Keystone()
        neutron_server()
        horizon_install()
        config_vxlan_control()
        config_vxlan_network()
        key_private()
    if n == '2':
        exit(0)
    if n == '3':
        exit(0)
    if n =='q':
        exit(0)

print('Install Openstack ALL IN ONE done.')

print("\nDashboard: http://"+ip_controller+"/dashboard\ndomain: default\nUser : admin\npassword: "+pass_admin)










