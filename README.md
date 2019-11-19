## MENU

### [I: GIỚI THIỆU](#I)

### [II: INSTALL AND CONFIG](#2.1)

- #### [1 NODE (ALL IN ONE)](#2.1)

- #### [2 NODE (CONTROLL-COMPUTE)](#2.2)

- #### [3 NODE (CONTROLL-NETWORK-COMPUTE)](#2.3)

- #### [3 NODE (CONTROLL-COMPUTE-STORAGE(LVM backend)))](#2.4)

- #### [3 NODE (CONTROLL-COMPUTE-STORAGE(NFS backend)))](#2.5)

- #### [3 NODE (CONTROLL-COMPUTE-STORAGE(mutil backend))](#2.6)

### [III: BASIC COMMAND](#III)

### [IV: WEB GUID ](#IV)

### [V: Hỗ trợ ](#V)


### <a name="I"><a/>**I GIỚI THIỆU**

- Là một IT  chắc các bạn cũng đã nghe qua các cum từ Ảo Hóa (Virtualization) và Điện toán đám mây (Cloud Computing). Vậy Ảo Hóa là gì, điện toán đám mây là gì.
 
- Ảo hóa (Virtualization) 

    - Đa số khi nói đến Virtualization thì mọi người đều hiểu là Ảo hóa. Ảo hóa là kỹ thuật tạo ra phần cứng, thiết bị  mạng, thiết bị lưu trữ,… ảo – không có thật (cũng có thể là giả lập hoặc mô phỏng).
    
    - Đi kèm với Ảo hóa thường có các cụm từ Hardware Virtualization, Platform Virtualization: các cụm từ này ám chỉ việc tạo ra các thành phần phần cứng (ảo) để tạo ra các máy ảo (Virtual Machine), chúng gần như có đầy đủ các thành phần như máy vật lý (physical machine ) và có thể cài đặt hệ điều hành (Linux, Windows,….) trong network thì có thể có các Router ảo và Switch ảo.
    
- Cloud Computing

    -  Điện toán đám mây (Cloud Computing) theo định nghĩa của IBM là việc cung cấp các tài nguyên máy tính cho người dùng tùy theo mục đích sử dụng thông qua kết nối Internet. Nguồn tài nguyên đó có thể là bất kì thứ gì liên quan đến điện toán và máy tính, ví dụ như phần mềm, phần cứng, hạ tầng mạng cho đến các máy chủ và mạng lưới máy chủ cỡ lớn.
    
- Openstack là gì.

    - OpenStack là một phần mềm mã nguồn mở, dùng để triển khai Cloud Computing, bao gồm private cloud và public cloud (nhiều tài liệu giới thiệu là Cloud Operating System). Đúng như với thông tin từ trang chủ http://openstack.org, xin được trích lại như sau:  Open source software for building private and public clouds.
    
    - Các thành phần chính (Openstack Queens):
    
        - Identity Service(Keystone): Quản lý xác thực cho user và projects.
        - Compute Service(Nova): Quản lý máy ảo
        - Image Service(Glance): Là OpenStack Image Service, quản lý các disk image ảo. Glance hỗ trợ các ảnh Raw, Hyper-V (VHD), VirtualBox (VDI), Qemu (qcow2) và VMWare (VMDK, OVF). Bạn có thể thực hiện: cập nhật thêm các virtual disk images, cấu hình các public và private image và điều khiển việc truy cập vào chúng, và tất nhiên là có thể tạo và xóa chúng.
        - Dashboard(Horizon): Cung cấp cho người quản trị cũng như người dùng giao diện đồ họa để truy cập, cung cấp và tự động tài nguyên cloud. Việc thiết kế có thể mở rộng giúp dễ dàng thêm vào các sản phẩm cũng như dịch vụ ngoài như billing, monitoring và các công cụ giám sát khác.
        - Object Storage(Swift): Là nền tảng lưu trữ mạnh mẽ, có khả năng mở rộng và chịu lỗi cao, được thiết kế để lưu trữ một lượng lớn dữ liệu phi cấu trúc với chi phí thấp thông qua một http RESTful API.
        - Block Storage(Cinder): Cung cấp dịch vụ Block Storage. Một cách ngắn gọn, Cinder thực hiện ảo hóa pool các khối thiết bị lưu trữ và cung cấp cho người dùng cuối API để request và sử dụng tài nguyên mà không cần biết khối lưu trữ của họ thực sự lưu trữ ở đâu và loại thiết bị là gì. Cũng như các dịch vụ khác trong OpenStack, self service API được sử dụng để tương tác với dịch vụ Cinder.
        - Network Service(Neutron): Là thành phần quản lý network cho các máy ảo. Cung cấp chức năng network as a service. Đây là hệ thống có các tính chất pluggable, scalable và API-driven.
        - Orchestration Service(Heat): Cung cấp chức năng điều phối cho máy ảo
        - Metering Service(Ceilometer): Cung cấp cở sở hạ tầng để thu thập mọi thông tin cần thiết liên quan tới OpenStack
        - Database Service(Trove):Là dịch vụ cho phép người dùng sử dụng database quan hệ hoặc phi quan hệ (Relational database và Non-Relational database - NoSQL) mà không cần quan tâm tới hạ tầng database. Nó tạo ra lớp abstract giữa người dùng và database, thực hiện dự phòng, mở rộng và quản lý database trên hạ tầng OpenStack.   
        - ....
        




