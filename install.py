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

print('create key ssh')

time.sleep(2)

os.system('''ssh-keygen <<EOF


          EOF''')



os.system('systemctl stop firewalld')
os.system('systemctl disable firewalld')

os.system(str("sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config"))
os.system(str("sed -i 's/SELINUX=permissive/SELINUX=disabled/g' /etc/selinux/config"))

########################################################################################################################

#os.system('yum -y install centos-release-openstack-queens epel-release python36 python36-devel python36-setuptools ')
#os.system('sed -i -e "s/enabled=1/enabled=0/g" /etc/yum.repos.d/CentOS-OpenStack-queens.repo ')

# install Mariadb
#os.system('yum --enablerepo=centos-openstack-queens -y install mariadb-server')

##############################    COPY PRIVATE KEY   ###################################################################

os.system('ssh-copy-id -i /root/.ssh/id_rsa.pub root@'+ip_compute)
os.system('ssh-copy-id -i /root/.ssh/id_rsa.pub root@'+ip_stogare)

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


################################# 	Install RabbitMQ, Memcached ########################################################

print('Install RabbitMQ, Memcached')

time.sleep(2)

os.system('yum --enablerepo=epel -y install rabbitmq-server memcached')
os.system('systemctl start rabbitmq-server memcached')
os.system('systemctl enable rabbitmq-server memcached')

os.system('rabbitmqctl add_user '+memcache_user +' '+ pass_memcache)
os.system('rabbitmqctl set_permissions '+memcache_user+' ".*" ".*" ".*"')

###### print("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"") ##### debug sql

######################### Add a User and Database on MariaDB for Keystone ##############################################

print('Add a User and Database on MariaDB for Keystone')

time.sleep(2)

os.system("mysql -uroot -p"+rootsql+ " -e \"create database keystone;\"")
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'localhost' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"grant all privileges on keystone.* to keystone@'%' identified by"' \'' +pass_user_service+'\''';\"')
os.system("mysql -uroot -p"+rootsql+ " -e \"flush privileges;\"")

########################## 	Install Keystone ###########################################################################

print('Install Keystone')

time.sleep(2)

os.system('yum --enablerepo=centos-openstack-queens,epel -y install openstack-keystone openstack-utils python-openstackclient httpd mod_wsgi')

#os.system("sed -i 's/\[mysqld]/[mysqld]\ncharacter-set-server=utf8/1' /etc/my.cnf.d/server.cnf")

os.system(str("sed -i 's/memcache_servers =/ "+ip_controller+":11211/1' /etc/keystone/keystone.conf"))
os.system(str("sed -i 's/connection =/ mysql+pymysql://keystone:password@"+ip_controller+"/keystone/1' /etc/keystone/keystone.conf"))
os.system(str("sed -i 's/\[token]/[token]\nprovider = fernet/1' /etc/keystone/keystone.conf"))
os.system('su -s /bin/bash keystone -c "keystone-manage db_sync"')
os.system('keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone')
os.system('keystone-manage credential_setup --keystone-user keystone --keystone-group keystone')

os.system('keystone-manage bootstrap --bootstrap-password '+pass_admin+' \
bootstrap-admin-url http://'+ip_controller+':5000/v3/ \
bootstrap-internal-url http://'+ip_controller+':5000/v3/ \
bootstrap-public-url http://'+ip_controller+':5000/v3/  \
bootstrap-region-id RegionOne')

os.system('ln -s /usr/share/keystone/wsgi-keystone.conf /etc/httpd/conf.d/')
os.system('systemctl start httpd')
os.system('systemctl enable httpd')

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
os.system('echo "source /root/keystonerc " >> /root/.bash_profile')

############################## Create Projects #########################################################################

print('Create Projects')

time.sleep(2)

os.system('openstack project create --domain default --description "Service Project" service ')
os.system('openstack project list ')


































