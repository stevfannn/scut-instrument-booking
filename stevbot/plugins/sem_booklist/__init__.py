from nonebot import on_command
from nonebot.adapters.cqhttp import Bot, Event

import re
import calendar

from .utils import get_booklist

YEAR = 2020

sem_booklist = on_command('电镜时间', priority=5)


@sem_booklist.handle()
async def handel_receive_date(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        arg_list = args.split()
        # 设备id参数，没有传入32位id或长度不够则默认14号楼107电镜
        if len(arg_list[0]) == 32:
            state['id'] = arg_list[0]
        elif len(arg_list[0]) == 4:
            result = await process_date(arg_list[0])
            if result:
                state['mm'], state['dd'] = result
            else:
                await sem_booklist.reject('日期格式不对或月份日数不正确，请确认是否是mmdd格式（如0809）')
        else:
            await help()
        if len(arg_list) > 1:
            result = await process_date(arg_list[0])
            if result:
                state['mm'], state['dd'] = result
            else:
                await sem_booklist.reject('日期格式不对或月份日数不正确，请确认是否是mmdd格式（如0809）')
    else:
        await help()


@sem_booklist.got('mm', prompt='请输入正确的日期')
@sem_booklist.got('dd', prompt='请输入正确的日期')
async def handle_date(bot: Bot, event: Event, state: dict):
    eid = state.get('id', '53c2d66934875f5c01348781996e0482')
    mm = state['mm']
    dd = state['dd']
    booklist = await get_booklist(eid, mm, dd)
    await sem_booklist.finish(booklist)


async def help():
    await sem_booklist.reject(r'''/电镜时间 [设备id] 日期
设备id：(可选)32位字母数字结构字符串，留空默认填入140107的电镜设备id
日期：(必须)请输入mmdd格式的日期，如10月15日则输入1015
下面是一个例子：
/电镜时间 1015
将会返回10月15日140107电镜的预约列表''')


async def process_date(strdate: str):
    if len(strdate) == 4:
        month, day = [int(x) for x in re.findall(r'(\d{2})(\d{2})', strdate)[0]]
        if 0 < month <= 12:
            _, max_day = calendar.monthrange(YEAR, month)
            if int(day) <= max_day:
                return month, day
