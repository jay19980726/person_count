from ruamel.yaml import YAML
import socket

# 实例化
yaml = YAML()
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.load(file)
    return config



my_yaml = load_config("arges.yaml")






"""
与VM进行tcp/ip通讯
"""



# client_socket, client_address,server_socket = None, None, None

def VM_socket():
    # global client_socket, client_address, server_socket
    # tcp ip 通讯
    if my_yaml["message"][0]:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((my_yaml["VM_tcpip"]["ip"], int(my_yaml["VM_tcpip"]["port"])))  # 绑定本地地址和端口
        server_socket.listen(1)  # 开始监听，最多允许一个连接

        print(f"等待VM客户端连接...")
        client_socket, client_address = server_socket.accept()  # 是一个阻塞方法，它会一直等待，直到有客户端尝试连接到服务端
        print(f"VM客户端已连接：{client_address}")
        return client_socket, client_address, server_socket



def VM_read(client_socket, client_address, server_socket, result_queue_VM):
    # # ---通讯防呆 自动重连
    # global client_socket,client_address,server_socket
    global data, start_r
    start_r = 1
    # count = 0
    while start_r:
    # while count<=5:
    # while start_counte_VM:
        try:
            print("读取VM测量信息----")
            # VM心跳
            client_socket.send("VM".encode("utf-8"))
            # 读取消息
            data = client_socket.recv(1024).decode()
            print("接收到VM尺寸测量信息：", data)
            # Add_Text(f"接收到VM尺寸测量信息： {data}")
            start_r = 0
            # start_counte_VM = False
        except Exception as e:
            print("与VM客户端链接出错：", e)
            client_socket, client_address = server_socket.accept()
            start_r = 1
            # continue

        try:
            # 发送给PLC
            # data = "1-4445;2-567;3-756;4-854;5-157;6-792"
            # cam_data = data.strip(" ").split(";")
            # 判断长度等于6
            if len(data) > 5 :
                # VM测量结果放入队列
                result_queue_VM.put(data)

                # cam_data1, cam_data2, cam_data3, cam_data4, cam_data5, cam_data6 = cam_data[0], cam_data[1], cam_data[2], cam_data[3], cam_data[4], cam_data[5]
                # PLC_client_socket.sendall(str(data).encode("utf-8"))

                # PLC_client_socket.send(str(cam_data1).encode("utf-8"))
                # PLC_client_socket.send(str(cam_data2).encode("utf-8"))
                # PLC_client_socket.send(str(cam_data3).encode("utf-8"))
                # PLC_client_socket.send(str(cam_data4).encode("utf-8"))
                # PLC_client_socket.send(str(cam_data5).encode("utf-8"))
                # PLC_client_socket.send(str(cam_data6).encode("utf-8"))
                print("VM测量信息放入队列成功")

            else:
                print("VM发送数据错误")

        except Exception as e:
            print("测量信息放入队列错误：", e)

            # continue



def VM_write(cam_name, client_socket, client_address, server_socket):
    # global client_socket,server_socket
    start_w = True
    while start_w:
        try:
            # VM心跳
            client_socket.sendall("VM".encode("utf-8"))

            # 触发VM拍照
            message_to_send = str(cam_name)
            # print(str(cam_name), type(str(cam_name)))
            client_socket.sendall(message_to_send.encode("utf-8"))
            start_w = False
            print("通讯发送", message_to_send)

        except Exception as e:
            print("VM_write 异常", e)
            client_socket, client_address = server_socket.accept()  # 是一个阻塞方法，它会一直等待，直到有客户端尝试连接到服务端
            # break




# # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
def sum_data_VM_AI(result_queue_VM, result_queue1, result_queue2, result_queue3, result_queue4,result_queue5,result_queue6):
    # 1.AI---f'{cam_name}-0-0-3-0000-0000-0000-{str(max_w2)}-{str(max_h2)}-000'
    # 序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间
    # 队列第一个
    print("开始分割AI数据")
    AI1 = result_queue1.get()
    AI1_list = AI1.strip("").split("-")  # [cam_name,0,0,3,0000,0000,0000,str(max_w2),str(max_h2),000]
    # 队列第二个
    AI2 = result_queue2.get()
    AI2_list = AI2.strip("").split("-")  # [cam_name,0,0,3,0000,0000,0000,str(max_w2),str(max_h2),000]
    # 队列第三个
    AI3 = result_queue3.get()
    AI3_list = AI3.strip("").split("-")  # [cam_name,0,0,3,0000,0000,0000,str(max_w2),str(max_h2),000]
    # 队列第四个
    AI4 = result_queue4.get()
    AI4_list = AI4.strip("").split("-")  # [cam_name,0,0,3,0000,0000,0000,str(max_w2),str(max_h2),000]
    # 队列第五个
    AI5 = result_queue5.get()
    AI5_list = AI5.strip("").split("-")  # [cam_name,0,0,3,0000,0000,0000,str(max_w2),str(max_h2),000]
    # 队列第6个
    AI6 = result_queue6.get()
    AI6_list = AI6.strip("").split("-")  # [cam_name,0,0,3,0000,0000,0000,str(max_w2),str(max_h2),000]

    # 2.VM---0-4445;0-567;0-756;0-854;0-157;0-792
    VM1_6 = result_queue_VM.get()
    VM_list = VM1_6.strip("").split(";")  # [0-4445,0-567,0-756,0-854,0-157,0-792]
    print("AI队列整合完毕")


    "数据要求：序号-检测完成-检测结果-不良类型-测量尺寸-缺陷长-缺陷宽-裂纹长-裂纹宽-检测时间"
    # 1.整合第1个 检测结果; 0:不良;1∶良品----- 不良类型(0:良品;1∶尺寸;2:凹陷;3:製痕,4;无球，5:缺陷全有
        # 良品
    if VM_list[0][0] == "1" and AI1_list[2] == "1":
        number1 = f"{AI1_list[0]}-1-1-0-{VM_list[0][2:]}-{AI1_list[5]}-{AI1_list[6]}-{AI1_list[7]}-{AI1_list[8]}-{AI1_list[9]}"
        # VM无缺陷，AI有缺陷
    elif VM_list[0][0] == "1" and AI1_list[2] != "1":
        number1 = f"{AI1_list[0]}-1-0-{AI1_list[3]}-{VM_list[0][2:]}-{AI1_list[5]}-{AI1_list[6]}-{AI1_list[7]}-{AI1_list[8]}-{AI1_list[9]}"
        # VM有缺陷，AI无缺陷
    elif VM_list[0][0] != "1" and AI1_list[2] == "1":
        number1 = f"{AI1_list[0]}-1-0-1-{VM_list[0][2:]}-{AI1_list[5]}-{AI1_list[6]}-{AI1_list[7]}-{AI1_list[8]}-{AI1_list[9]}"
        # 都有缺陷
    elif VM_list[0][0] != "1" and AI1_list[2] != "1" and AI1_list[3] != "4":
        number1 = f"{AI1_list[0]}-1-0-5-{VM_list[0][2:]}-{AI1_list[5]}-{AI1_list[6]}-{AI1_list[7]}-{AI1_list[8]}-{AI1_list[9]}"
    # 无球
    elif AI1_list[3] == "4":
        number1 = f"{AI1_list[0]}-1-0-4-0000-0000-0000-0000-0000-{AI1_list[9]}"
    else:
        number1 = f"{AI1_list[0]}-1-0-6-0000-0000-0000-0000-0000-{AI1_list[9]}"
    print("第一个球队列整合完毕")


    # 2.整合第2个 结果; 0:不良;1∶良品
        # 良品
    if VM_list[1][0] == "1" and AI2_list[2] == "1":
        number2 = f"{AI2_list[0]}-1-1-0-{VM_list[1][2:]}-{AI2_list[5]}-{AI2_list[6]}-{AI2_list[7]}-{AI2_list[8]}-{AI2_list[9]}"
        # VM无缺陷，AI有缺陷
    elif VM_list[1][0] == "1" and AI2_list[2] != "1":
        number2 = f"{AI2_list[0]}-1-0-{AI2_list[3]}-{VM_list[1][2:]}-{AI2_list[5]}-{AI2_list[6]}-{AI2_list[7]}-{AI2_list[8]}-{AI2_list[9]}"
        # VM有缺陷，AI无缺陷
    elif VM_list[1][0] != "1" and AI2_list[2] == "1":
        number2 = f"{AI2_list[0]}-1-0-1-{VM_list[1][2:]}-{AI2_list[5]}-{AI2_list[6]}-{AI2_list[7]}-{AI2_list[8]}-{AI2_list[9]}"
        # 缺陷类型；所有缺陷都有
    elif VM_list[1][0] != "1" and AI2_list[2] != "1" and AI2_list[3] != "4":
        number2 = f"{AI2_list[0]}-1-0-5-{VM_list[1][2:]}-{AI2_list[5]}-{AI2_list[6]}-{AI2_list[7]}-{AI2_list[8]}-{AI2_list[9]}"
    # 无球
    elif AI2_list[3] == "4":
        number2 = f"{AI2_list[0]}-1-0-4-0000-0000-0000-0000-0000-{AI2_list[9]}"
    else:
        number2 = f"{AI2_list[0]}-1-0-6-0000-0000-0000-0000-0000-{AI2_list[9]}"
    print("第二个球队列整合完毕")



    # 3.整合第3个 结果; 0:不良;1∶良品
    if VM_list[2][0] == "1" and AI3_list[2] == "1":   # 良品
        number3 = f"{AI3_list[0]}-1-1-0-{VM_list[2][2:]}-{AI3_list[5]}-{AI3_list[6]}-{AI3_list[7]}-{AI3_list[8]}-{AI3_list[9]}"
        # VM无缺陷，AI有缺陷
    elif VM_list[2][0] == "1" and AI3_list[2] != "1":
        number3 = f"{AI3_list[0]}-1-0-{AI3_list[3]}-{VM_list[2][2:]}-{AI3_list[5]}-{AI3_list[6]}-{AI3_list[7]}-{AI3_list[8]}-{AI3_list[9]}"
        # VM有缺陷，AI无缺陷v
    elif VM_list[2][0] != "1" and AI3_list[2] == "1":
        number3 = f"{AI3_list[0]}-1-0-1-{VM_list[2][2:]}-{AI3_list[5]}-{AI3_list[6]}-{AI3_list[7]}-{AI3_list[8]}-{AI3_list[9]}"
    # 缺陷类型；所有缺陷都有
    elif VM_list[2][0] != "1" and AI3_list[2] != "1" and AI3_list[3] != "4":
        number3 = f"{AI3_list[0]}-1-0-5-{VM_list[2][2:]}-{AI3_list[5]}-{AI3_list[6]}-{AI3_list[7]}-{AI3_list[8]}-{AI3_list[9]}"
    # 无球
    elif AI3_list[3] == "4":
        number3 = f"{AI3_list[0]}-1-0-4-0000-0000-0000-0000-0000-{AI3_list[9]}"
    else:
        number3 = f"{AI3_list[0]}-1-0-6-0000-0000-0000-0000-0000-{AI3_list[9]}"
    print("第三个球队列整合完毕")


    # 4.整合第4个 结果; 0:不良;1∶良品
        # 良品
    if VM_list[3][0] == "1" and AI4_list[2] == "1":
        number4 = f"{AI4_list[0]}-1-1-0-{VM_list[3][2:]}-{AI4_list[5]}-{AI4_list[6]}-{AI4_list[7]}-{AI4_list[8]}-{AI4_list[9]}"
        # VM无缺陷，AI有缺陷
    elif VM_list[3][0] == "1" and AI4_list[2] != "1":
        number4 = f"{AI4_list[0]}-1-0-{AI4_list[3]}-{VM_list[3][2:]}-{AI4_list[5]}-{AI4_list[6]}-{AI4_list[7]}-{AI4_list[8]}-{AI4_list[9]}"
        # VM有缺陷，AI无缺陷
    elif VM_list[3][0] != "1" and AI4_list[2] == "1":
        number4 = f"{AI4_list[0]}-1-0-1-{VM_list[3][2:]}-{AI4_list[5]}-{AI4_list[6]}-{AI4_list[7]}-{AI4_list[8]}-{AI4_list[9]}"
        # 缺陷类型；所有缺陷都有
    elif VM_list[3][0] != "1" and AI4_list[2] != "1" and AI4_list[3] != "4":
        number4 = f"{AI4_list[0]}-1-0-5-{VM_list[3][2:]}-{AI4_list[5]}-{AI4_list[6]}-{AI4_list[7]}-{AI4_list[8]}-{AI4_list[9]}"
    # 无球
    elif AI4_list[3] == "4":
        number4 = f"{AI4_list[0]}-1-0-4-0000-0000-0000-0000-0000-{AI4_list[9]}"
    else:
        number4 = f"{AI4_list[0]}-1-0-6-0000-0000-0000-0000-0000-{AI4_list[9]}"
    print("第四个球队列整合完毕")


    # 5.整合第5个 结果; 0:不良;1∶良品
    if VM_list[4][0] == "1" and AI5_list[2] == "1":   # 良品
        number5 = f"{AI5_list[0]}-1-1-0-{VM_list[4][2:]}-{AI5_list[5]}-{AI5_list[6]}-{AI5_list[7]}-{AI5_list[8]}-{AI5_list[9]}"
        # VM无缺陷，AI有缺陷
    elif VM_list[4][0] == "1" and AI5_list[2] != "1":
        number5 = f"{AI5_list[0]}-1-0-{AI5_list[3]}-{VM_list[4][2:]}-{AI5_list[5]}-{AI5_list[6]}-{AI5_list[7]}-{AI5_list[8]}-{AI5_list[9]}"
        # VM有缺陷，AI无缺陷
    elif VM_list[4][0] != "1" and AI5_list[2] == "1":
        number5 = f"{AI5_list[0]}-1-0-1-{VM_list[4][2:]}-{AI5_list[5]}-{AI5_list[6]}-{AI5_list[7]}-{AI5_list[8]}-{AI5_list[9]}"
        # 缺陷类型；所有缺陷都有
    elif VM_list[4][0] != "1" and AI5_list[2] != "1" and AI5_list[3] != "4":
        number5 = f"{AI5_list[0]}-1-0-5-{VM_list[4][2:]}-{AI5_list[5]}-{AI5_list[6]}-{AI5_list[7]}-{AI5_list[8]}-{AI5_list[9]}"
    # 无球
    elif AI5_list[3] == "4":
        number5 = f"{AI5_list[0]}-1-0-4-0000-0000-0000-0000-0000-{AI5_list[9]}"
    else:
        number5 = f"{AI5_list[0]}-1-0-6-0000-0000-0000-0000-0000-{AI5_list[9]}"
    print("第五个球队列整合完毕")



    # 6.整合第6个 结果; 0:不良;1∶良品
    if VM_list[5][0] == "1" and AI6_list[2] == "1":   # 良品
        number6 = f"{AI6_list[0]}-1-1-0-{VM_list[5][2:]}-{AI6_list[5]}-{AI6_list[6]}-{AI6_list[7]}-{AI6_list[8]}-{AI6_list[9]}"
        # VM无缺陷，AI有缺陷
    elif VM_list[5][0] == "1" and AI6_list[2] != "1":
        number6 = f"{AI6_list[0]}-1-0-{AI6_list[3]}-{VM_list[5][2:]}-{AI6_list[5]}-{AI6_list[6]}-{AI6_list[7]}-{AI6_list[8]}-{AI6_list[9]}"
        # VM有缺陷，AI无缺陷
    elif VM_list[5][0] != "1" and AI6_list[2] == "1":
        number6 = f"{AI6_list[0]}-1-0-1-{VM_list[5][2:]}-{AI6_list[5]}-{AI6_list[6]}-{AI6_list[7]}-{AI6_list[8]}-{AI6_list[9]}"
        # 缺陷类型；所有缺陷都有
    elif VM_list[5][0] != "1" and AI6_list[2] != "1" and AI6_list[3] != "4":
        number6 = f"{AI6_list[0]}-1-0-5-{VM_list[5][2:]}-{AI6_list[5]}-{AI6_list[6]}-{AI6_list[7]}-{AI6_list[8]}-{AI6_list[9]}"
    # 无球
    elif AI6_list[3] == "4":
        number6 = f"{AI6_list[0]}-1-0-4-0000-0000-0000-0000-0000-{AI6_list[9]}"
    else:
        number6 = f"{AI6_list[0]}-1-0-6-0000-0000-0000-0000-0000-{AI6_list[9]}"
    print("第六个球队列整合完毕")


    # 6个结果合并
    data6 = f"{number1};{number2};{number3};{number4};{number5};{number6}"
    return data6