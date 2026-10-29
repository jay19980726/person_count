import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication
)

from main import MainWindow
from util.auto_remove_Imgfile import *




# # AUTO image-file
# auto_remove_OK(max_file=10, file="cam1")
# auto_remove_NG(max_file=10, file="cam1")
# auto_remove_OK(max_file=10, file="cam2")
# auto_remove_NG(max_file=10, file="cam2")
# auto_remove_OK(max_file=10, file="cam3")
# auto_remove_NG(max_file=10, file="cam3")
# auto_remove_OK(max_file=10, file="cam4")
# auto_remove_NG(max_file=10, file="cam4")


#
#save_img(f"cam{cam_index}", img1)
auto_remove(5, "cam0")
auto_remove(5, "cam1")
auto_remove(5, "cam2")
auto_remove(5, "cam3")
auto_remove(5, "cam4")
auto_remove(5, "cam5")
auto_remove(5, "cam6")
auto_remove(5, "cam7")





if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    font = QFont("Microsoft YaHei", 7)
    app.setFont(font)

    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())





