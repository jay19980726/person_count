import socket




def start_server(ip_address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 绑定服务器地址和端口
        server_socket.bind((ip_address, port))

        # 监听连接，允许最多一个客户端排队等待
        server_socket.listen(1)
        print(f"服务器正在监听 {ip_address}:{port} ...")

        # 等待客户端连接
        client_socket, client_address = server_socket.accept()
        print(f"连接来自 {client_address}")

        # 发送消息给客户端
        message_to_send = "Hello, client!"
        client_socket.sendall(message_to_send.encode())

        # 接收客户端发送的消息
        data = client_socket.recv(1024)
        print("客户端消息:", data.decode())

        # 关闭连接
        client_socket.close()

if __name__ == "__main__":
    server_ip_address = "127.0.0.1"
    server_port = 12345

    # 启动服务器
    start_server(server_ip_address, server_port)
