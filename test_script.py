import unittest
import os
import time
import random
import shutil
import subprocess
import math

# for x in dir(unittest.TestCase):
#     print(x)
# Путь к скрипту который хотим протестировать, заменить на реальный путь
BASH_SCRIPT_PATH = './check_folder_usage.sh'
FOLDER_PATH='/mnt/VHD/'

class ScriptTest(unittest.TestCase):
    def setUp(self):  # в данном методе перед каждый тестом мы будем создавать новую тестовую папку
        try:
            self.test_dir = FOLDER_PATH  # todo спросить андрюху
        except Exception as e:
            print(f"Exception in SetUp {e}")

    def tearDown(self):
        for filename in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Ошибка при удалении {file_path}: {e}")

    def create_test_files(self, num_files, target_size_gb=0.6):  # создаем папку с мин размером 0.6 в гб
        target_size_bytes = target_size_gb * 1024 * 1024 * 1024
        current_size = 0
        one_size = math.ceil(target_size_bytes / num_files)
        for i in range(num_files):
            file_path = os.path.join(self.test_dir, f'test_file_{i}.txt')  # закидываем в тестовую папку файл
            with open(file_path, 'w') as f:
                f.write(" " * one_size)  # заполняем этот файл чарами, 1 чар - 1 байт
        current_size=self.get_folder_size(self.test_dir)
        if current_size < target_size_bytes:
            print(f"Нехватка заполненности памяти папки, папка заполнена: {self.get_folder_size(self.test_dir)}")
            # todo: нужна ли эта штука!!!!
            # вопрос нужна ли эта штука!! надеюсб что это штука выведет запо.лненность в битах, надо еще изучить

    def get_folder_size(self, directory):
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

        # вот это хз надо или нет!
        # todo: все оставшиеся assert IN такие штуки будут работать или они должны прописываться в скрипте? и в каком образе??
        # self.assertIn("Заполненность папки: ", result.stdout)
        # self.assertIn("Архив создан: ", result.stdout)

        self.assertTrue(os.path.exists(self.test_dir))  # наврено проверка что она сущ
        # todo: вместо 15 подумать
        self.assertTrue(len(os.listdir(self.test_dir)) <= 30)  # вместо 15 задать сколько файлов должно остаться
        archive_path = '/home/user/backup/oldest_files.tar.gz'  # задали путь
        # todo ввести строчкой что именно тот путь существует!
        self.assertTrue(os.path.exists(archive_path))  # наверно проверка что он сущ
        current_folder_size = self.get_folder_size(self.test_dir)  # получаем текущий размер папки
        self.assertLess(current_folder_size, expected_folder_size)  # проверяем меньше ли текущий чем прошлый


    def test_invalid_path(self):
        incorrect_path = "noneistent_dir"
        result = subprocess.run([BASH_SCRIPT_PATH, incorrect_path, "70"], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)  # неуспешное заверешение скрипта

        self.assertIn(f"Папка '{incorrect_path}' не существует!\n", result.stdout)


    def test_invalid_folder_size(self):
        self.create_test_files(40)
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "invalid"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)  # проверка на неуспешное завершение скрипта
        self.assertIn("Вы передали не число !\n", result.stdout)

    def test_folder_size_below_threshold(self):
        self.create_test_files(20,0.6)

        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)  # успешное завершение скрипта
        #self.assertNotIn("Архив создан", result.stdout) такая строчка в скрипте не прописана
        self.assertEqual(len(os.listdir(self.test_dir)), 20)  # проверка что в нашей папке 20 файлов

    def test_folder_size_above_threshold(self):
        self.create_test_files(60,0.8)
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)  # успешная отработка скрипта
        #self.assertIn("Архив создан", result.stdout)  # проверка архивирования? если унас такая есть
        # todo вопрос с количеством файлов 60 или 40 будет в итоге создано!
        self.assertLess(len(os.listdir(self.test_dir)), 60)  # проверка того, что в нашей папке меньше 60 файлов

    def test_sort_files_by_creation_time(self):
        self.create_test_files(40,0.8)
        # заменены проценты с 75 на 70
        result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "70"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)  # успешная отработка кода
        # todo разобраться, что это такое вообще и работает ли!
        files = sorted(os.listdir(self.test_dir),
                       key=lambda filename: os.path.getctime(os.path.join(self.test_dir, filename)))
        # проверка что 30 файлов в папке,а  10 в архив
        # todo вопрос с количеством файлов, после того что сделала эта штука, что происходит с файлами???
        self.assertEqual(len(files), 30)

    # def test_invalid_file_count(self):
#     self.create_test_files(40)
#     result = subprocess.run([BASH_SCRIPT_PATH, self.test_dir, "invalid", "70"], capture_output=True, text=True)
#
#     self.assertNotEqual(result.returncode, 0)  # неуспешное заверешние скрипта
#
#     self.assertIn("Ошибка количества числа файлов", result.stderr)

if __name__ == '__main__':
    unittest.main()
