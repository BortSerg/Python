#!/usr/bin/python3
from random import randint
import xlsxwriter as xw
from os import getcwd
from sys import platform
from datetime import datetime


def export_to_xlsx(connect_type: list, norm_temp_list: list, test_list: list):
    power_type = ["АКБ", "От сети", "220+Charge"]
    temperature_list = ['-10', '+45', '+25']
    voltage_list = [85, 150, 220, 250]

    filename = f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}_pairwise_gsm_eth_power.xlsx"
    if platform in {"linux", "linux2"}:
        file = open(f"{getcwd()}/{filename}", "w")
        file.close()
    if platform == "win32":
        file = open(f"{getcwd()}\{filename}", "w")
        file.close()

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

    # data in first column
    for x in range(3):
        col = 1
        row = x * 10
        write_to_book.set_column('B1:D1', 10) if x == 0 else None
        write_to_book.merge_range(row, col, row, col + 2, f"Temp ({temperature_list[x]}) Low АКБ", head_merge_format)
        write_to_book.write(row + 1, col, "Connection", head_text_format)
        write_to_book.write(row + 1, col + 1, "Power", head_text_format)
        write_to_book.write(row + 1, col + 2, "Result", head_text_format)
        if x < 2:                                                                                              # Temp (-10/+45) Low АКБ
            for y in range(3):
                write_to_book.write(row + 2 + y, col, f"{connect_type[y]}", body_format)
                write_to_book.write(row + 2 + y, col + 1, f"{power_type[0]}", body_format)
                write_to_book.write(row + 2 + y, col + 2, "", body_format)
        else:                                                                                                   # Temp (+25) Low АКБ
            for i in range(2):
                write_to_book.write(row + 2 + i, col, norm_temp_list[i*3], body_format)
                write_to_book.write(row + 2 + i, col + 1, f"{power_type[0]}", body_format)
                write_to_book.write(row + 2 + i, col + 2, "", body_format)

    # data in second column
    for x in range(3):
        col = 6
        row = x * 10
        write_to_book.set_column('G1:J1', 10) if x == 0 else None
        write_to_book.merge_range(row, col, row, col + 3, f"Temp ({temperature_list[x]}) 220V", head_merge_format)
        write_to_book.write(row + 1, col, "Voltage", head_text_format)
        write_to_book.write(row + 1, col + 1, "Connection", head_text_format)
        write_to_book.write(row + 1, col + 2, "Power", head_text_format)
        write_to_book.write(row + 1, col + 3, "Result", head_text_format)
        if x < 2:                                                                                 # data Temp (-10/+45) 220V
            for idx, volt in enumerate(voltage_list):
                write_to_book.write(row + 2 + idx, col, volt, body_format)
                if x == 0:
                    write_to_book.write(row + 2 + idx, col + 1, test_list[idx][0], body_format)
                if x == 1:
                    write_to_book.write(row + 2 + idx, col + 1, test_list[idx][2], body_format)

                write_to_book.write(row + 2 + idx, col + 2, power_type[1], body_format)
                write_to_book.write(row + 2 + idx, col + 3, "", body_format)
        else:
            for i in range(2):                                                                      # data Temp (+25) 220V
                write_to_book.write(row + 2 + i, col, 220, body_format)
                write_to_book.write(row + 2 + i, col + 1, norm_temp_list[(i * 3) + 1], body_format)
                write_to_book.write(row + 2 + i, col + 2, power_type[1], body_format)
                write_to_book.write(row + 2 + i, col + 3, "", body_format)

    # data im third column
    for x in range(3):
        col = 12
        row = x * 10
        write_to_book.set_column('M1:P1', 11) if x == 0 else None
        write_to_book.merge_range(row, col, row, col + 3, f"Temp ({temperature_list[x]}) От сети+зарядка", head_merge_format)
        write_to_book.write(row + 1, col, "Voltage", head_text_format)
        write_to_book.write(row + 1, col + 1, "Connection", head_text_format)
        write_to_book.write(row + 1, col + 2, "Power", head_text_format)
        write_to_book.write(row + 1, col + 3, "Result", head_text_format)
        if x < 2:
            write_to_book.write(row + 2, col, 85, body_format)
            write_to_book.write(row + 2, col + 1, "GPRS", body_format)
            write_to_book.write(row + 2, col + 2, power_type[2], body_format)
            write_to_book.write(row + 2, col + 3, "", body_format)
            for idx, volt in enumerate(voltage_list):
                write_to_book.write(row + 3 + idx, col, volt, body_format)
                if x == 0:
                    write_to_book.write(row + 3 + idx, col + 1, test_list[idx][1], body_format)
                if x == 1:
                    write_to_book.write(row + 3 + idx, col + 1,  test_list[idx][3], body_format)
                write_to_book.write(row + 3 + idx, col + 2, power_type[2], body_format)
                write_to_book.write(row + 3 + idx, col + 3, "", body_format)
        else:                                                                               # data Temp (+25) 220V + charge
            for i in range(2):
                write_to_book.write(row + 2 + i, col, 220, body_format)
                write_to_book.write(row + 2 + i, col + 1, norm_temp_list[(i * 3) + 2], body_format)
                write_to_book.write(row + 2 + i, col + 2, power_type[2], body_format)
                write_to_book.write(row + 2 + i, col + 3, "", body_format)

    book.close()
    print(f"file save path {getcwd()}/{filename}")


def random_norm_temp(connect_type: list):
    norm_temp_list = []
    for row in range(2):
        count = {"ETH": 0, "GPRS": 0, "ETH+GPRS": 0}
        for col in range(3):
            while True:
                value = connect_type[randint(0, len(connect_type) - 1)]
                if (count[value] == 0 and row == 0) or (count[value] == 0 and row == 1 and value != norm_temp_list[col - 3] and value != norm_temp_list[col - 2]):
                    count[value] += 1
                    break
            norm_temp_list.append(value)
    return norm_temp_list


def random_test_list(connect_type: list):
    test_list = [[], [], [], []]
    for row in range(3):
        counter = {"ETH": 2, "GPRS": 0, 'ETH+GPRS': 0} if row == 0 else {"ETH": 0, "GPRS": 0, 'ETH+GPRS': 0}
        for col in range(4):
            while True:
                value = connect_type[randint(0, len(connect_type) - 1)]
                if row == 0:
                    if col == 1 or col == 3:
                        value = connect_type[0]
                        break
                    elif counter[value] == 0:
                        counter[value] += 1
                        break
                else:
                    check_list = []
                    for i in range(row):
                        check_list.append(test_list[i][col])
                    if value not in check_list and counter[value] <= 1:
                        counter[value] += 1
                        break
            test_list[row].append(value)
    counter = {"ETH": 0, "GPRS": 0, 'ETH+GPRS': 0}
    for x in range(4):
        while True:
            value = connect_type[randint(0, len(connect_type) - 1)]
            if counter[value] == 0:
                test_list[3].append(value)
                counter[value] += 1
                break
            if x == 3:
                test_list[3].append(value)
                break

    return test_list


def print_to_console(test_list: list):
    for col in range(4):
        for row in range(4):
            print(test_list[row][col])
        print('-'*10)


def main():
    connect_type = ["ETH", "GPRS", "ETH+GPRS"]
    norm_temp_list = random_norm_temp(connect_type)
    test_list = random_test_list(connect_type)
    print_to_console(test_list)
    export_to_xlsx(connect_type, norm_temp_list, test_list)


if __name__ == '__main__':
    main()
