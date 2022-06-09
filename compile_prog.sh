#!/bin/bash
#Скрипт для компиляции скриптов *.py в бинарный файл для работы в Linux и скрития кода программы

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo $DIR
cd "$DIR"
rm -r build/
rm *.spec

NAME=$(uname -v)

NAME="$(lsb_release "-r")"
echo $NAME

if [[ $NAME == *"21.10"* ]]; then
  DIR_NAME='Ubuntu 21.10'
fi

if [[ $NAME == *"20.04"* ]]; then
  DIR_NAME='Ubuntu 18.04'
fi

if [[ $NAME == *"18.04"* ]]; then
  DIR_NAME='Ubuntu 18.04'
fi

echo saved to $DIR/$DIR_NAME

#python3 -m PyInstaller --onefile --distpath "$DIR_NAME" --name "alarm_zone" alarm_zone.py
python3 -m PyInstaller --clean --onefile --distpath "$DIR_NAME" --name "blink" blink.py
python3 -m PyInstaller --clean --onefile --distpath "$DIR_NAME" --name "check_synchro" check_synchro.py
python3 -m PyInstaller --clean --onefile --distpath "$DIR_NAME" --name "fibra_scan" fibra_scan.py
python3 -m PyInstaller --clean --onefile --distpath "$DIR_NAME" --name "lost_test" lost_test.py
python3 -m PyInstaller --clean --onefile --distpath "$DIR_NAME" --name "power_test" power_test.py

rm -r build/
rm *.spec