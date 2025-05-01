from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QTableWidgetItem
from Libraries.Threading.ProgressBar import ProgressBar


# 处理线程
class BatchProcessor(QThread):
    progressBarCallback = pyqtSignal(int, str)
    finishedCallback = pyqtSignal()

    def __del__(self):
        self.work = False
        self.terminate()

    def __init__(self, objects, processor, title: str, finished_action=None):
        super().__init__()
        self.__progressBar = ProgressBar(len(objects), title, self)
        self.__progressBar.show()
        self.progressBarCallback.connect(self.__progressBar.update_search_progress)
        self.finishedCallback.connect(self.end)
        self.__objects = objects
        self.__processor = processor
        self.__finishAction = finished_action

    def run(self):
        index = 0
        success_count = 0
        for obj in self.__objects:
            index += 1
            text = ''
            if isinstance(obj, str):
                text = obj
            elif isinstance(obj, QTableWidgetItem):
                text = obj.text()
            elif isinstance(obj, dict) and 'name' in obj:
                text = obj['name']
            self.progressBarCallback.emit(index, text)
            if self.__processor(obj):
                success_count += 1
        self.finishedCallback.emit()

    def end(self):
        self.__progressBar.destroy()
        if self.__finishAction:
            self.__finishAction()


