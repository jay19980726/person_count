# import time
#
# from app2.config import *
# from pyModbusTCP.client import ModbusClient
#
#
#
# def mod_bus_tcp():
#
#     host = tcp['ip']  # ip
#     port = tcp['port']  # 端口
#
#     on_off = True  # 循环连接开关
#
#     # 创建Modbus TCP客户端并连接服务端
#     client = ModbusClient(host, port=port)
#
#     # 循环链接
#     while on_off:
#         if client.open():
#             print("成功连接到Modbus服务器")
#             on_off = False
#             return client
#
#         else:
#             print("无法连接到Modbus服务器--正在重连")
#             client = ModbusClient(host, port=port)
#             time.sleep(2)
#
#
#
# #
# # def mod_bus_tcp2():
# #
# #     host = modbus_tcp['ip']  # ip
# #     port = 501  # 端口
# #
# #     on_off = True  # 循环连接开关
# #
# #     # 创建Modbus TCP客户端并连接服务端
# #     client = ModbusClient(host, port=port)
# #
# #     # 循环链接
# #     while on_off:
# #         if client.open():
# #             print("成功连接到Modbus服务器")
# #             on_off = False
# #             return client
# #
# #         else:
# #             print("无法连接到Modbus服务器--正在重连")
# #             client = ModbusClient(host, port=port)
# #             time.sleep(2)
#
#
#
#
# # def modbus_heartbeat(client, running):
# #     data = 1
# #     while running:
# #         try:
# #
# #             if data == 1:
# #                 client.write_multiple_registers(1, [data])
# #                 data = 2
# #             else:
# #                 client.write_multiple_registers(1, [data])
# #                 data = 1
# #
# #         except Exception as e:
# #             print("心跳异常：", e)
# #             host = modbus_tcp['ip']  # ip
# #             port = modbus_tcp['port']  # 端口
# #             # 创建Modbus TCP客户端并连接服务端
# #             client = ModbusClient(host, port=port)


