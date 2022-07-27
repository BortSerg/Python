#!/usr/bin/python3
import asyncio
import os
import time
import serial
import telebot
#from telebot import types

from sys import platform


def main():
    ws_id1 = "1F33DB"
    ws_id2 = '1c745e'
    port = input("Enter port: ")
    if platform == "linux" or platform == "linux2":
        serialport = serial.Serial("/dev/ttyUSB"+port, 115200)
    if platform == "win32":
        serialport = serial.Serial("COM"+port, 115200)

    serialport.write("log * 0\r\n".encode("UTF-8"))
    serialport.write("log jwl3* 5\r\n".encode("UTF-8"))
    serialport.write("log hts* 5\r\n".encode("UTF-8"))
    serialport.write("log hub* 5\r\n".encode("UTF-8"))
    serialport.write("log HUB* 5\r\n".encode("UTF-8"))

    # time_begin = time.ctime(time.time())
    # print("Time to start 2 case: ", time_begin)
    # ws_clicker2(ws_id, serialport)
    # time_begin = time.ctime(time.time())
    # print("Time to start 3 case: ", time_begin)
    # ws_clicker3(ws_id,serialport)
    ws_clicker2(ws_id1,ws_id2,serialport)

    serialport.close()


def ws_clicker2(ws_id, ws_id2, serialport):
    time_begin = time.time()
    serialport.write(("jwl3 ws %s 2\r\n" %ws_id).encode("UTF-8"))
    clicked_counter = 0
    while True:
    # while time.time()-time_begin<11000:
        clicked_counter = clicked_counter+1
        print("Test1: ",clicked_counter)

        time.sleep(180)
        i = 0
        while i<10:
            serialport.write(("jwl3 ws %s 1\r\n" %ws_id).encode("UTF-8"))
            serialport.write(("jwl3 ws %s 1\r\n" %ws_id2).encode("UTF-8"))
            time.sleep(4)
            serialport.write(("jwl3 ws %s 2\r\n" %ws_id).encode("UTF-8"))
            serialport.write(("jwl3 ws %s 2\r\n" %ws_id2).encode("UTF-8"))
            time.sleep(4)
            i=i+1


def ws_clicker3(ws_id, serialport):
    time_begin = time.time()
    serialport.write(("jwl3 ws %s 1\r\n" % ws_id).encode("UTF-8"))
    clicked_counter1 = 0
    while True:
    #while True:
        clicked_counter1 = clicked_counter1 + 1
        print("Test2: ", clicked_counter1)

        time.sleep(180)

        serialport.write(("jwl3 ws %s 2\r\n" % ws_id).encode("UTF-8"))
        time.sleep(2)
        serialport.write(("jwl3 ws %s 1\r\n" % ws_id).encode("UTF-8"))


def pair_click(ws_id1,ws_id2, serialport):
    time_begin = time.time()
    serialport.write(("jwl3 ws %s 1\r\n" % ws_id1).encode("UTF-8"))
    serialport.write(("jwl3 ws %s 1\r\n" % ws_id2).encode("UTF-8"))
    clicked_counter1 = 0

    while True:

        clicked_counter1 = clicked_counter1 + 1
        print("Pair Click: ", clicked_counter1)

        i = 0
        while i < 10:
            serialport.write(("jwl3 ws %s 1\r\n" % ws_id2).encode("UTF-8"))
            time.sleep(4)
            serialport.write(("jwl3 ws %s 2\r\n" % ws_id2).encode("UTF-8"))
            time.sleep(4)
            i = i + 1
        serialport.write(("jwl3 ws %s 1\r\n" % ws_id2).encode("UTF-8"))


        time.sleep(100)

        serialport.write(("jwl3 ws %s 2\r\n" % ws_id1).encode("UTF-8"))
        time.sleep(2)
        serialport.write(("jwl3 ws %s 1\r\n" % ws_id1).encode("UTF-8"))



if __name__ == '__main__':
    main()
