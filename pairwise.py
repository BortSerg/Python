#!/usr/bin/python3
from random import randint
import xlsxwriter as xw
from os import getcwd
from sys import platform
from datetime import datetime


def generate_head_list(test_list: list, volt_list: list, akb_list: list, temp_list: list):
    for temp in temp_list:
        for akb in akb_list:
            for volt in volt_list:
                test_list.append([volt, akb, "", temp])
    for x in range(2):
        for y in range(2):
            test_list.append([volt_list[2], akb_list[x], "", 25])


def generate_random_connect_list(test_list: list, connect_type: list):
    for idx in range(4):
        counter = {"eth": 0, "gprs": 0, "eth+gprs": 0}
        for row in range(idx, len(test_list), 4):
            volt, akb, connect, temp = test_list[row]
            if row < 12:
                while True:
                    if row == 0 or row == 8:
                        connect = connect_type[0]  # = eth
                        break
                    connect = connect_type[randint(0, 2)]
                    if (idx == 0 or idx == 3) and counter[connect] == 0:
                        counter[connect] += 1
                        break
                    if (0 < idx < 3) and (counter[connect]) <= 1:
                        check_list = []
                        for x in range(row - idx, row, 1):
                            check_list.append(test_list[x][2])
                        if connect not in check_list:
                            counter[connect] += 1
                            break

            if row >= 12:
                while True:
                    connect = connect_type[randint(0, 2)]
                    if idx == 0 or idx == 3:
                        break
                    if 0 < idx < 3:
                        check_list = []
                        for x in range(row - idx, row, 1):
                            check_list.append(test_list[x][2])
                        if connect not in check_list:
                            break

            test_list[row] = [volt, akb, connect, temp]
    while True:                                                                # for check repeats random value in normal temp table
        if test_list[-1:][0][2] != test_list[-2:-1][0][2]:
            break
        else:
            connect = connect_type[randint(0, 2)]
            if connect != test_list[-2:-1][0][2]:
                test_list[-2:-1][0][2] = connect
                break

    test_list.insert(1, [85, "Low_AKB", 'gprs', -10])
    test_list.insert(10, [85, "Low_AKB", 'gprs', 45])


def print_to_console(test_list: list):
    for i in range(len(test_list)):
        print(test_list[i])
        if i in {4, 8, 13, 17}:
            print("=" * 26)


def export_to_xlsx(test_list: list):
    filename = f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}_pairwise.xlsx"
    if platform in {"linux", "linux2"}:
        file = open(f"{getcwd()}/{filename}", "w")
        file.close()
    if platform == "win32":
        file = open(f"{getcwd()}\{filename}", "w")
        file.close()

    akb_status = ["LOW", "100%"]
    book = xw.Workbook(filename=filename)
    write_to_book = book.add_worksheet(name="pairwise")

    head_merge_format = book.add_format({
        'font_name': 'Calibri',
        'font_size': 11,
        'bold': False,
        'border': 0,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#dee6ef',
    })

    head_text_format = book.add_format({
        'font_name': 'Calibri',
        'font_size': 11,
        'bold': False,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'fff5ce',
    })

    body_format = book.add_format({
        'font_name': 'Calibri',
        'font_size': 11,
        'bold': False,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    })

    # generate head
    for row in range(3):
        if row > 0:
            row *= 9
        for col in range(2):
            write_to_book.set_column(col * 6 + 2, col * 6 + 2, 10)
            write_to_book.merge_range(row, col * 6 + 1, row, col * 6 + 4, f"АКБ {akb_status[col]}", head_merge_format)
            write_to_book.write_row(row + 1, col * 6 + 1, ("Voltage", "Connection", "Temp", "Results"), head_text_format)

    # write data to table
    for idx in range(0, len(test_list), 1):
        row = idx + 2
        voltage, akb_status, conn_type, temperature = test_list[idx]
        if akb_status == "Low_AKB":
            write_to_book.write_row(row, 1, (voltage, conn_type, temperature, ""), body_format)
        if akb_status == "Norm_AKB":
            row = row - 5 if idx < 20 else row - 2
            write_to_book.write_row(row, 7, (voltage, conn_type, temperature, ""), body_format)
    book.close()
    print(f"file save path {getcwd()}/{filename}")


def main():
    connect_type = ["eth", "gprs", "eth+gprs"]
    volt_list = [85, 150, 220, 250]
    akb_list = ["Low_AKB", "Norm_AKB"]
    temp_list = [-10, 45]
    test_list = []

    generate_head_list(test_list, volt_list, akb_list, temp_list)                         # generate head test list

    generate_random_connect_list(test_list, connect_type)                                 # generate random connection type

    print_to_console(test_list)                                                           # print to console test list

    export_to_xlsx(test_list)                                                             # export to exel file


if __name__ == "__main__":
    main()
