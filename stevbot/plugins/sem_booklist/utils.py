import re
import requests
from lxml import etree

URL = 'http://yqgx.7w2.cas.scut.edu.cn:8380/guest/appointmentList!query.action'
URL_ID = 'http://yqgx.7w2.cas.scut.edu.cn:8380/guest/appointmentDetailList.action'
URL_DETAIL = 'http://yqgx.7w2.cas.scut.edu.cn:8380/details.jsp'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/84.0.4147.105 Safari/537.36 '
}
re_id = re.compile(r"'([0-9a-zA-Z]{32})'")


def end_time_shift(t: str) -> str:
    mmss = [int(x) for x in re.findall(r'(\d{2}):(\d{2})', t)[0]]
    mmss[1] += 15
    if mmss[1] >= 60:
        mmss[0] += 1
        mmss[1] = '00'
    return '{}:{}'.format(*mmss)


async def get_booklist(eid: str, mm: str, dd: str):
    # response = requests.get(url=URL_DETAIL, headers=headers, params=f'equipmentId={eid}')
    #
    booking_data = {
        'equipmentId': eid,
        'day': dd,
        'year': '2020',
        'month': mm,
    }
    response = requests.post(url=URL, data=booking_data, headers=headers)
    tree = etree.HTML(response.text)
    tr_list = tree.xpath('//*[@id="listForm"]/div[4]/table/tr/td[@id="dialog"]/table/tr')
    book_time_list = []
    id_list = []
    for tr in tr_list:
        td_list = tr.xpath('./td')
        for td in td_list:
            a_tag = td.xpath('./a')
            if a_tag:
                a_href = td.xpath('./a/@href')[0]
                id_list.append(re.findall(re_id, a_href)[0])
                book_time_list.append(td.xpath('./a/text()')[0])
    bname_list = []
    for bid in id_list:
        response = requests.get(url=URL_ID, headers=headers, params=f'id={bid}').text
        tree = etree.HTML(response)
        bname = tree.xpath('//div[@class="area4"]/table/tr[2]/td[3]/text()')[0]
        bname_list.append(bname)
    output_str = '2020年{}月{}日{}的预约情况：'.format(mm, dd, eid)

    book_section = book_separator(book_time_list, bname_list)
    output_str = output_formattor(output_str, book_section)
    return output_str


def output_formattor(output_str, book_section):
    if len(book_section) > 0:
        book_time_list = []
        bname_list = []
        for (i, b_s) in enumerate(book_section):
            output_str += '\n[{}]\t预约时间段：{time_start} - {time_end}\n\t{blank:^4}预约人：{name}'.format(
                i + 1,
                blank=' ',
                **b_s
            )
        return output_str
    else:
        output_str += '\n今天还没有预约哦'
        return output_str


def book_separator(time_list, name_list):
    time_list.append('end')
    name_list.append('end')
    last_name = name_list[0]
    last_time = time_list[0]
    book_section = []
    for i, t in enumerate(time_list):
        if name_list[i] != last_name:
            book_section.append({
                'name': last_name,
                'time_start': last_time,
                'time_end': end_time_shift(time_list[i - 1])
            })
            last_name = name_list[i]
            last_time = time_list[i]
    return book_section
