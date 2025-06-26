from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from django.contrib.auth import get_user_model
from io import BytesIO

User = get_user_model()

def create_stat_report(data, start, end):
    workbook = load_workbook('reports/stat_rep_template/pattern.xlsx')
    ws = workbook['Лист1']  # Указываем имя листа

    start_day, start_month = start.day, start.month
    end_day, end_month = end.day, end.month
    year = end.year

    ws['A2'] = (f'СТАТИСТИЧЕСКАЯ ФОРМА ОТЧЕТНОСТИ "1" отдела КЦОКБ за период с '
                f'{start_day}.{start_month}.{year} по {end_day}.{end_month}.{year}')

    organs = {   # координаты столбцов органов в excell
        'FIN': {
            'h': 'D',
            'm': 'E'
        },
        'GTS': {
            'h': 'F',
            'm': 'G'
        },
        'GNS': {
            'h': 'H',
            'm': 'I'
        },
        'ADM': {
            'h': 'N',
            'm': 'O'
        }
    }
    users = {
        'sema': 'Семаева Н.О.',
        'aza': 'Бейшеналиев А.К.',
        'adil': 'Осмоналиев А.А.',
        'ular': 'Касымбеков У.Н.'
    }

    start_row = 6

    for i, usr in enumerate(users, 1):
        row = start_row + i
        ws['A' + str(row)] = i   # заполняем число нумерацию
        ws['B' + str(row)] = users[usr]   # заполняем имя пользователя

        data = {k.lower(): v for k, v in data.items()}

        if usr.lower() not in data:   # если такой пользователь отсутствует в базе, то просто добавляем в таблицу без днных
            continue

        organizations_dct = data[usr]
        for org in organizations_dct:
            h_m = organs.get(org)

            if not h_m:
                continue

            cell_numb_h = h_m['h'] + str(row)
            org_h_m = organizations_dct[org]
            cell_val_h = org_h_m.get('Критическая', 0) + org_h_m.get('Высокая', 0)
            ws[cell_numb_h] = cell_val_h

            h_m = organs[org]
            cell_numb_m = h_m['m'] + str(row)
            org_h_m = organizations_dct[org]
            cell_val_m = org_h_m.get('Средняя', 0) + org_h_m.get('Низкая', 0)
            ws[cell_numb_m] = cell_val_m


    # Суммирование по столбцам
    for col in range(3, 21):
        col_letter = get_column_letter(col)
        formula = f"=SUM({col_letter}{start_row}:{col_letter}{11 - 1})"
        ws.cell(row=11, column=col).value = formula
        ws.cell(row=11, column=col).alignment = Alignment(horizontal='center')

    # Сохранение файла
    # Сохранение файла в память
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
