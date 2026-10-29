"""
modbusTcp 客户端读写寄存器 示例
"""

from pyModbusTCP.client import ModbusClient

"""
1.读取地址--15288  ， 0:无，1:准备，2:拍照 
2.写入地址--15289  ， 通讯状态 写入a(0,11) 
3.写入地址--15290  ， 拍照状态：  0:无， 1:准备就绪，2:拍照完成
4.写入地址--15291  ， 检测状态：  0:无， 1:合格， 2:NG

      15288为1时，15290也为1
"""


"""
modbusTcp通信，
连接服务端
"""

host = "192.168.2.1"  # ip
port = 509  # 端口

on_off = True  # 循环连接开关

# 创建Modbus TCP客户端并连接服务端
client = ModbusClient(host, port=port)

# 循环链接
while on_off:
    if client.open():
        print("成功连接到Modbus服务器")
        on_off = False

    else:
        print("无法连接到Modbus服务器--正在重连")
        client = ModbusClient(host, port=port)


"""
1.写入寄存器
"""
client.write_multiple_registers(0, [222])  # 从寄存器 15290 开始写, 写入的值是 1
# print(123)
# client.write_multiple_registers(0, [1])

"""
2.读取寄存器
"""
modbusTcp_result = client.read_holding_registers(0, 1)   # 从寄存器15288开始读，读1个寄存器
print(modbusTcp_result)


"""
3.读取寄存器的字符串（以字的方式读取，并解码为字符串）
"""
# if client.open():
#     # 读取寄存器中的数据，从地址15289开始，读取8个字(每个字符占一个字)
#     regs = client.read_holding_registers(15292, 8)
#
#     # 检查是否读取成功
#     if regs:
#         # 将16位字的数据解码为字符串
#         decoded_img_name = "".join([chr((reg & 0xFF00) >> 8) + chr(reg & 0xFF) for reg in reversed(regs)])
#         # 处理读取的字符串
#         img_name = decoded_img_name.strip('\x00')  # 去掉空字符的占位
#         print(img_name)
#
#     else:  # 没有读取成功
#         img_name = ""
#         print("无产品编号")

