import requests
from lxml import etree
import pickle

URL_DETAIL = 'http://yqgx.7w2.cas.scut.edu.cn:8380/details.jsp'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/84.0.4147.105 Safari/537.36 '
}
# 将内置设备id的识别码与eid对应转换的字典
M2EID = {
    'm0': '53c2d66934875f5c01348781996e0482',
    'm1': '4aa6427333f87dba01340c0c6e880003',
}
DICT_PATH = './eid2ename_dict.pkl'


def print_e_name():
    print_str = '机器人内置的识别码和对应设备名称列表如下：\n'
    try:
        with open(DICT_PATH, 'rb') as fp:
            eid2name = pickle.load(fp)
    except EOFError:
        return 'Error: eid2name need a init.'
    for k, v in M2EID.items():
        print_str += '{} - {} (id: {})\n'.format(k, eid2name.get(v), v)
    return print_str


async def get_e_name(eid: str):
    try:
        with open(DICT_PATH, 'rb') as fp:
            eid2name = pickle.load(fp)
    except (EOFError, FileNotFoundError):
        eid2name = {}
    if eid2name.get(eid) is not None:
        return eid2name.get(eid)
    else:
        response = requests.get(url=URL_DETAIL, headers=headers, params=f'equipmentId={eid}').text
        tree = etree.HTML(response)
        equipment_name = tree.xpath('/html/body/div[1]/div[1]/span/span[1]/text()')
        if len(equipment_name) > 0:
            equipment_name = equipment_name[0]
            eid2name[eid] = equipment_name
            with open(DICT_PATH, 'wb') as fp:
                pickle.dump(eid2name, fp)
            return equipment_name
        else:
            return None

