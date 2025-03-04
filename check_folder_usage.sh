#!/bin/bash

# Проверяем, переданы ли аргументы

if [ $# -ne 2 ]; then
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

if [[ ! $2 =~ ^[0-9]+  ]]; then
  echo "Вы передали не число !"
  exit 1
fi

# Выводим процент заполненности

persent_of_full=$(df $folder_path |  awk 'NR==2 {print $5}' | awk -F '%' '{print $1}')
echo "Заполнение папки '$folder_path': $persent_of_full %"

# Сравниваем с аргументами
if [ $persent_of_full -lt $2 ]; then
  exit 0
fi
N=10
oldest_files=$(find $folder_path -type f -printf '%T+ %p\n' 2>/dev/null | sort | awk -F $folder_path 'NR<='$N' {print $2}' )

tar -czf $HOME/backup/oldest_files.tar.gz -C $folder_path $oldest_files 

for file in $oldest_files; do
  echo "Удаляем файл $file"
  rm $folder_path'/'$file
done

# Возвращаем код 0, если все прошло успешно
exit 0
