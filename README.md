## MENU

### [I Giới thiệu](#I)

### [1 NODE (ALL IN ONE)](#II)

### [2 NODE (CONTROLL-COMPUTE)](#III)

### [3 NODE (CONTROLL-NETWORK-COMPUTE)](#IV)

### [3 NODE (CONTROLL-COMPUTE-STORAGE(LVM backend)))](#V)

### [3 NODE (CONTROLL-COMPUTE-STORAGE(NFS backend)))](#VI)

### [3 NODE (CONTROLL-COMPUTE-STORAGE(mutil backend))](#VII)



<a href="http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img" rel="nofollow">Cirros dowload.<a>

### <a name="II"><a/>1 NODE (ALL IN ONE)

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

### <a name="III"><a/> 2 NODE (CONTROLLER-COMPUTE)

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



### <a name="IV"><a/>3 NODE (CONTROLLER-NETWORK-COMPUTE)

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
- Link hướng dẫn tạo network và route trên dashboard 

[![Tạo network và route trên dashboard ](https://i9.ytimg.com/vi/LC-ddCl_MJY/mq2.jpg?sqp=CJyFnu4F&rs=AOn4CLArmxKzM28ugXAKXVIlpVvKO6vt-Q)](https://www.youtube.com/watch?v=LC-ddCl_MJY&feature=youtu.be)
            
            
### <a name="V"><a/>3 NODE (CONTROLLER-COMPUTE-STORACE(LVM backend))
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






### <a name="VI"><a/>3 NODE (CONTROLLER-COMPUTE-STORACE(NFS backend))
Sơ đồ LAB 3 **NODE CONTROLL - COMPUTE - STORAGE(NFS backend)**

UPDATING....

### <a name="VII"><a/>3 NODE (CONTROLLER-COMPUTE-STORACE(Multi backend))
Sơ đồ LAB 3 **NODE CONTROLL - COMPUTE - STORAGE(Multi backend)**

UPDATING....

