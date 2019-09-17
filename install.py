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
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_api.* to mova@'%' identified by"' \'' +pass_user_service+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_placement;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_placement.* to nova@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_placement.* to mova@'%' identified by"' \'' +pass_user_service+'\''';\"')

os.system("mysql -uroot -p"+rootsql+ " -e \"create database nova_cell0;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_cell0.* to nova@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on nova_cell0.* to mova@'%' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")























