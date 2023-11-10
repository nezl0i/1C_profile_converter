import os
from abc import ABC, abstractmethod
from .converter_excel_header import create


class CreateProfileFiles:
    def __init__(self, path):
        self.path = path
        self.html_files: list = []  # Количество валидных html файлов
        self.txt_files: list = []  # Количество валидных html файлов
        self.all_files: list = []  # Общее количество файлов в каталоге
        self.find_profile_files()

    def find_profile_files(self):
        if isinstance(self.path, list):
            for file in self.path:
                self.all_files.append(file)
                if file.endswith('.html'):
                    self.html_files.append(file)
                if file.endswith('.txt'):
                    self.txt_files.append(file)
        else:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    self.all_files.append(os.path.join(root, file))
                    if file.endswith('.html'):
                        self.html_files.append(os.path.join(root, file))
                    if file.endswith('.txt'):
                        self.txt_files.append(os.path.join(root, file))


class AbstractConvertApplication(ABC):

    def __init__(self, profile):
        # self.profile_files = CreateProfileFiles(self.path)
        self.profile_files = profile

        self.all_data: list = []
        self.bad_txt_files: list = []  # Количество файлов с ошибками или невалидных файлов
        self.bad_html_files: list = []  # Количество файлов с ошибками или невалидных файлов

        self.all_files = self.profile_files.all_files  # Общее количество файлов в каталоге
        self.html_files = self.profile_files.html_files  # Количество валидных html файлов
        self.txt_files = self.profile_files.txt_files  # Количество валидных html файлов
        self.serial = '00000000'
        self.create_report = create

    @abstractmethod
    async def make_report(self): ...