<a href="http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img" rel="nofollow">Cirros dowload.<a>

### <a name="2.1"><a/>**1 NODE (ALL IN ONE)**

sơ đồ và cấu hình **1 node ALL IN ONE**

![image](https://user-images.githubusercontent.com/19284401/68357223-2d261e00-0147-11ea-8808-174a5afdbf37.png)
![image](https://user-images.githubusercontent.com/19284401/68355669-8b043700-0142-11ea-9155-5350234b3497.png)

- Cài đặt git
            
            yum  -y install git
             
- Clone git

            git clone https://github.com/letran3691/openstack.git             

- Phân quyền file 
            
            chmod +x openstack/ops.sh
            
- Thực thi file

            ./openstack/ops.sh
            
            
- Chọn 1 để cài 1 NODE ALL IN ONE.

![image](https://user-images.githubusercontent.com/19284401/68368404-93706800-016a-11ea-8588-77a5daad291d.png)

- Sau khi chọn 1 bạn sẽ được yêu cầu nhập các thông tin như hình trên. Sau khi nhập xong nhân **ENTER**. Quá trình cài đặt và cấu hình bắt đầu.

![image](https://user-images.githubusercontent.com/19284401/68359637-2c918580-014f-11ea-8f6a-59c020eb2279.png)

- Từ lúc bắt đầu cài đặt, đến lúc cài đặt và cấu hình xong thì ko cần phải làm gì nữa. Chỉ cần ngồi đợi thôi.
- Quá trình cài đặt và cấu hình nhanh hay chạm tùy thuộc vào cầu hình VM của các bạn. Nếu trong quá trình cài đặt và cấu hình bị lỗi, thì sẽ hiện luôn ở màn hình.

- Màn hình xuất hiên WARNING như hình dưới thì cứ kệ nhé.

![image](https://user-images.githubusercontent.com/19284401/68359784-e7218800-014f-11ea-9650-0cf0749a145a.png)

- **restart service nova** khá là lâu các bạn nhé NODE ALL IN ONE của mình 6G RAM mà mất khoảng 10 phút mới restart xong.

- Sau khi Cài đặt và cấu hình xong, ở cuối màn hình sẽ hiện ra link dashboard và thông tin đăng nhập, đồng th NODE sẽ tự động reboot

![image](https://user-images.githubusercontent.com/19284401/68359950-a5451180-0150-11ea-9c87-4d526d10b899.png)

- Ngoài ra tránh trường hợp bị rớt nào ở chỗ nào đó thì trong /root/ có 1 file info. File này lưu lại toàn bộ các thông liên quan đến user, password mà các bạn đã đặt.

![image](https://user-images.githubusercontent.com/19284401/68360701-a4fa4580-0153-11ea-86f3-65bc55997947.png)

- 1 vài hình ảnh về GUI WEB

![image](https://user-images.githubusercontent.com/19284401/68360778-eab70e00-0153-11ea-908b-059ce43982bf.png)

- Tạo network private cho instance

![image](https://user-images.githubusercontent.com/19284401/68360993-b42dc300-0154-11ea-9012-ddab32f5eda5.png)

- Tạo Provider network (Associate floating ip)

![image](https://user-images.githubusercontent.com/19284401/68361166-6feef280-0155-11ea-869b-be7197212d62.png)

- Tạo route

![image](https://user-images.githubusercontent.com/19284401/68393856-6b4f2c00-019f-11ea-92ff-d348d4b3c8fe.png)

- Ad interface cho route

![image](https://user-images.githubusercontent.com/19284401/68395867-24633580-01a3-11ea-8405-ce4b55c13a8c.png)
![image](https://user-images.githubusercontent.com/19284401/68396124-96d41580-01a3-11ea-8423-9a0a847e4923.png)


- Tạo instance và test public connect
![image](https://user-images.githubusercontent.com/19284401/68396415-1cf05c00-01a4-11ea-826f-90f5ded37fa2.png)
![image](https://user-images.githubusercontent.com/19284401/68396385-106c0380-01a4-11ea-998b-5ffb35a4f4c6.png)
![image](https://user-images.githubusercontent.com/19284401/68396544-4f01be00-01a4-11ea-9fc5-33f3e74813f5.png)

- Như vậy là xong OPENSTACK ALL IN ONE

### <a name="2.2"><a/> **2 NODE (CONTROLLER-COMPUTE)**

**Sơ đồ LAB 2 **NODE CONTROLL - COMPUTE****

![image](https://user-images.githubusercontent.com/19284401/68357384-c48b7100-0147-11ea-982b-466588c19f58.png)
![image](https://user-images.githubusercontent.com/19284401/68357417-e127a900-0147-11ea-8e51-08d4e088fa41.png)

- Cài đặt git
            
            yum  -y install git
             
- Clone git

            git clone https://github.com/letran3691/openstack.git             

- Phân quyền file 
            
            chmod +x openstack/ops.sh
            
- Thực thi file

            ./openstack/ops.sh
            
            
- Chọn 2 để cài  **2 NODE CONTROLL - COMPUTE****

![3](https://user-images.githubusercontent.com/19284401/68399477-0993bf80-01a9-11ea-9738-3cf3e7ab0da9.JPG)

- Nhập các thông tin yêu cầu như hình trên thì nhấn ENTER.

**_- Chú ý: Nó yêu cầu nhập password root  bên node compute thì nhớ nhập để copy key ssh nhé_**

- Sau khi điền đầu đủ các thông tin trên nhấn ENTER thì lại ngồi chơi đợi quá trình cài đặt và cấu hình hoàn tất thôi. :D

- Thấy cảnh báo như dưới đây thì bỏ qua, không cần quan tâm.

![image](https://user-images.githubusercontent.com/19284401/68399766-7d35cc80-01a9-11ea-8d42-fc45233a0035.png)

- Restart nova service sẽ khá lâu nhé.

![image](https://user-images.githubusercontent.com/19284401/68400069-ff25f580-01a9-11ea-8482-ba70da0db446.png)
![image](https://user-images.githubusercontent.com/19284401/68402599-2e3e6600-01ae-11ea-8609-b5b717e47f75.png)



### <a name="2.3"><a/>**3 NODE (CONTROLLER-NETWORK-COMPUTE)**

Sơ đồ LAB 3 **NODE CONTROLL-NETWORK-COMPUTE**

![image](https://user-images.githubusercontent.com/19284401/68357955-9444d200-0149-11ea-8263-a3cf6b3a442c.png)
![image](https://user-images.githubusercontent.com/19284401/68357824-2d271d80-0149-11ea-8503-2c37b434917f.png)

- Cài đặt git
            
            yum  -y install git
             
- Clone git

            git clone https://github.com/letran3691/openstack.git             

- Phân quyền file 
            
            chmod +x openstack/ops.sh
            
- Thực thi file

            ./openstack/ops.sh

![3](https://user-images.githubusercontent.com/19284401/68479994-44a7f880-0266-11ea-8322-88f0d0a58820.JPG)

- Nhập các thông tin yêu cầu như hình trên thì nhấn ENTER.

**_- Chú ý: Nó yêu cầu nhập password root  bên node compute và network thì nhớ nhập để copy key ssh nhé_**

- Sau khi điền đầu đủ các thông tin trên nhấn ENTER thì lại ngồi chơi đợi quá trình cài đặt và cấu hình hoàn tất thôi. :D

- Thấy cảnh báo như dưới đây thì bỏ qua, không cần quan tâm.

![image](https://user-images.githubusercontent.com/19284401/68399766-7d35cc80-01a9-11ea-8d42-fc45233a0035.png)
![image](https://user-images.githubusercontent.com/19284401/68400069-ff25f580-01a9-11ea-8482-ba70da0db446.png)
![image](https://user-images.githubusercontent.com/19284401/68402599-2e3e6600-01ae-11ea-8609-b5b717e47f75.png)
![image](https://user-images.githubusercontent.com/19284401/68482476-4379ca00-026c-11ea-865b-2a23b8b7aaf5.png)

- Cài đặt và cấu hình xong  **3 NODE CONTROLL-NETWORK-COMPUTE**

<!--
title: dashboard 3 NODE CONTROLL-NETWORK-COMPUTE
author: Trunglv
-->
- Link hướng dẫn tạo network và route trên dashboard (click vào ảnh phía dưới).

[![Tạo network và route trên dashboard ](https://user-images.githubusercontent.com/19284401/68360778-eab70e00-0153-11ea-908b-059ce43982bf.png)](https://www.youtube.com/watch?v=LC-ddCl_MJY)
            
            
### <a name="2.4"><a/>**3 NODE (CONTROLLER-COMPUTE-STORACE(LVM backend))**
Sơ đồ LAB 3 **NODE CONTROLL - COMPUTE - STORAGE(LVM backend)**

![image](https://user-images.githubusercontent.com/19284401/68358148-382e7d80-014a-11ea-9727-21b773ad54ec.png)
![3](https://user-images.githubusercontent.com/19284401/68538423-ab343000-03a6-11ea-8952-0194a90a9736.JPG)

- Cài đặt git
            
            yum  -y install git
             
- Clone git

            git clone https://github.com/letran3691/openstack.git             

- Phân quyền file 
            
            chmod +x openstack/ops.sh
            
- Thực thi file

            ./openstack/ops.sh

![image](https://user-images.githubusercontent.com/19284401/68592600-0dd01d80-04c6-11ea-8558-4f393902b4f4.png)

- Nhập các thông tin yêu cầu như hình trên thì nhấn ENTER.

**_- Chú ý: Nó yêu cầu nhập password root  bên node storage và compute thì nhớ nhập để copy key ssh nhé_**

- Sau khi điền đầu đủ các thông tin trên nhấn ENTER thì lại ngồi chơi đợi quá trình cài đặt và cấu hình hoàn tất thôi. :D

- Thấy cảnh báo như dưới đây thì bỏ qua, không cần quan tâm.

![image](https://user-images.githubusercontent.com/19284401/68399766-7d35cc80-01a9-11ea-8d42-fc45233a0035.png)
![image](https://user-images.githubusercontent.com/19284401/68402599-2e3e6600-01ae-11ea-8609-b5b717e47f75.png)


### <a name="2.5"><a/>**3 NODE (CONTROLLER-COMPUTE-STORACE(NFS backend))**

_**CHÚ Ý: RAM CỦA BẠN NÀO HƠN 12G THÌ HÃY THỰC HIỆN LAB NÀY**_

![image](https://user-images.githubusercontent.com/19284401/68775821-ae0e7980-0661-11ea-8b6a-9d299e21f8f0.png)

Sơ đồ LAB 3 **NODE CONTROLL - COMPUTE - STORAGE(NFS backend)**

![image](https://user-images.githubusercontent.com/19284401/68823125-746f5a00-06c5-11ea-863d-4125074a7085.png)

![3](https://user-images.githubusercontent.com/19284401/68772916-33dbf600-065d-11ea-9a2c-f1857c1a8156.JPG)


- Cài đặt git
            
            yum  -y install git
             
- Clone git

            git clone https://github.com/letran3691/openstack.git             

- Phân quyền file 
            
            chmod +x openstack/ops.sh
            
- Thực thi file

            ./openstack/ops.sh


![Untitled-1](https://user-images.githubusercontent.com/19284401/68774590-ead97100-065f-11ea-8137-cb213ac6fce3.png)

- Nhập các thông tin yêu cầu như hình trên thì nhấn ENTER.

**_- Chú ý: Nó yêu cầu nhập password root  bên node storage và compute và NFS server thì nhớ nhập để copy key ssh nhé_**

- Sau khi điền đầu đủ các thông tin trên nhấn ENTER thì lại ngồi chơi đợi quá trình cài đặt và cấu hình hoàn tất thôi. :D

- Thấy cảnh báo như dưới đây thì bỏ qua, không cần quan tâm.

![image](https://user-images.githubusercontent.com/19284401/68399766-7d35cc80-01a9-11ea-8d42-fc45233a0035.png)

![image](https://user-images.githubusercontent.com/19284401/68776466-b1563500-0662-11ea-816a-14d4d604a781.png)
![image](https://user-images.githubusercontent.com/19284401/68402599-2e3e6600-01ae-11ea-8609-b5b717e47f75.png)

- Mình tạo 2 instance:
    
    - 1 là volume mặc định của instance mấy vài phút, là instance tạo xong.
    - Instance thứ 2 tạo volume từ NFS rất lâu mới tạo xong (21 phút) có thể có do cấu hình LAB đuối quá, nên tọa lâu. Nhưng instance vậy hoạt động ngon lành.

- Một vài hình ảnh về storage NFS backend.

![image](https://user-images.githubusercontent.com/19284401/68952449-73881680-07f2-11ea-8550-ca58f545cdbd.png)
![image](https://user-images.githubusercontent.com/19284401/68953443-7d127e00-07f4-11ea-8f06-f134be005608.png)


### <a name="2.6"><a/>**3 NODE (CONTROLLER-COMPUTE-STORACE(Multi backend))**

_**CHÚ Ý: RAM CỦA BẠN NÀO HƠN 12G THÌ HÃY THỰC HIỆN LAB NÀY**_

![image](https://user-images.githubusercontent.com/19284401/68775821-ae0e7980-0661-11ea-8b6a-9d299e21f8f0.png)

Sơ đồ LAB 3 **NODE CONTROLL - COMPUTE - STORAGE(Multi backend)**

![image](https://user-images.githubusercontent.com/19284401/68823250-c912d500-06c5-11ea-8020-762ffd33abe3.png)
![3](https://user-images.githubusercontent.com/19284401/68993001-72fc8800-08a5-11ea-9c8a-5b225d2b53e0.jpg)

- Cài đặt git
            
            yum  -y install git
             
- Clone git

            git clone https://github.com/letran3691/openstack.git             

- Phân quyền file 
            
            chmod +x openstack/ops.sh
            
- Thực thi file

            ./openstack/ops.sh


![image](https://user-images.githubusercontent.com/19284401/69115294-a06e4f00-0aba-11ea-9263-e1ed0e2ace1f.png)


- Nhập các thông tin yêu cầu như hình trên thì nhấn ENTER.

**_- Chú ý: Nó yêu cầu nhập password root  bên node storage và compute và NFS server thì nhớ nhập để copy key ssh nhé_**

- Sau khi điền đầu đủ các thông tin trên nhấn ENTER thì lại ngồi chơi đợi quá trình cài đặt và cấu hình hoàn tất thôi. :D

- Thấy cảnh báo như dưới đây thì bỏ qua, không cần quan tâm.

![image](https://user-images.githubusercontent.com/19284401/68399766-7d35cc80-01a9-11ea-8d42-fc45233a0035.png)

![image](https://user-images.githubusercontent.com/19284401/68776466-b1563500-0662-11ea-816a-14d4d604a781.png)
![image](https://user-images.githubusercontent.com/19284401/68402599-2e3e6600-01ae-11ea-8609-b5b717e47f75.png)



### <a name="III"><a/>**III: BASIC COMMAND**

- Create project
            
            openstack project create --domain default --description "demo Project" demo
- Show project 

            openstack project list 
- download disk image

            wget http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img -O /var/lib/glance/images/cirros.img
- Add virtual image to glance

             openstack image create "cirros" --file /var/lib/glance/images/cirros.img --disk-format qcow2 --container-format bare --public
- Show virtual image

            openstack image list
- Create user

            openstack user create --domain default --project demo --password 12345 demo     
- Show user 

            openstack user list 
- Create role

            openstack role create demo
- Add user to role

            openstack role add --project demo --user demo  demo
- Add flavor
            
            openstack flavor create --id 0 --vcpus 1 --ram 512 --disk 10 test
- Show flavor

            openstack flavor list
- Create virtual router

            openstack router create router01    
- Show router

             openstack router list   
- Create internal network

            openstack network create internal --provider-network-type vxlan 
- Create subnet in internal network

            openstack subnet create sub-inter --network internal --subnet-range 10.0.0.0/24 --gateway 10.0.0.1 --dns-nameserver 8.8.8.8
- Create external network
    
            openstack network create --provider-physical-network physnet1 --provider-network-type flat --external external
- Create subnet in external network

            openstack subnet create sub-exter --network external --subnet-range 192.168.124.0/24 --allocation-pool start=192.168.124.200,end=192.168.124.254 --gateway 192.168.124.2 --dns-nameserver 8.8.8.8 --no-dhcp
    - Chú ý: Kiểm tra kĩ lại network sao cho subnet trùng với lớp mạng trên **ADAPTER2**   
    
- Create rbac    

            openstack network rbac create --target-project admin --type network --action access_as_shared internal    
- Show network

            openstack network list    
- Set internal network to router
            
            openstack router add subnet router01 sub-inter                                                            
- Set gateway to the router

            openstack router set router01 --external-gateway external
- Create a security group for instances

            openstack security group create secgroup01
- Show security group

             openstack security group list            
            
- Create key ssh to instance
            
            ssh-keygen -q -N ""                   
- Add public key

            openstack keypair create --public-key ~/.ssh/id_rsa.pub mykey           
- Create instance

            openstack server create --flavor test --image cirros --security-group secgroup01 --network internal --key-name mykey cirros_test
            
- Assign floating IP to Instance    

            openstack floating ip create external 
- Add floating ip to

 ![image](https://user-images.githubusercontent.com/19284401/69009997-4459dc80-098d-11ea-8310-aaf152174db5.png)
 
   - **_Chú ý cái ip nhé_**

            openstack server add floating ip  cirros_test 192.168.124.215
- Comfirm setting

            openstack floating ip show 192.168.124.215
- Show instance

            openstack server list
            
- Add rorulele to security group

    - permit ICMP

            openstack security group rule create --protocol icmp --ingress secgroup01
            
    permit SSH
    
            openstack security group rule create --protocol tcp --dst-port 22:22 secgroup01
            
- Show rule security group
    
            openstack security group rule list  
- Volume            
    
    - **_Chú ý: chỉ up dụng với LAB có cấu hình Storage node_**                
                
    - Create volume
    
                 openstack volume create --size 6 disk01
    - Show volume
    
                openstack volume list
    - Add volume to instace
    
                openstack server add volume  cirros_test disk01 
                
     ![image](https://user-images.githubusercontent.com/19284401/69010552-766e3d00-0993-11ea-9382-a0fb8ea172d5.png)
           
                       
- ssh to instance

            ssh cirros@192.168.124.215                                                
                                

### <a name="IV"><a/>**IV: WEB GUID**
<!--
title: Dashboard 
author: Trunglv
-->
- Link hướng dẫn trên dashboard (click vào ảnh phía dưới).

[![Hướng dẫn trên dashboard ](https://user-images.githubusercontent.com/19284401/68360778-eab70e00-0153-11ea-908b-059ce43982bf.png)](https://youtu.be/D597lhzCmkc)


### <a name="V"><a/>**V: HỖ TRỢ**
#### Liên hệ: <a href="https://www.facebook.com/trunglv.91" rel="nofollow">Facebook<a>.