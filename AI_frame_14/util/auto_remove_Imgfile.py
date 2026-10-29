import os
import shutil

from app2.config import save_images


def auto_remove_NG(max_file=None, file=None):   # max_file:文件夹最大数量， file：要删除的子文件夹目录
    try:
        # 设置父文件夹的路径
        parent_folder = save_images["root"] + "\\" +file + "\\NG"

        # 设置子文件夹的最大数量
        max_subfolder_count = max_file  # 修改为你需要的数量

        # 获取父文件夹下的所有子文件夹
        subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]

        # 如果子文件夹数量超过最大数量，删除旧的子文件夹
        if len(subfolders) > max_subfolder_count:
            # 对子文件夹按创建时间进行排序
            subfolders.sort(key=lambda x: os.path.getctime(os.path.join(parent_folder, x)))

            # 计算需要删除的子文件夹数量
            subfolders_to_delete = len(subfolders) - max_subfolder_count

            # 删除最旧的子文件夹
            for i in range(subfolders_to_delete):
                folder_to_delete = os.path.join(parent_folder, subfolders[i])
                shutil.rmtree(folder_to_delete)
                print(f"Deleted folder: {folder_to_delete}")

        print("Process completed.")
    except Exception as e:
        print("删除NG文件夹出错：", e)
        return





def auto_remove_OK(max_file=None, file=None):   # max_file:文件夹最大数量， file：要删除的子文件夹目录
    try:
        # 设置父文件夹的路径
        parent_folder = save_images["root"] + "\\" + file + "\\OK"

        # 设置子文件夹的最大数量
        max_subfolder_count = max_file  # 修改为你需要的数量

        # 获取父文件夹下的所有子文件夹
        subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]

        # 如果子文件夹数量超过最大数量，删除旧的子文件夹
        if len(subfolders) > max_subfolder_count:
            # 对子文件夹按创建时间进行排序
            subfolders.sort(key=lambda x: os.path.getctime(os.path.join(parent_folder, x)))

            # 计算需要删除的子文件夹数量
            subfolders_to_delete = len(subfolders) - max_subfolder_count

            # 删除最旧的子文件夹
            for i in range(subfolders_to_delete):
                folder_to_delete = os.path.join(parent_folder, subfolders[i])
                shutil.rmtree(folder_to_delete)
                print(f"Deleted folder: {folder_to_delete}")

        print("Process completed.")
    except Exception as e:
        print("删除OK文件夹出错：", e)
        return





def auto_remove(max_file=None, file=None):   # max_file:文件夹最大数量， file：要删除的子文件夹目录
    try:
        # 设置父文件夹的路径
        parent_folder = r"D:/img_data/" + file

        # 设置子文件夹的最大数量
        max_subfolder_count = max_file  # 修改为你需要的数量

        # 获取父文件夹下的所有子文件夹
        subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]

        # 如果子文件夹数量超过最大数量，删除旧的子文件夹
        if len(subfolders) > max_subfolder_count:
            # 对子文件夹按创建时间进行排序
            subfolders.sort(key=lambda x: os.path.getctime(os.path.join(parent_folder, x)))

            # 计算需要删除的子文件夹数量
            subfolders_to_delete = len(subfolders) - max_subfolder_count

            # 删除最旧的子文件夹
            for i in range(subfolders_to_delete):
                folder_to_delete = os.path.join(parent_folder, subfolders[i])
                shutil.rmtree(folder_to_delete)
                print(f"Deleted folder: {folder_to_delete}")

        print("Process completed.")

    except Exception as e:
        print("删除文件夹出错：", e)
        return




if __name__ == '__main__':
    pass
    # a = auto_remove(0,"cam1")