
#!/bin/bash

# Проверяем, переданы ли аргументы

if [ $# -ne 3 ]; then
  echo "Неверное количество аргуметов !"
  exit 1
fi

# Получаем путь к папке
folder_path=$1

# Проверяем, коректность аргументов
if [ ! -d "$folder_path" ]; then
  echo "Папка '$folder_path' не существует!"
  exit 1
fi

if [ ! ["$2" =~ ^[0-9]+] ]; then
  echo "Вы передали не число !"
  exit 1
fi

if [ ! ["$3" =~ ^[0-9]+] ]; then
  echo "Вы передали не число !"
  exit 1
fi
# Выводим результат
echo "Заполнение папки '$folder_path': $(df $folder_path |  awk 'NR==2 {print $5}')"

# Возвращаем код 0, если все прошло успешно
exit 0
