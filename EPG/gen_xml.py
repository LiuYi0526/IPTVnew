# -*- coding:utf-8 -*-
import datetime
import pytz
import html
import asyncio
import logging
from cctv import *
from tvmao import *
from nowtv import *
from mod import *
from tbc import *
from jxgdw import *
from epgpw import *
from ntdtv import *
from ettvamerica import *
from fourgtv import *
from tdm import *
from homeplus import *
from suntv import *
from xjtvs import *
from hami import *
import xml.etree.ElementTree as ET
from xml.dom import minidom

beijing_tz = pytz.timezone('Asia/Shanghai')

async def get_epgs(c):
    logging.info(c)
    epgs = []
    times = 0
    success = '✅'
    if c['source'] == 'cctv':
        for get_days in range(-6, 2):  # 7+1天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_cctv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    if c['source'] == 'tvmao':
        for get_days in range(-6, 2):  # 7+1天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_tvmao(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    if c['source'] == 'xjtvs':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_xjtvs(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    if c['source'] == 'nowtv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_nowtv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'mod':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_mod(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'hami':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_hami(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    if c['source'] == 'ETTVAmerica':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_ettvamerica(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    if c['source'] == 'tdm':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_tdm(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'tbc':
        while times < 5:
            ret = await get_epgs_tbc(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'jxgdw':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_jxgdw(c, need_date)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'epg.pw':
        while times < 5:
            ret = await get_epgs_epgpw(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'ntdtv':
        while times < 5:
            ret = await get_epgs_ntdtv(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'suntv':
        while times < 5:
            ret = await get_epgs_suntv(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == '4gtv':
        while times < 5:
            ret = await get_epgs_4gtv(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'homeplus':
        while times < 5:
            ret = await get_epgs_homeplus(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    return epgs, f"|{c['id']}|{c['name']}|{success}|\n"


async def gen_xml(channels, filename):
    tz = ' +0800'
    # tasks = [get_epgs(c) for c in channels]
    # epgs0 = await asyncio.gather(*tasks)
    epgs0 = []
    for c in channels:
        logging.info(c)
        epgs0.append(await get_epgs(c))
    epgs = []
    README = ['|tvg-id|tvg-name|EPG状态|\n', '|:---:|:---:|:---:|\n']
    for i, text in epgs0:
        README.append(text)
        for k in i:
            epgs.append(k)
    f = open('README.md', 'w', encoding='utf-8')
    f.writelines(README)
    f.close()
    tv = ET.Element('tv')
    for channel in channels:
        channel_element = ET.SubElement(tv, 'channel', {'id': channel['id']})
        display_name_element = ET.SubElement(channel_element, 'display-name')
        display_name_element.text = channel["name"]
    for epg in epgs:
        # print(epg)
        start = epg['starttime'].astimezone(tz=beijing_tz).strftime('%Y%m%d%H%M%S') + tz
        end = epg['endtime'].astimezone(tz=beijing_tz).strftime('%Y%m%d%H%M%S') + tz
        programme_element = ET.SubElement(tv, 'programme', {
            'start': start,
            'stop': end,
            'channel': epg['channel_id']
        })
        title_element = ET.SubElement(programme_element, 'title')
        title_element.text = epg['title']
        desc_element = ET.SubElement(programme_element, 'desc')
        desc_element.text = epg["desc"]
    xml_str = ET.tostring(tv, encoding='utf-8', method='xml').decode()
    xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_str)


if __name__ == '__main__':
    channels = [{'id': 'hami_OTT_LIVE_0000001853', 'name': '愛爾達體育MAX1台', 'id0': 'OTT_LIVE_0000001853', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001854', 'name': '愛爾達體育MAX2台', 'id0': 'OTT_LIVE_0000001854', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001855', 'name': '愛爾達體育MAX3台', 'id0': 'OTT_LIVE_0000001855', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001856', 'name': '愛爾達體育MAX4台', 'id0': 'OTT_LIVE_0000001856', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001744', 'name': '愛爾達體育1台', 'id0': 'OTT_LIVE_0000001744', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001743', 'name': '愛爾達體育2台', 'id0': 'OTT_LIVE_0000001743', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001745', 'name': '愛爾達體育3台', 'id0': 'OTT_LIVE_0000001745', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002055', 'name': '愛爾達體育4台', 'id0': 'OTT_LIVE_0000002055', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002017', 'name': 'Hami大聯盟台', 'id0': 'OTT_LIVE_0000002017', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001830', 'name': 'Hami 羽球台', 'id0': 'OTT_LIVE_0000001830', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002087', 'name': 'Hami 日漫台(免費)', 'id0': 'OTT_LIVE_0000002087', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001573', 'name': '愛爾達綜合台', 'id0': 'OTT_LIVE_0000001573', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001561', 'name': 'TVBS', 'id0': 'OTT_LIVE_0000001561', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001568', 'name': '中視', 'id0': 'OTT_LIVE_0000001568', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001541', 'name': '中視菁采台', 'id0': 'OTT_LIVE_0000001541', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001519', 'name': '台視', 'id0': 'OTT_LIVE_0000001519', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001790', 'name': '台視綜合台', 'id0': 'OTT_LIVE_0000001790', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001579', 'name': '民視台灣台', 'id0': 'OTT_LIVE_0000001579', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001534', 'name': '民視無線台', 'id0': 'OTT_LIVE_0000001534', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001535', 'name': '民視第一台', 'id0': 'OTT_LIVE_0000001535', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001825', 'name': '華藝 MBC 綜合台', 'id0': 'OTT_LIVE_0000001825', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001526', 'name': '華視', 'id0': 'OTT_LIVE_0000001526', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001652', 'name': '靖天日本台', 'id0': 'OTT_LIVE_0000001652', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001518', 'name': '愛爾達娛樂台', 'id0': 'OTT_LIVE_0000001518', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001757', 'name': 'Mezzo Live', 'id0': 'OTT_LIVE_0000001757', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001758', 'name': 'Trace Urban', 'id0': 'OTT_LIVE_0000001758', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001559', 'name': 'TVBS 歡樂台', 'id0': 'OTT_LIVE_0000001559', 'source': 'hami'},
#                {'id': 'hami_OTT_LIVE_0000001789', 'name': 'TVBS 精采台', 'id0': 'OTT_LIVE_0000001789', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001528', 'name': '八大精彩台', 'id0': 'OTT_LIVE_0000001528', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001549', 'name': '八大綜藝台', 'id0': 'OTT_LIVE_0000001549', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001539', 'name': '古典音樂台', 'id0': 'OTT_LIVE_0000001539', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001550', 'name': '民視綜藝台', 'id0': 'OTT_LIVE_0000001550', 'source': 'hami'},
#                {'id': 'hami_OTT_LIVE_0000001548', 'name': '豬哥亮歌廳秀', 'id0': 'OTT_LIVE_0000001548', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001938', 'name': '電影原聲台 CMusic', 'id0': 'OTT_LIVE_0000001938', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001517', 'name': '愛爾達影劇台', 'id0': 'OTT_LIVE_0000001517', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002079', 'name': '愛爾達日韓台', 'id0': 'OTT_LIVE_0000002079', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002073', 'name': 'Hami 韓劇台', 'id0': 'OTT_LIVE_0000002073', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001546', 'name': 'amc 電影台', 'id0': 'OTT_LIVE_0000001546', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001710', 'name': 'CatchPlay 電影台', 'id0': 'OTT_LIVE_0000001710', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002005', 'name': 'Rock Action', 'id0': 'OTT_LIVE_0000002005', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001860', 'name': 'Rock Entertainment', 'id0': 'OTT_LIVE_0000001860', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001861', 'name': 'Rock Extreme', 'id0': 'OTT_LIVE_0000001861', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001884', 'name': 'tvN', 'id0': 'OTT_LIVE_0000001884', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001888', 'name': 'Warner TV', 'id0': 'OTT_LIVE_0000001888', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001566', 'name': '中視經典台', 'id0': 'OTT_LIVE_0000001566', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001555', 'name': '公視戲劇台', 'id0': 'OTT_LIVE_0000001555', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001689', 'name': '影迷數位電影台', 'id0': 'OTT_LIVE_0000001689', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001551', 'name': '民視影劇台', 'id0': 'OTT_LIVE_0000001551', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001635', 'name': '采昌影劇台', 'id0': 'OTT_LIVE_0000001635', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001915', 'name': '金光布袋戲', 'id0': 'OTT_LIVE_0000001915', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001904', 'name': '龍華偶像', 'id0': 'OTT_LIVE_0000001904', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001542', 'name': '龍華影劇', 'id0': 'OTT_LIVE_0000001542', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001839', 'name': '龍華戲劇', 'id0': 'OTT_LIVE_0000001839', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001840', 'name': '龍華電影', 'id0': 'OTT_LIVE_0000001840', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002098', 'name': '龍華洋片台', 'id0': 'OTT_LIVE_0000002098', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001845', 'name': '博斯運動一台', 'id0': 'OTT_LIVE_0000001845', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001903', 'name': '博斯網球台', 'id0': 'OTT_LIVE_0000001903', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001972', 'name': '博斯魅力網', 'id0': 'OTT_LIVE_0000001972', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001846', 'name': '博斯高球一台', 'id0': 'OTT_LIVE_0000001846', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001882', 'name': '博斯無限台', 'id0': 'OTT_LIVE_0000001882', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001973', 'name': '博斯無限二台', 'id0': 'OTT_LIVE_0000001973', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001850', 'name': 'Ginx TV 電競頻道', 'id0': 'OTT_LIVE_0000001850', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001771', 'name': 'Eurosport', 'id0': 'OTT_LIVE_0000001771', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002056', 'name': 'INULTRA', 'id0': 'OTT_LIVE_0000002056', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001766', 'name': 'TechStorm', 'id0': 'OTT_LIVE_0000001766', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001759', 'name': 'Trace Sport Stars', 'id0': 'OTT_LIVE_0000001759', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002087', 'name': 'Hami 日漫台(免費)', 'id0': 'OTT_LIVE_0000002087', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001711', 'name': 'BBC Cbeebies', 'id0': 'OTT_LIVE_0000001711', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001889', 'name': 'Cartoonito', 'id0': 'OTT_LIVE_0000001889', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002002', 'name': 'CN 卡通頻道', 'id0': 'OTT_LIVE_0000002002', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001836', 'name': 'DreamWorks 夢工廠動畫', 'id0': 'OTT_LIVE_0000001836', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001914', 'name': 'LiveABC 互動英語頻道', 'id0': 'OTT_LIVE_0000001914', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001865', 'name': 'MOMO 親子台', 'id0': 'OTT_LIVE_0000001865', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001939', 'name': 'Nick Jr.', 'id0': 'OTT_LIVE_0000001939', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001851', 'name': '尼克兒童頻道', 'id0': 'OTT_LIVE_0000001851', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001520', 'name': '愛放 ifun 動漫台', 'id0': 'OTT_LIVE_0000001520', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001553', 'name': '空中英語教室', 'id0': 'OTT_LIVE_0000001553', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001547', 'name': '達文西頻道', 'id0': 'OTT_LIVE_0000001547', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002039', 'name': 'Asian Food Network 亞洲美食頻道', 'id0': 'OTT_LIVE_0000002039', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001510', 'name': 'BBC Earth', 'id0': 'OTT_LIVE_0000001510', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001513', 'name': 'BBC Lifestyle', 'id0': 'OTT_LIVE_0000001513', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001924', 'name': 'Discovery Asia', 'id0': 'OTT_LIVE_0000001924', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001514', 'name': 'Discovery DMAX', 'id0': 'OTT_LIVE_0000001514', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001511', 'name': 'Discovery EVE', 'id0': 'OTT_LIVE_0000001511', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001512', 'name': 'Discovery Science', 'id0': 'OTT_LIVE_0000001512', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001971', 'name': 'Global Trekker', 'id0': 'OTT_LIVE_0000001971', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001901', 'name': 'HGTV 居家樂活頻道', 'id0': 'OTT_LIVE_0000001901', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001970', 'name': 'Lifetime', 'id0': 'OTT_LIVE_0000001970', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001867', 'name': 'Love Nature', 'id0': 'OTT_LIVE_0000001867', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001876', 'name': 'PET CLUB TV', 'id0': 'OTT_LIVE_0000001876', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001756', 'name': 'Travel Channel', 'id0': 'OTT_LIVE_0000001756', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002070', 'name': '亞洲旅遊台', 'id0': 'OTT_LIVE_0000002070', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001527', 'name': 'BBC NEWS', 'id0': 'OTT_LIVE_0000001527', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002015', 'name': 'Bloomberg TV', 'id0': 'OTT_LIVE_0000002015', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002003', 'name': 'CNN 國際新聞台', 'id0': 'OTT_LIVE_0000002003', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002004', 'name': 'CNN 頭條新聞台(HLN)', 'id0': 'OTT_LIVE_0000002004', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001974', 'name': 'NHK 新聞資訊台', 'id0': 'OTT_LIVE_0000001974', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001560', 'name': 'TVBS 新聞台', 'id0': 'OTT_LIVE_0000001560', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001516', 'name': '三立新聞台', 'id0': 'OTT_LIVE_0000001516', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001690', 'name': '三立 iNEWS', 'id0': 'OTT_LIVE_0000001690', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001562', 'name': '中天新聞台', 'id0': 'OTT_LIVE_0000001562', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001508', 'name': '中央氣象署影音頻道', 'id0': 'OTT_LIVE_0000001508', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001567', 'name': '中視新聞台', 'id0': 'OTT_LIVE_0000001567', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001565', 'name': '台視新聞台', 'id0': 'OTT_LIVE_0000001565', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001791', 'name': '台視財經台', 'id0': 'OTT_LIVE_0000001791', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002069', 'name': '寰宇新聞台', 'id0': 'OTT_LIVE_0000002069', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001564', 'name': '東森新聞台', 'id0': 'OTT_LIVE_0000001564', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001563', 'name': '東森財經台', 'id0': 'OTT_LIVE_0000001563', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001533', 'name': '民視新聞台', 'id0': 'OTT_LIVE_0000001533', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001569', 'name': '華視新聞資訊台', 'id0': 'OTT_LIVE_0000001569', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002006', 'name': '鏡電視新聞台', 'id0': 'OTT_LIVE_0000002006', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001649', 'name': '非凡商業台', 'id0': 'OTT_LIVE_0000001649', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001650', 'name': '非凡新聞台', 'id0': 'OTT_LIVE_0000001650', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001752', 'name': 'CNEX 紀實頻道', 'id0': 'OTT_LIVE_0000001752', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001859', 'name': 'History', 'id0': 'OTT_LIVE_0000001859', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000002019', 'name': '罪案偵緝頻道', 'id0': 'OTT_LIVE_0000002019', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001793', 'name': '人間衛視', 'id0': 'OTT_LIVE_0000001793', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001736', 'name': '國會頻道1', 'id0': 'OTT_LIVE_0000001736', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001735', 'name': '國會頻道2', 'id0': 'OTT_LIVE_0000001735', 'source': 'hami'},
                {'id': 'hami_OTT_LIVE_0000001538', 'name': '大愛電視', 'id0': 'OTT_LIVE_0000001538', 'source': 'hami'},
#                {'id': '4gtv_4gtv-4gtv003', 'name': '民視第一台', 'id0': '4gtv-4gtv003', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv001', 'name': '民視台灣台', 'id0': '4gtv-4gtv001', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv002', 'name': '民視', 'id0': '4gtv-4gtv002', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live007', 'name': '大愛電視', 'id0': '4gtv-live007', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv040', 'name': '中視', 'id0': '4gtv-4gtv040', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv080', 'name': '中視經典台', 'id0': '4gtv-4gtv080', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv041', 'name': '華視', 'id0': '4gtv-4gtv041', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live207', 'name': '三立綜合台', 'id0': '4gtv-live207', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv043', 'name': '客家電視台', 'id0': '4gtv-4gtv043', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv039', 'name': '八大綜藝台', 'id0': '4gtv-4gtv039', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv064', 'name': '中視菁采台', 'id0': '4gtv-4gtv064', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv067', 'name': 'TVBS精采台', 'id0': '4gtv-4gtv067', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv070', 'name': '愛爾達娛樂台', 'id0': '4gtv-4gtv070', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv046', 'name': '靖天綜合台', 'id0': '4gtv-4gtv046', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv047', 'name': '靖天日本台', 'id0': '4gtv-4gtv047', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live050', 'name': '新唐人亞太台', 'id0': '4gtv-live050', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv079', 'name': 'ARIRANG阿里郎頻道', 'id0': '4gtv-4gtv079', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live112', 'name': 'Global Trekker', 'id0': '4gtv-live112', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live014', 'name': '原住民族電視台', 'id0': '4gtv-live014', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn19', 'name': 'Smart知識台', 'id0': 'litv-longturn19', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live049', 'name': '東森購物四台', 'id0': '4gtv-live049', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live030', 'name': 'LiveABC互動英語頻道', 'id0': '4gtv-live030', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv018', 'name': '達文西頻道', 'id0': '4gtv-4gtv018', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn20', 'name': 'ELTV生活英語台', 'id0': 'litv-longturn20', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live032', 'name': 'Nick Jr. 兒童頻道', 'id0': '4gtv-live032', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live105', 'name': '尼克兒童頻道', 'id0': '4gtv-live105', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live017', 'name': 'DreamWorks 夢工廠動畫', 'id0': '4gtv-live017', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv044', 'name': '靖天卡通台', 'id0': '4gtv-4gtv044', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv057', 'name': '靖洋卡通Nice Bingo', 'id0': '4gtv-4gtv057', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv15', 'name': 'i-Fun動漫台', 'id0': 'litv-ftv15', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn01', 'name': '龍華卡通台', 'id0': 'litv-longturn01', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live107', 'name': 'MOMO親子台', 'id0': '4gtv-live107', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live047', 'name': '東森購物一台', 'id0': '4gtv-live047', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv075', 'name': '鏡電視新聞台', 'id0': '4gtv-4gtv075', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv152', 'name': '東森新聞台', 'id0': '4gtv-4gtv152', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv052', 'name': '華視新聞', 'id0': '4gtv-4gtv052', 'source': '4gtv'},
#                {'id': '4gtv_litv-ftv13', 'name': '民視新聞台', 'id0': 'litv-ftv13', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live089', 'name': '三立新聞iNEWS', 'id0': '4gtv-live089', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv072', 'name': 'TVBS新聞', 'id0': '4gtv-4gtv072', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv153', 'name': '東森財經新聞台', 'id0': '4gtv-4gtv153', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv074', 'name': '中視新聞', 'id0': '4gtv-4gtv074', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv009', 'name': '中天新聞台', 'id0': '4gtv-4gtv009', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live059', 'name': 'Bloomberg TV', 'id0': '4gtv-live059', 'source': '4gtv'},
#                {'id': '4gtv_litv-longturn14', 'name': '寰宇新聞台', 'id0': 'litv-longturn14', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn15', 'name': '寰宇新聞台灣台', 'id0': 'litv-longturn15', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live060', 'name': 'SBN全球財經台', 'id0': '4gtv-live060', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn23', 'name': '寰宇財經台', 'id0': 'litv-longturn23', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv073', 'name': 'TVBS', 'id0': '4gtv-4gtv073', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live046', 'name': '東森購物二台', 'id0': '4gtv-live046', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv004', 'name': '民視綜藝台', 'id0': '4gtv-4gtv004', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv006', 'name': '豬哥亮歌廳秀', 'id0': '4gtv-4gtv006', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv062', 'name': '靖天育樂台', 'id0': '4gtv-4gtv062', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv063', 'name': 'KLT-靖天國際台', 'id0': '4gtv-4gtv063', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv054', 'name': 'Nice TV 靖天歡樂台', 'id0': '4gtv-4gtv054', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv065', 'name': '靖天資訊台', 'id0': '4gtv-4gtv065', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv068', 'name': 'TVBS歡樂台', 'id0': '4gtv-4gtv068', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live377', 'name': '韓國娛樂台 KMTV', 'id0': '4gtv-live377', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live080', 'name': 'ROCK Entertainment', 'id0': '4gtv-live080', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live029', 'name': 'Lifetime 娛樂頻道', 'id0': '4gtv-live029', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live031', 'name': '電影原聲台CMusic', 'id0': '4gtv-live031', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv082', 'name': 'TRACE Urban', 'id0': '4gtv-4gtv082', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live025', 'name': 'MTV Live HD 音樂頻道', 'id0': '4gtv-live025', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv083', 'name': 'Mezzo Live HD', 'id0': '4gtv-4gtv083', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv059', 'name': 'CLASSICA 古典樂', 'id0': '4gtv-4gtv059', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live048', 'name': '東森購物三台', 'id0': '4gtv-live048', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn05', 'name': '博斯高球台', 'id0': 'litv-longturn05', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn06', 'name': '博斯高球二台', 'id0': 'litv-longturn06', 'source': '4gtv'},
#                {'id': '4gtv_litv-longturn07', 'name': '博斯運動一台', 'id0': 'litv-longturn07', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn10', 'name': '博斯無限台', 'id0': 'litv-longturn10', 'source': '4gtv'},
#                {'id': '4gtv_litv-longturn09', 'name': '博斯網球台', 'id0': 'litv-longturn09', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn08', 'name': '博斯運動二台', 'id0': 'litv-longturn08', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn04', 'name': '博斯魅力台', 'id0': 'litv-longturn04', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv077', 'name': 'TRACE Sport Stars', 'id0': '4gtv-4gtv077', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv101', 'name': '智林體育台', 'id0': '4gtv-4gtv101', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv014', 'name': '時尚運動X', 'id0': '4gtv-4gtv014', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live201', 'name': '車迷TV', 'id0': '4gtv-live201', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv053', 'name': 'GINX Esports TV', 'id0': '4gtv-4gtv053', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live109', 'name': 'TechStorm', 'id0': '4gtv-live109', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live110', 'name': 'Pet Club TV', 'id0': '4gtv-live110', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv07', 'name': '民視旅遊台', 'id0': 'litv-ftv07', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live012', 'name': '滾動力rollor', 'id0': '4gtv-live012', 'source': '4gtv'},
#                {'id': '4gtv_litv-longturn17', 'name': '亞洲旅遊台', 'id0': 'litv-longturn17', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live011', 'name': 'fun探索娛樂台', 'id0': '4gtv-live011', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live206', 'name': '幸福空間居家台', 'id0': '4gtv-live206', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live208', 'name': 'Love Nature', 'id0': '4gtv-live208', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live026', 'name': 'History 歷史頻道', 'id0': '4gtv-live026', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live120', 'name': '愛爾達生活旅遊台', 'id0': '4gtv-live120', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live121', 'name': 'LUXE TV Channel', 'id0': '4gtv-live121', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live122', 'name': 'TV5MONDE STYLE HD 生活時尚', 'id0': '4gtv-live122', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn12', 'name': '龍華偶像台', 'id0': 'litv-longturn12', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv042', 'name': '公視戲劇', 'id0': '4gtv-4gtv042', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv09', 'name': '民視影劇台', 'id0': 'litv-ftv09', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn18', 'name': '龍華戲劇台', 'id0': 'litv-longturn18', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live620', 'name': 'HITS頻道', 'id0': '4gtv-live620', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn11', 'name': '龍華日韓台', 'id0': 'litv-longturn11', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv034', 'name': '八大精彩台', 'id0': '4gtv-4gtv034', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live145', 'name': '霹靂布袋戲', 'id0': '4gtv-live145', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv058', 'name': '靖天戲劇台', 'id0': '4gtv-4gtv058', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv045', 'name': '靖洋戲劇台', 'id0': '4gtv-4gtv045', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live027', 'name': 'CI 罪案偵查頻道', 'id0': '4gtv-live027', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv013', 'name': '視納華仁紀實頻道', 'id0': '4gtv-4gtv013', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live023', 'name': '影迷數位紀實台', 'id0': '4gtv-live023', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live144', 'name': '金光布袋戲', 'id0': '4gtv-live144', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live138', 'name': 'ROCK Action', 'id0': '4gtv-live138', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv049', 'name': '采昌影劇台', 'id0': '4gtv-4gtv049', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv055', 'name': '靖天映畫', 'id0': '4gtv-4gtv055', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv061', 'name': '靖天電影台', 'id0': '4gtv-4gtv061', 'source': '4gtv'},
                {'id': '4gtv_litv-longturn03', 'name': '龍華電影台', 'id0': 'litv-longturn03', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv011', 'name': '影迷數位電影台', 'id0': '4gtv-4gtv011', 'source': '4gtv'},
                {'id': '4gtv_4gtv-4gtv017', 'name': 'amc電影台', 'id0': '4gtv-4gtv017', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live069', 'name': 'CinemaWorld', 'id0': '4gtv-live069', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live157', 'name': 'My Cinema Europe HD 我的歐洲電影', 'id0': '4gtv-live157', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv17', 'name': '好消息2台', 'id0': 'litv-ftv17', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv16', 'name': '好消息', 'id0': 'litv-ftv16', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live106', 'name': '大愛二台', 'id0': '4gtv-live106', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-live008', 'name': '人間衛視', 'id0': '4gtv-live008', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live146', 'name': 'FRANCE24 英文台', 'id0': '4gtv-live146', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv10', 'name': '半島國際新聞台', 'id0': 'litv-ftv10', 'source': '4gtv'},
                {'id': '4gtv_litv-ftv03', 'name': 'VOA美國之音', 'id0': 'litv-ftv03', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live130', 'name': 'CNBC Asia 財經台', 'id0': '4gtv-live130', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live071', 'name': 'DW德國之聲', 'id0': '4gtv-live071', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv084', 'name': '國會頻道1', 'id0': '4gtv-4gtv084', 'source': '4gtv'},
#                {'id': '4gtv_4gtv-4gtv085', 'name': '國會頻道2', 'id0': '4gtv-4gtv085', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live087', 'name': 'TVBS綜藝台', 'id0': '4gtv-live087', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live088', 'name': 'TVBS台劇台', 'id0': '4gtv-live088', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live021', 'name': '經典電影台', 'id0': '4gtv-live021', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live022', 'name': '經典卡通台', 'id0': '4gtv-live022', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live009', 'name': '兒童卡通台', 'id0': '4gtv-live009', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live024', 'name': '精選動漫台', 'id0': '4gtv-live024', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live010', 'name': '戲劇免費看 1台', 'id0': '4gtv-live010', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live006', 'name': '戲劇免費看 2台', 'id0': '4gtv-live006', 'source': '4gtv'},
                {'id': '4gtv_4gtv-live005', 'name': '電影免費看 2台', 'id0': '4gtv-live005', 'source': '4gtv'},
                {'id': 'tdm_1', 'name': '澳視澳門 Ch. 91', 'id0': '1', 'source': 'tdm'},
                {'id': 'tdm_2', 'name': '澳視葡文 Ch. 92', 'id0': '2', 'source': 'tdm'},
                {'id': 'tdm_3', 'name': '澳門電台 FM100.7', 'id0': '3', 'source': 'tdm'},
                {'id': 'tdm_4', 'name': 'Rádio Macau FM98', 'id0': '4', 'source': 'tdm'},
                {'id': 'tdm_5', 'name': '澳門資訊 Ch.94', 'id0': '5', 'source': 'tdm'},
                {'id': 'tdm_6', 'name': '澳門體育 Ch.93', 'id0': '6', 'source': 'tdm'},
                {'id': 'tdm_7', 'name': '澳門綜藝 Ch.95', 'id0': '7', 'source': 'tdm'},
                {'id': 'tdm_8', 'name': '澳門 - MACAU 衛星頻道 Ch.96', 'id0': '8', 'source': 'tdm'}
                ]
    asyncio.run(gen_xml(channels, 'EPG.xml'))
