import os
import sys
import traceback
import clipboard
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from QtDesign.MainWindow_ui import Ui_MainWindow
from ObjectTools import RenameTools
from Libraries.Threading.BatchProcessor import BatchProcessor
from Libraries import FileTools


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.currentFolder = ''

    def setup_triggers(self):
        self.tblActiveObjects.itemClicked.connect(self.copy_object_path)
        self.tblActiveObjects.itemDoubleClicked.connect(self.open_item)
        self.btnOpenFolder.clicked.connect(self.load_folder)
        self.btnGoParentFolder.clicked.connect(self.go_up_directory)

    # 更新底部状态栏文字
    def update_status_bar(self, text: str):
        self.statusbar.showMessage(text)
        self.activateWindow()

    # 打开文件夹
    def load_folder(self):
        self.update_current_folder(FileTools.open_folder())

    # 更新当前文件夹
    def update_current_folder(self, new_folder):
        if not new_folder:
            return
        self.currentFolder = new_folder
        self.lblCurrentFolder.setText(f'当前文件夹为{self.currentFolder}')
        self.fill_table()

    # 返回上层文件夹
    def go_up_directory(self):
        self.update_current_folder(os.path.dirname(self.currentFolder))

    # 填充表格
    def fill_table(self):
        self.tblActiveObjects.setRowCount(0)
        BatchProcessor(os.listdir(self.currentFolder), self.process_item, f'正在读取{self.currentFolder}', self.on_read_folder_finished).start()

    # 处理文件夹中每一个对象
    def process_item(self, obj_name):
        full_path = os.path.join(self.currentFolder, obj_name)
        if not os.path.exists(full_path):
            return
        row_count = self.tblActiveObjects.rowCount()
        self.tblActiveObjects.insertRow(row_count)
        self.tblActiveObjects.setItem(row_count, 0, QTableWidgetItem(obj_name))
        # 文件或文件夹大小
        info = FileTools.get_file_info(full_path)
        size_item = QTableWidgetItem(info['size_str'])
        size_item.setData(Qt.ItemDataRole.InitialSortOrderRole, info['raw_size'])
        self.tblActiveObjects.setItem(row_count, 1, QTableWidgetItem(info['type']))
        self.tblActiveObjects.setItem(row_count, 2, size_item)
        # 详细信息
        self.tblActiveObjects.setItem(row_count, 3, QTableWidgetItem(info['detail']))

    # 读取文件夹完毕
    def on_read_folder_finished(self):
        self.tblActiveObjects.resizeColumnsToContents()

    # 打开文件或进入下级文件夹
    def open_item(self, item: QTableWidgetItem):
        row = item.row()
        child_path = os.path.join(self.currentFolder, self.tblActiveObjects.item(row, 0).text())
        if os.path.isdir(child_path):
            self.update_current_folder(child_path)
        else:
            os.startfile(child_path)


    # 复制文件路径
    def copy_object_path(self, item: QTableWidgetItem):
        if item.column() != 0:
            item = self.tblActiveObjects.item(item.row(), 0)
        full_path = os.path.join(self.currentFolder, item.text())
        clipboard.copy(full_path)


sys.excepthook = traceback.print_exception

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
