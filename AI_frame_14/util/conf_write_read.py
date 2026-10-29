"""
# 保存参数文件
"""
import os
from app2.config import *



def write_conf(arges):

    try:
        folder_path =  conf_agrs_path["root"]    # 路径
        # if not os.path.exists(folder_path):
        #     os.makedirs(folder_path)
        #     print(f"Folder '{folder_path}' created successfully.")
        # else:
        #     print(f"Folder '{folder_path}' already exists.")

        with open(folder_path, "w+") as write_file:   # 写入
            write_file.write(f"{arges}")
            print(folder_path, "参数写入成功")

    except Exception as e:
        print(e)




"""
# 读取参数文件
"""
def read_conf():

    try:
        folder_path = conf_agrs_path["root"]
        if not os.path.exists(folder_path):
            print(f"{folder_path}文件不存在！,参数读取失败。")
            return 0.5   # 默认0.5

        else:
            print(f"{folder_path}文件读取成功！正在加载参数。")

            with open(folder_path, "r") as read_file:   # 读取
                value = read_file.readline()
                # max, min = value.strip().split(",")
                print(f"参数加载成功: conf--{value}")
                return value

    except Exception as e:
        print(e)







def write_WH(arges):
    try:

        folder_path = WH_agrs_path["root"]   # 路径
        # if not os.path.exists(folder_path):
        #     os.makedirs(folder_path)
        #     print(f"Folder '{folder_path}' created successfully.")
        # else:
        #     print(f"Folder '{folder_path}' already exists.")

        with open(folder_path, "w+") as write_file:   # 写入
            write_file.write(f"{arges}")
            print(folder_path, "参数写入成功")

    except Exception as e:
        print(e)


def read_WH():

    try:
        folder_path = WH_agrs_path["root"]
        if not os.path.exists(folder_path):
            print(f"{folder_path}文件不存在！,参数读取失败。")
            return 0, 0  # 默认0
        else:
            print(f"{folder_path}文件读取成功！正在加载参数。")

            with open(folder_path, "r") as read_file:   # 读取
                value = read_file.readline()
                W, H = value.strip().split(",")
                print(f"参数加载成功: 长--{W}, 宽--{H}")
                return W, H

    except Exception as e:
        print(e)




import json
def load_from_file():
    config_file_path = time_params_path["root"]
    """从 JSON 文件读取保存的值，文件不存在返回空列表"""
    if not os.path.exists(config_file_path):
        return [10,10,10,10,10,10,10]
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("time_values", [])
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return [10,10,10,10,10,10,10]


if __name__ == '__main__':
    pass
    # a = load_from_file()
    # print(a)