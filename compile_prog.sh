#!/bin/bash
#python3 -m PyInstaller --onefile --name "alarm_zone" alarm_zone.py
python3 -m PyInstaller --onefile --name "blink" blink.py
python3 -m PyInstaller --onefile --name "check_synchro" check_synchro.py
python3 -m PyInstaller --onefile --name "fibra_scan" fibra_scan.py
python3 -m PyInstaller --onefile --name "lost_test" lost_test.py
python3 -m PyInstaller --onefile --name "power_test" power_test.py
