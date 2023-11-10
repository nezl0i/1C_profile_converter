import os
import xlsxwriter


async def create_sheet(serial, profile):
    root_path = os.getcwd()
    path = os.path.join(root_path, "Excel")

    # Создаем папку, если она не существует
    if not os.path.exists(path):
        os.makedirs(path)

    # if not os.path.isfile(os.path.join(path, f'{serial}.xlsx')):
    workbook = xlsxwriter.Workbook(os.path.join(path, f'{serial}.xlsx'))
    # else:
    #     workbook = xlsxwriter.Workbook(os.path.join(path, f'{serial}_2.xlsx'))

    if profile[0][0] == '30+30' or profile[0][0] == '60':
        # sheet = workbook.get_worksheet_by_name('60 мин')
        sheet = workbook.add_worksheet('60 мин')
    else:
        # sheet = workbook.get_worksheet_by_name('30 мин')
        sheet = workbook.add_worksheet('30 мин')

    header_format = workbook.add_format(
        {'bg_color': '#BDD7EE', 'border': 1, "font_name": "Arial Narrow", 'align': 'center'})
    column_format = workbook.add_format(
        {'border': 1, "font_name": "Arial Narrow", 'align': 'center', 'num_format': '# ##0.0000'})
    footer_format = workbook.add_format(
        {'bg_color': '#FFDAB9', 'border': 1, "font_name": "Arial Narrow", 'align': 'center'})
    total_format = workbook.add_format(
        {'bg_color': '#FFDAB9', 'border': 1, "font_name": "Arial Narrow", 'align': 'center', 'num_format': '###0.0000'})

    # Заголовок
    sheet.write('A8', 'Дата', header_format)
    sheet.write('B8', 'Время', header_format)
    sheet.write('C8', 'A+, Квт', header_format)
    sheet.write('D8', 'A-, Квт', header_format)
    sheet.write('E8', 'R+, Квт', header_format)
    sheet.write('F8', 'R-, Квт', header_format)

    sheet.write('B1', 'Точка учета', header_format)
    sheet.write('B2', 'Код', header_format)
    sheet.write('B3', 'Номер договора', header_format)
    sheet.write('B4', 'Номер ТУ', header_format)
    sheet.write('B5', 'Номер ПУ', header_format)
    sheet.write('B6', 'Ктт/Ктн', header_format)
    sheet.write('B7', 'Уровень напряжения', header_format)

    for _ in range(1, 8):
        sheet.write(f'A{_}', '', header_format)
        sheet.merge_range(f'C{_}:F{_}', '', header_format)

    sheet.set_column('A:A', 12.30)
    sheet.set_column('B:B', 24.30)
    sheet.set_column('C:F', 20)

    total_active_positive = 0
    total_active_negative = 0
    total_reactive_positive = 0
    total_reactive_negative = 0

    sheet.write('C5:F5', serial, header_format)

    end_row = 0

    for row_num, row_data in enumerate(profile, start=8):
        sheet.write(row_num, 0, row_data[1].split()[0], column_format)
        sheet.write(row_num, 1, row_data[1].split()[1], column_format)
        sheet.write(row_num, 2, float(row_data[2]), column_format)
        sheet.write(row_num, 3, float(row_data[3]), column_format)
        sheet.write(row_num, 4, float(row_data[4]), column_format)
        sheet.write(row_num, 5, float(row_data[5]), column_format)

        total_active_positive += float(row_data[2])
        total_active_negative += float(row_data[3])
        total_reactive_positive += float(row_data[4])
        total_reactive_negative += float(row_data[5])

        end_row = row_num

    sheet.merge_range(f'A{end_row + 2}:B{end_row + 2}', '', footer_format)
    sheet.write(end_row + 1, 0, 'Итого кВтч/кВАРч', footer_format)
    sheet.write(end_row + 1, 2, total_active_positive, total_format)
    sheet.write(end_row + 1, 3, total_active_negative, total_format)
    sheet.write(end_row + 1, 4, total_reactive_positive, total_format)
    sheet.write(end_row + 1, 5, total_reactive_negative, total_format)
    workbook.close()


async def create(data_list):
    if data_list is None or len(data_list) == 0:
        return

    for profile_items in data_list:
        for serial, profile in profile_items.items():
            await create_sheet(serial, profile)

# if __name__ == '__main__':
#     mercury = Mercury('../')
#     data = mercury.get_data()
#     create(data)
