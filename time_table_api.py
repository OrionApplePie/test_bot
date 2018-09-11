import re
from datetime import datetime

import requests
from lxml import etree, html


TIMETABLE_URL = 'https://www.dvgups.ru/studtopmenu/study/timetables'


def _get_text_timetable(faculty, group):
    u"""Метод для извлечения и парсинга текстового расписания заданной группы."""
    payload = {
        'view': 'timetable',
        'selector': 'grp',
        'sel1': faculty,
        'sel2': group
    }
    # TODO: сделать проверку возвращаемого кода
    page = requests.get(
        TIMETABLE_URL,
        params=payload
    )

    tree = html.fromstring(page.content)
    
    table = tree.xpath('//*[@id="grp_selector"]/pre/text()')

    return table


def _parse_time_table(time_table):
    """Parse time texttimetable to dict."""

    time_table = time_table[0].replace(u'\xa0', ' ').split('\n')
    
    start_collect = False
    is_simple_line = False
    is_class_line = False
    
    table_list = []
    
    for line in time_table:
        # поиск горизонтальной линии-разделитиля с временем в начале
        is_class_line = re.findall(r'(\d\d\.\d\d)\s?─', line)
        # поиск простой горизонтальной линии-разделитиля
        is_simple_line = re.findall(r'^[─]+\s?$', line)
        
        if is_simple_line or is_class_line:
            start_collect = True
            
            if table_list:
                table_list.append(
                    ['line']*len(table_list[0])
                )
            
            continue
        
        if start_collect:    
            table_list.append(
                line.split('│')
            )
    
    max_len_el = len(max(table_list))
    
    new_table_list = filter(
        lambda el: len(el) == max_len_el,
        table_list
    )
    
    zipped_table_list = zip(*new_table_list)
    
    day_count = 0
    res_time_table = {}
    
    for column in list(zipped_table_list):
        day = {}
        count = 0
                 
        for i in column:
            if i == 'line':
                count += 1
                continue
    
            if count in day:
                day[count] += (i + '\n')
            else:
                day[count] = (i + '\n')
        
        res_time_table[day_count] = day
        day_count += 1
    
    return res_time_table



def get_time_table(department='ЕНИ', group='ПМ1.TXT'):
    """Api function for get tt."""    
    tt = _get_text_timetable(department, group)
    tt = _parse_time_table(tt)
    return tt


def get_timetable_by_day(weekday):
    """"""
    
    tt = get_time_table()
    # for class_ in tt[weekday]:
        # if
    res = ''

    try:
        tt_day = tt[weekday].items()
    except KeyError as e:
        return 'День не найден!'

    for class_num, t in tt_day:
        if class_num != 0:
            res += ('\n{} пара\n'.format(class_num) + t)
    
    return res
