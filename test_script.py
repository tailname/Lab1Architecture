import unittest
import os
import time
import random
import shutil
import subprocess
import math

BASH_SCRIPT_PATH = './check_folder_usage.sh'
FOLDER_PATH = '/mnt/VHD/'


class ScriptTest(unittest.TestCase):
    def setUp(self):  # данный метод выполняется перед каждым тестом
        try:
            self.test_dir = FOLDER_PATH
        except Exception as e:
            print(f"Exception in SetUp {e}")

    def tearDown(self):  # данный метод выполняется после каждого теста, он очищает всю папку
        for filename in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Ошибка при удалении {file_path}: {e}")

    def create_test_files(self, num_files,
                          target_size_gb=0.6):  # данный метод создает папку с мин размером 0.6 в гб,если аргумент не передан
        target_size_bytes = target_size_gb * 1024 * 1024 * 1024
        current_size_of_folder = 0
        one_size_of_file = math.ceil(target_size_bytes / num_files)
        for i in range(num_files):
            file_path = os.path.join(self.test_dir, f'test_file_{i}.txt')  # закидываем в тестовую папку файл
            with open(file_path, 'w') as f:
                f.write(" " * one_size_of_file)  # заполняем этот файл чарами, 1 чар - 1 байт
        current_size_of_folder = self.get_folder_size(self.test_dir)
        if current_size_of_folder < target_size_bytes:
            print(f"Нехватка заполненности памяти папки, папка заполнена: {self.get_folder_size(self.test_dir)}")

    def get_folder_size(self, directory):  # данный метод выдает размер папки
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):  # пробегаемся по папке
            for f in filenames:  # пробегаемся по всем файлам
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)  # прибавляем к общей сумме размер f -того файла
        return total_size

    def test_valid_arguments(self):
        self.create_test_files(40, 0.8)  # папка заполнилась файлами
        expected_folder_size = self.get_folder_size(self.test_dir)
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        self.assertTrue(os.path.exists(self.test_dir))
        self.assertTrue(len(os.listdir(self.test_dir)) <= 30)
        archive_path = '/home/user/backup/oldest_files.tar.gz'  # задали путь
        self.assertTrue(os.path.exists(archive_path))
        current_folder_size = self.get_folder_size(self.test_dir)  # получаем размер папки после архивации
        self.assertLess(current_folder_size, expected_folder_size)  # проверяем меньше ли текущий чем прошлый

    def test_invalid_path(self):
        incorrect_path = "noneistent_dir"
        result = subprocess.run([BASH_SCRIPT_PATH, incorrect_path, "70"], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)

        self.assertIn(f"Папка '{incorrect_path}' не существует!\n", result.stdout)

    def test_invalid_folder_size(self):
        self.create_test_files(40)
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "invalid"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)  # проверка на неуспешное завершение скрипта
        self.assertIn("Вы передали не число !\n", result.stdout)

    def test_folder_size_below_threshold(self):
        self.create_test_files(20, 0.6)

        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)  # успешное завершение скрипта
        self.assertEqual(len(os.listdir(self.test_dir)), 20)  # проверка что в нашей папке 20 файлов

    def test_folder_size_above_threshold(self):
        self.create_test_files(60, 0.8)
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)  # успешная отработка скрипта
        self.assertLess(len(os.listdir(self.test_dir)), 60)  # проверка того, что в нашей папке меньше 60 файлов

    def test_sort_files_by_creation_time(self):
        self.create_test_files(40, 0.8)
        files_after_script = sorted(os.listdir(self.test_dir),
                       key=lambda filename: os.path.getctime(os.path.join(self.test_dir, filename))) #сортирует файлы
        second_30_files=files_after_script[10:]
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)  # успешная отработка кода
        files = sorted(os.listdir(self.test_dir),
                       key=lambda filename: os.path.getctime(os.path.join(self.test_dir, filename))) # сортирует файлы
        self.assertListEqual(files, second_30_files)


if __name__ == '__main__':
    unittest.main()
