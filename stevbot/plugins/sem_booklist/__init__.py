from nonebot import on_command, on_regex
from nonebot.adapters.cqhttp import Bot, Event

import re
import calendar
import datetime

from .utils import get_booklist
from .eid_dict import M2EID

YEAR = 2020
DATE_CN = ['今天', '明天', '后天']

sem_booklist = on_regex(r'设备时间|看看', priority=5)


@sem_booklist.handle()
async def handel_receive_date(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        arg_list = args.split()
        # 设备id参数，没有传入32位id或长度不够则默认14号楼107电镜
        if len(arg_list[1]) == 32:
            state['id'] = arg_list[1]
        elif arg_list[1][0] == 'm':
            if M2EID.get(arg_list[1]) is not None:
                state['id'] = M2EID.get(arg_list[1])
            else:
                await sem_booklist.reject(f'{arg_list[1]}编号还未加入机器人的内置id列表！')
        i = 2 if len(arg_list) > 2 else 1
        result = await process_date(arg_list[i])
        if result:
            state['mm'], state['dd'] = result
        else:
            await sem_booklist.reject('日期格式不对或月份日数不正确，请确认是否是mmdd格式（如0809）')
    else:
        await sem_booklist.reject(r'''- /设备时间 [设备id] 日期
- - 设备id：(可选)32位字母数字结构字符串，留空默认填入140107的电镜设备id
机器人也内置了励吾楼电镜的id，直接输入m1代替设备id即可。
- - 日期：(必须)请输入mmdd格式的日期，如10月15日则输入1015
也可以输入今天、明天、后天三个关键词自动填入对应日期

- 下面是一些例子：
- - /设备时间 1014
将会返回10月14日140107电镜的预约列表
- - /设备时间 m1 明天
将会返回明天励吾楼场发射电镜的预约列表
- - /设备时间 一串设备id 后天
将会返回给定设备后天的预约列表''')


@sem_booklist.got('mm')
@sem_booklist.got('dd')
async def handle_date(bot: Bot, event: Event, state: dict):
    eid = state.get('id', '53c2d66934875f5c01348781996e0482')
    mm = state['mm']
    dd = state['dd']
    booklist = await get_booklist(eid, mm, dd)
    # await bot.send(event, booklist, at_sender=True)
    await sem_booklist.finish(booklist)


async def process_date(strdate: str):
    if len(strdate) == 4:
        # 判断是否mmdd格式
        month, day = [int(x) for x in re.findall(r'(\d{2})(\d{2})', strdate)[0]]
        if 0 < month <= 12:
            _, max_day = calendar.monthrange(YEAR, month)
            if int(day) <= max_day:
                return month, day
    elif len(strdate) == 2:
        # 判断是否中文日子？
        try:
            day_shift = DATE_CN.index(strdate)
            today = datetime.date.today()
            day_modified = today + datetime.timedelta(days=day_shift)
            return day_modified.month, day_modified.day
        except ValueError:
            pass
