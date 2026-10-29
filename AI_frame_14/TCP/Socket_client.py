
import socket
from app2.config import *

"""
连接TCP服务端
"""
def client_VM():
    host = tcp['ip']  # ip
    port = tcp['port']  # 端口
    connet = True
    while connet:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, port))
            print("连接PLC客户端成功!")
            connet = False
            return client

        except Exception as e:
            print("链接PLC服务的出错,尝试重连：", e)
                # continue
                # return client


if __name__ == "__main__":
    pass
