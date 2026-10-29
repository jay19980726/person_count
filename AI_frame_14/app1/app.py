from ruamel.yaml import YAML
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from exe2 import Window




yaml = YAML()
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.load(file)
    return config




if __name__ == '__main__':

    # 读取yaml 信息
    my_yaml = load_config("arges.yaml")

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)
# try:
    app = QApplication(sys.argv)
    w = Window(my_yaml)
    # w.showFullScreen()
    w.show()
    # w.showMinimized()  # 最小化窗口
    app.exec_()

    # except Exception as e:
    #     print(e)
    #     logging.error(f"Exception occurred: {e}")

