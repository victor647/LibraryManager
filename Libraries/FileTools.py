import os
import re
import json
import csv
import shutil
import xml.etree.ElementTree as ElementTree
from PyQt6.QtWidgets import QFileDialog

# 打开文件夹
def open_folder():
    folder_path = QFileDialog.getExistingDirectory()
    return folder_path

# 从json文件导入
def import_from_json():
    file_path = QFileDialog.getOpenFileName(filter='JSON(*.json)')
    if file_path[0] == '':
        return None
    file = open(file_path[0], 'r')
    return json.load(file)


# 导出到json文件
def export_to_json(json_obj, file_name: str):
    file_path = QFileDialog.getSaveFileName(filter='JSON(*.json)', directory=file_name)
    if file_path[0] == '':
        return
    file = open(file_path[0], 'w')
    file.write(json.dumps(json_obj, indent=2))


# 导出二维数组到csv文件
def export_to_csv(data: list, file_name: str):
    file_path = QFileDialog.getSaveFileName(filter='CSV(*.csv)', directory=file_name)
    if file_path[0] == '':
        return
    file = open(file_path[0], mode='w', newline='')
    writer = csv.writer(file)
    writer.writerows(data)


# 从csv文件导入
def import_from_csv():
    file_path = QFileDialog.getOpenFileName(filter='CSV(*.csv)')
    if file_path[0] == '':
        return None
    file = open(file_path[0], 'r')
    return list(csv.reader(file))


# 从xml或WorkUnit文件导入
def import_from_xml(extension='xml'):
    file_path = QFileDialog.getOpenFileName(filter=f'XML(*.{extension})')
    if file_path[0] == '':
        return None, None
    tree = ElementTree.parse(file_path[0])
    root = tree.getroot()
    return root, file_path[0]


# 移动文件
def move_file(old_path, new_path):
    if not os.path.exists(old_path):
        return
    folder = os.path.dirname(new_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    shutil.move(old_path, new_path)
    print(f'Moved file from {old_path} to {new_path}')


# 判断文件类型
def get_file_type(file_name: str):
    if '.' not in file_name:
        return '文件夹'
    file_name = file_name.lower()
    if re.match(r'.*\.(mp3|wav|ogg|aif)$', file_name):
        return '音频'
    if re.match(r'.*\.(mp4|mov|avi|mpeg)$', file_name):
        return '视频'
    if re.match(r'.*\.(jpg|png|bmp|gif)$', file_name):
        return '图片'
    if re.match(r'.*\.(nef|dng|cr2|cr3)$', file_name):
        return 'RAW照片'
    if re.match(r'.*\.(txt|json|xml)$', file_name):
        return '文本'
    if re.match(r'.*\.(dll|exe|bat)$', file_name):
        return '程序'
    if re.match(r'.*\.(py|cs|h|cpp|lua|js)$', file_name):
        return '代码'
    return '其他'

# 计算文件大小，返回带单位的字符串
def get_file_size(path: str):
    if os.path.isdir(path):
        raw_size, file_count = get_dir_size(path)
    else:
        raw_size = round(os.path.getsize(path) / 1024, 3)
        file_count = 0
    unit = 'KB'
    if raw_size > 1024:
        size = raw_size / 1024
        unit = 'MB'
        if size > 1024:
            size /= 1024
            unit = 'GB'
    else:
        size = raw_size
    return raw_size, f'{round(size, 2)}{unit}', file_count


# 计算文件夹大小
def get_dir_size(root_dir: str):
    total_size = 0
    file_count = 0
    try:
        for obj_name in os.listdir(root_dir):
            full_path = os.path.join(root_dir, obj_name)
            if os.path.isfile(full_path):
                total_size += os.path.getsize(full_path) / 1024
                file_count += 1
            elif os.path.isdir(full_path):
                if os.path.exists(full_path):
                    size, files = get_dir_size(full_path)
                    total_size += size
                    file_count += files
        print(f'{root_dir} size={round(total_size, 2)}KB, files={file_count}')
        return total_size, file_count
    except PermissionError:
        return total_size, file_count