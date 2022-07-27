#!/usr/bin/python3
from random import randint
import xlsxwriter as xw
from os import getcwd
from sys import platform
from datetime import datetime


def export_to_xlsx(conn_type: list):
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
        if x < 2:
            for y in range(3):
                write_to_book.write(row + 2 + y, col, f"{conn_type[y]}", body_format)
                write_to_book.write(row + 2 + y, col + 1, f"{power_type[0]}", body_format)
                write_to_book.write(row + 2 + y, col + 2, "", body_format)
        else:
            for i in range(2):
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
        if x < 2:
            for idx, volt in enumerate(voltage_list):
                write_to_book.write(row + 2 + idx, col, volt, body_format)
                write_to_book.write(row + 2 + idx, col + 2, power_type[1], body_format)
                write_to_book.write(row + 2 + idx, col + 3, "", body_format)
        else:
            for i in range(2):
                write_to_book.write(row + 2 + i, col, 220, body_format)
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
            write_to_book.write(row + 2, col + 2, power_type[2], body_format)
            write_to_book.write(row + 2, col + 3, "", body_format)
            for idx, volt in enumerate(voltage_list):
                write_to_book.write(row + 3 + idx, col, volt, body_format)
                write_to_book.write(row + 3 + idx, col + 2, power_type[2], body_format)
                write_to_book.write(row + 3 + idx, col + 3, "", body_format)

        else:
            for i in range(2):
                write_to_book.write(row + 2 + i, col, 220, body_format)
                write_to_book.write(row + 2 + i, col + 2, power_type[2], body_format)
                write_to_book.write(row + 2 + i, col + 3, "", body_format)

    book.close()


def random_norm_temp(norm_temp_list: list, conn_type: list):
    pass


def random_test_list(test_list: list, conn_type: list):
    pass


def main():
    conn_type = ["ETH", "GPRS", "ETH+GPRS"]
    norm_temp_list = []
    test_list = []

    export_to_xlsx(conn_type)


if __name__ == '__main__':
    main()
