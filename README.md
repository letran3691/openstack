

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







                

Sơ đồ LAB 2 **NODE CONTROLL - COMPUTE**

![image](https://user-images.githubusercontent.com/19284401/68357384-c48b7100-0147-11ea-982b-466588c19f58.png)
![image](https://user-images.githubusercontent.com/19284401/68357417-e127a900-0147-11ea-8e51-08d4e088fa41.png)



Sơ đồ LAB 3 **NODE CONTROLL - NETWORK - COMPUTE**

![image](https://user-images.githubusercontent.com/19284401/68357955-9444d200-0149-11ea-8263-a3cf6b3a442c.png)
![image](https://user-images.githubusercontent.com/19284401/68357824-2d271d80-0149-11ea-8503-2c37b434917f.png)


Sơ đồ LAB 3 **NODE CONTROLL - COMPUTE - STORAGE(backend LVM)**

![image](https://user-images.githubusercontent.com/19284401/68358148-382e7d80-014a-11ea-9727-21b773ad54ec.png)
