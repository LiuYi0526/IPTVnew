# -*- coding:utf-8 -*-
import datetime
import pytz
import asyncio
import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom
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
from mytvsuper import *
from cctvplus import *
from hoy import *
from litv import *
from cctv6m1905 import *

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
    elif c['source'] == 'tvmao':
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
    elif c['source'] == 'xjtvs':
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
    elif c['source'] == 'nowtv':
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
    elif c['source'] == 'ETTVAmerica':
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
    elif c['source'] == 'tdm':
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
    elif c['source'] == 'mytvsuper':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_mytvsuper(c, need_date)
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
    elif c['source'] == 'cctvplus':
        while times < 5:
            ret = await get_epgs_cctvplus(c)
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
    elif c['source'] == 'hoy':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_hoy(c, need_date)
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
    elif c['source'] == 'litv':
        while times < 5:
            ret = await get_epgs_litv(c)
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
    elif c['source'] == '1905':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_1905(c, need_date)
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
    asyncio.run(download_litv_epgs())
    channels = [
        {'id': 'cctv_cctv1', 'name': 'CCTV-1 综合', 'id0': 'cctv1', 'source': 'cctv'},
        {'id': 'cctv_cctv2', 'name': 'CCTV-2 财经', 'id0': 'cctv2', 'source': 'cctv'},
        {'id': 'cctv_cctv3', 'name': 'CCTV-3 综艺', 'id0': 'cctv3', 'source': 'cctv'},
        {'id': 'cctv_cctv4', 'name': 'CCTV-4 (亚洲)', 'id0': 'cctv4', 'source': 'cctv'},
        {'id': 'cctv_cctv5', 'name': 'CCTV-5 体育', 'id0': 'cctv5', 'source': 'cctv'},
        {'id': 'cctv_cctv6', 'name': 'CCTV-6 电影', 'id0': 'cctv6', 'source': 'cctv'},
        {'id': 'cctv_cctv7', 'name': 'CCTV-7 国防军事', 'id0': 'cctv7', 'source': 'cctv'},
        {'id': 'cctv_cctv8', 'name': 'CCTV-8 电视剧', 'id0': 'cctv8', 'source': 'cctv'},
        {'id': 'cctv_cctvjilu', 'name': 'CCTV-9 纪录', 'id0': 'cctvjilu', 'source': 'cctv'},
        {'id': 'cctv_cctv10', 'name': 'CCTV-10 科教', 'id0': 'cctv10', 'source': 'cctv'},
        {'id': 'cctv_cctv11', 'name': 'CCTV-11 戏曲', 'id0': 'cctv11', 'source': 'cctv'},
        {'id': 'cctv_cctv12', 'name': 'CCTV-12 社会与法', 'id0': 'cctv12', 'source': 'cctv'},
        {'id': 'cctv_cctv13', 'name': 'CCTV-13 新闻', 'id0': 'cctv13', 'source': 'cctv'},
        {'id': 'cctv_cctvchild', 'name': 'CCTV-14 少儿', 'id0': 'cctvchild', 'source': 'cctv'},
        {'id': 'cctv_cctv15', 'name': 'CCTV-15 音乐', 'id0': 'cctv15', 'source': 'cctv'},
        {'id': 'cctv_cctv5plus', 'name': 'CCTV-5+ 体育赛事', 'id0': 'cctv5plus', 'source': 'cctv'},
        {'id': 'cctv_cctv16', 'name': 'CCTV-16奥林匹克', 'id0': 'cctv16', 'source': 'cctv'},
        {'id': 'cctv_cctv17', 'name': 'CCTV-17农业农村', 'id0': 'cctv17', 'source': 'cctv'},
        {'id': 'cctv_cctveurope', 'name': 'CCTV-4 (欧洲)', 'id0': 'cctveurope', 'source': 'cctv'},
        {'id': 'cctv_cctvamerica', 'name': 'CCTV-4 (美洲)', 'id0': 'cctvamerica', 'source': 'cctv'},
        {'id': 'cctvplus_channel1', 'name': 'CCTV+ Channel 1', 'id0': 'channel1', 'source': 'cctvplus'},
        {'id': 'cctvplus_channel2', 'name': 'CCTV+ Channel 2', 'id0': 'channel2', 'source': 'cctvplus'},
        {'id': 'cctvplus_channel3', 'name': 'CCTV+ Channel 3', 'id0': 'channel3', 'source': 'cctvplus'},
        {'id': 'cctvplus_channel4', 'name': 'CCTV+ Channel 4', 'id0': 'channel4', 'source': 'cctvplus'},
        {'id': 'tvmao_NANCHANG-NANCHANG1', 'name': '南昌电视台新闻综合频道', 'id0': 'NANCHANG-NANCHANG1', 'source': 'tvmao'},
        {'id': 'tvmao_NANCHANG-NANCHANG4', 'name': '南昌电视台都市频道', 'id0': 'NANCHANG-NANCHANG4', 'source': 'tvmao'},
        {'id': 'tvmao_NANCHANG-NANCHANG3', 'name': '南昌电视台资讯频道', 'id0': 'NANCHANG-NANCHANG3', 'source': 'tvmao'},
        {'id': '1905_xl', 'name': '初秋·电影放映厅', 'id0': 'xl', 'source': '1905'},
        {'id': '1905_1905tv', 'name': '环球经典', 'id0': '1905tv', 'source': '1905'},
        {'id': 'jxgdw_87', 'name': '江西卫视', 'id0': '87', 'source': 'jxgdw'},
        {'id': 'jxgdw_86', 'name': '都市频道', 'id0': '86', 'source': 'jxgdw'},
        {'id': 'jxgdw_153', 'name': '经济生活', 'id0': '153', 'source': 'jxgdw'},
        {'id': 'jxgdw_84', 'name': '影视旅游', 'id0': '84', 'source': 'jxgdw'},
        {'id': 'jxgdw_83', 'name': '公共农业', 'id0': '83', 'source': 'jxgdw'},
        {'id': 'jxgdw_82', 'name': '少儿频道', 'id0': '82', 'source': 'jxgdw'},
        {'id': 'jxgdw_81', 'name': '新闻频道', 'id0': '81', 'source': 'jxgdw'},
        {'id': 'jxgdw_112', 'name': '移动电视', 'id0': '112', 'source': 'jxgdw'},
        {'id': 'jxgdw_78', 'name': '陶瓷频道', 'id0': '78', 'source': 'jxgdw'},
        {'id': 'jxgdw_79', 'name': '风尚购物', 'id0': '79', 'source': 'jxgdw'},
        {'id': 'XJTV-1', 'name': 'XJTV-1', 'id0': '1', 'source': 'xjtvs'},
        {'id': 'XJTV-2', 'name': 'XJTV-2', 'id0': '3', 'source': 'xjtvs'},
        {'id': 'XJTV-3', 'name': 'XJTV-3', 'id0': '4', 'source': 'xjtvs'},
        {'id': 'XJTV-4', 'name': 'XJTV-4', 'id0': '16', 'source': 'xjtvs'},
        {'id': 'XJTV-5', 'name': 'XJTV-5', 'id0': '17', 'source': 'xjtvs'},
        {'id': 'XJTV-7', 'name': 'XJTV-7', 'id0': '21', 'source': 'xjtvs'},
        {'id': 'XJTV-8', 'name': 'XJTV-8', 'id0': '23', 'source': 'xjtvs'},
        {'id': 'RTHK_31', 'name': '港台電視31', 'id0': '368550', 'source': 'epg.pw'},
        {'id': 'RTHK_32', 'name': '港台電視32', 'id0': '368551', 'source': 'epg.pw'},
        {'id': 'RTHK_33', 'name': '港台電視33', 'id0': '368552', 'source': 'epg.pw'},
        {'id': 'RTHK_34', 'name': '港台電視34', 'id0': '368553', 'source': 'epg.pw'},
        {'id': 'RTHK_35', 'name': '港台電視35', 'id0': '368554', 'source': 'epg.pw'},
        {'id': 'HOY_76', 'name': 'HOY 國際財經台', 'id0': '76', 'source': 'hoy'},
        {'id': 'HOY_77', 'name': 'HOY TV', 'id0': '77', 'source': 'hoy'},
        {'id': 'HOY_78', 'name': 'HOY TV 資訊台', 'id0': '78', 'source': 'hoy'},
        {'id': 'nowtv_96', 'name': 'ViuTVsix', 'id0': '96', 'source': 'nowtv'},
        {'id': 'nowtv_99', 'name': 'ViuTV', 'id0': '99', 'source': 'nowtv'},
        {'id': 'nowtv_102', 'name': 'Viu 頻道', 'id0': '102', 'source': 'nowtv'},
        {'id': 'nowtv_105', 'name': 'Now華劇台', 'id0': '105', 'source': 'nowtv'},
        {'id': 'nowtv_108', 'name': 'NowJelli', 'id0': '108', 'source': 'nowtv'},
        {'id': 'nowtv_111', 'name': 'HBO Hits', 'id0': '111', 'source': 'nowtv'},
        {'id': 'nowtv_112', 'name': 'HBO Family', 'id0': '112', 'source': 'nowtv'},
        {'id': 'nowtv_113', 'name': 'CINEMAX', 'id0': '113', 'source': 'nowtv'},
        {'id': 'nowtv_114', 'name': 'HBO Signature', 'id0': '114', 'source': 'nowtv'},
        {'id': 'nowtv_115', 'name': 'HBO', 'id0': '115', 'source': 'nowtv'},
        {'id': 'nowtv_116', 'name': 'MOVIE MOVIE', 'id0': '116', 'source': 'nowtv'},
        {'id': 'nowtv_133', 'name': 'Now 爆谷台', 'id0': '133', 'source': 'nowtv'},
        {'id': 'nowtv_138', 'name': 'Now爆谷星影台', 'id0': '138', 'source': 'nowtv'},
        {'id': 'nowtv_162', 'name': '東森亞洲衛視', 'id0': '162', 'source': 'nowtv'},
        {'id': 'nowtv_218', 'name': 'Love Nature 4K', 'id0': '218', 'source': 'nowtv'},
        {'id': 'nowtv_316', 'name': 'CNN 國際新聞網絡', 'id0': '316', 'source': 'nowtv'},
        {'id': 'nowtv_329', 'name': 'RT', 'id0': '329', 'source': 'nowtv'},
        {'id': 'nowtv_331', 'name': 'Now直播台', 'id0': '331', 'source': 'nowtv'},
        {'id': 'nowtv_332', 'name': 'Now新聞台', 'id0': '332', 'source': 'nowtv'},
        {'id': 'nowtv_333', 'name': 'Now財經台', 'id0': '333', 'source': 'nowtv'},
        {'id': 'nowtv_366', 'name': '鳳凰衛視資訊台', 'id0': '366', 'source': 'nowtv'},
        {'id': 'nowtv_371', 'name': '東森亞洲新聞台', 'id0': '371', 'source': 'nowtv'},
        {'id': 'nowtv_538', 'name': '中天亞洲台', 'id0': '538', 'source': 'nowtv'},
        {'id': 'nowtv_611', 'name': 'Now Sports 4K 1', 'id0': '611', 'source': 'nowtv'},
        {'id': 'nowtv_621', 'name': 'Now Sports 英超1台', 'id0': '621', 'source': 'nowtv'},
        {'id': 'nowtv_622', 'name': 'Now Sports 英超2台', 'id0': '622', 'source': 'nowtv'},
        {'id': 'nowtv_623', 'name': 'Now Sports 英超3台', 'id0': '623', 'source': 'nowtv'},
        {'id': 'nowtv_624', 'name': 'Now Sports 英超4台', 'id0': '624', 'source': 'nowtv'},
        {'id': 'nowtv_625', 'name': 'Now Sports 英超5台', 'id0': '625', 'source': 'nowtv'},
        {'id': 'nowtv_626', 'name': 'Now Sports 英超6台', 'id0': '626', 'source': 'nowtv'},
        {'id': 'nowtv_627', 'name': 'Now Sports 英超7台', 'id0': '627', 'source': 'nowtv'},
        {'id': 'nowtv_630', 'name': 'Now Sports 精選', 'id0': '630', 'source': 'nowtv'},
        {'id': 'nowtv_631', 'name': 'Now Sports 1', 'id0': '631', 'source': 'nowtv'},
        {'id': 'nowtv_632', 'name': 'Now Sports 2', 'id0': '632', 'source': 'nowtv'},
        {'id': 'nowtv_633', 'name': 'Now Sports 3', 'id0': '633', 'source': 'nowtv'},
        {'id': 'nowtv_634', 'name': 'Now Sports 4', 'id0': '634', 'source': 'nowtv'},
        {'id': 'nowtv_635', 'name': 'Now Sports 5', 'id0': '635', 'source': 'nowtv'},
        {'id': 'nowtv_636', 'name': 'Now Sports 6', 'id0': '636', 'source': 'nowtv'},
        {'id': 'nowtv_637', 'name': 'Now Sports 7', 'id0': '637', 'source': 'nowtv'},
        {'id': 'nowtv_638', 'name': 'beIN SPORTS 1', 'id0': '638', 'source': 'nowtv'},
        {'id': 'nowtv_639', 'name': 'beIN SPORTS 2', 'id0': '639', 'source': 'nowtv'},
        {'id': 'nowtv_641', 'name': 'Now Sports 641', 'id0': '641', 'source': 'nowtv'},
        {'id': 'nowtv_642', 'name': 'NBA TV', 'id0': '642', 'source': 'nowtv'},
        {'id': 'nowtv_643', 'name': 'beIN SPORTS 3', 'id0': '643', 'source': 'nowtv'},
        {'id': 'nowtv_680', 'name': 'Now Sports Plus', 'id0': '680', 'source': 'nowtv'},
        {'id': 'nowtv_683', 'name': 'Now Golf 2', 'id0': '683', 'source': 'nowtv'},
        {'id': 'nowtv_684', 'name': 'Now Golf 3', 'id0': '684', 'source': 'nowtv'},
        {'id': 'tvb_CWIN', 'name': 'SUPER FREE (免費)', 'id0': '368376', 'source': 'epg.pw'},
        {'id': 'tvb_SVAR', 'name': 'SUPER獎門人 (免費)', 'id0': '430854', 'source': 'epg.pw'},
        {'id': 'tvb_SEYT', 'name': 'SUPER EYT (免費)', 'id0': '430550', 'source': 'epg.pw'},
        {'id': 'tvb_SFOO', 'name': 'SUPER識食 (免費)', 'id0': '430554', 'source': 'epg.pw'},
        {'id': 'tvb_STRA', 'name': 'SUPER識嘆 (免費)', 'id0': '430552', 'source': 'epg.pw'},
        {'id': 'tvb_SMUS', 'name': 'SUPER Music (免費)', 'id0': '430553', 'source': 'epg.pw'},
        {'id': 'tvb_SGOL', 'name': 'SUPER金曲 (免費)', 'id0': '431161', 'source': 'epg.pw'},
        {'id': 'tvb_SSIT', 'name': 'SUPER煲劇 (免費)', 'id0': '430551', 'source': 'epg.pw'},
        {'id': 'tvb_STVM', 'name': 'SUPER劇場 (免費)', 'id0': '430555', 'source': 'epg.pw'},
        {'id': 'tvb_SDOC', 'name': 'SUPER話當年 (免費)', 'id0': '431446', 'source': 'epg.pw'},
        {'id': 'tvb_SSPT', 'name': 'SUPER Sports (免費)', 'id0': '430853', 'source': 'epg.pw'},
        {'id': 'tvb_C18', 'name': 'myTV SUPER 18台', 'id0': '368334', 'source': 'epg.pw'},
        {'id': 'tvb_C28', 'name': '28AI智慧賽馬 (免費)', 'id0': '394087', 'source': 'epg.pw'},
        {'id': 'tvb_TVG', 'name': '黃金翡翠台 (免費)', 'id0': '368358', 'source': 'epg.pw'},
        {'id': 'tvb_J', 'name': '翡翠台 (免費)', 'id0': '368366', 'source': 'epg.pw'},
        {'id': 'tvb_B', 'name': 'TVB Plus (免費)', 'id0': '368361', 'source': 'epg.pw'},
        {'id': 'tvb_C', 'name': '無綫新聞台 (免費)', 'id0': '368359', 'source': 'epg.pw'},
        {'id': 'tvb_P', 'name': '明珠台 (免費)', 'id0': '368369', 'source': 'epg.pw'},
        {'id': 'tvb_CTVC', 'name': '千禧經典台', 'id0': '368325', 'source': 'epg.pw'},
        {'id': 'tvb_CTVS', 'name': '亞洲劇台', 'id0': '368335', 'source': 'epg.pw'},
        {'id': 'tvb_CDR3', 'name': '華語劇台', 'id0': '368344', 'source': 'epg.pw'},
        {'id': 'tvb_TVO', 'name': '黃金華劇台', 'id0': '368351', 'source': 'epg.pw'},
        {'id': 'tvb_CTVE', 'name': '娛樂新聞台 (免費)', 'id0': '368323', 'source': 'epg.pw'},
        {'id': 'tvb_CCOC', 'name': '戲曲台', 'id0': '368353', 'source': 'epg.pw'},
        {'id': 'tvb_KID', 'name': 'SUPER Kids Channel', 'id0': '368380', 'source': 'epg.pw'},
        {'id': 'tvb_ZOO', 'name': 'ZooMoo', 'id0': '368368', 'source': 'epg.pw'},
        {'id': 'tvb_CNIKO', 'name': 'Nickelodeon', 'id0': '368336', 'source': 'epg.pw'},
        {'id': 'tvb_CNIJR', 'name': 'Nick Jr', 'id0': '368367', 'source': 'epg.pw'},
        {'id': 'tvb_CCLM', 'name': '粵語片台', 'id0': '368381', 'source': 'epg.pw'},
        {'id': 'tvb_CMAM', 'name': '美亞電影台', 'id0': '368348', 'source': 'epg.pw'},
        {'id': 'tvb_CTHR', 'name': 'Thrill', 'id0': '368339', 'source': 'epg.pw'},
        {'id': 'tvb_CCCM', 'name': '天映經典頻道', 'id0': '368371', 'source': 'epg.pw'},
        {'id': 'tvb_CMC', 'name': '中國電影頻道', 'id0': '368330', 'source': 'epg.pw'},
        {'id': 'tvb_CRTX', 'name': 'ROCK Action', 'id0': '368362', 'source': 'epg.pw'},
        {'id': 'tvb_POPC', 'name': 'PopC', 'id0': '368322', 'source': 'epg.pw'},
        {'id': 'tvb_ACTM', 'name': 'Action Hollywood Movies (免費)', 'id0': '430248', 'source': 'epg.pw'},
        {'id': 'tvb_RCM', 'name': 'Rialto Classic Movies (RCM) (免費)', 'id0': '430255', 'source': 'epg.pw'},
        {'id': 'tvb_CKIX', 'name': 'KIX', 'id0': '368350', 'source': 'epg.pw'},
        {'id': 'tvb_TRSP', 'name': 'TRACE Sport Stars (免費)', 'id0': '430249', 'source': 'epg.pw'},
        {'id': 'tvb_LNH', 'name': 'Love Nature HD', 'id0': '368355', 'source': 'epg.pw'},
        {'id': 'tvb_LN4', 'name': 'Love Nature 4K', 'id0': '368364', 'source': 'epg.pw'},
        {'id': 'tvb_SMS', 'name': 'Global Trekker', 'id0': '368356', 'source': 'epg.pw'},
        {'id': 'tvb_PETC', 'name': 'Pet Club TV (免費)', 'id0': '430256', 'source': 'epg.pw'},
        {'id': 'tvb_GLBT', 'name': 'Globetrotter (免費)', 'id0': '430254', 'source': 'epg.pw'},
        {'id': 'tvb_DOCV', 'name': 'Docsville (免費)', 'id0': '430257', 'source': 'epg.pw'},
        {'id': 'tvb_PULS', 'name': 'Pulse Documentaries (免費)', 'id0': '430250', 'source': 'epg.pw'},
        {'id': 'tvb_CRTE', 'name': 'ROCK綜藝娛樂', 'id0': '368332', 'source': 'epg.pw'},
        {'id': 'tvb_CAXN', 'name': 'AXN', 'id0': '368365', 'source': 'epg.pw'},
        {'id': 'tvb_RKEX', 'name': 'ROCK Extreme', 'id0': '443416', 'source': 'epg.pw'},
        {'id': 'tvb_CANI', 'name': 'Animax', 'id0': '368333', 'source': 'epg.pw'},
        {'id': 'tvb_CJTV', 'name': 'tvN', 'id0': '368326', 'source': 'epg.pw'},
        {'id': 'tvb_CTS1', 'name': '無線衛星亞洲台', 'id0': '368357', 'source': 'epg.pw'},
        {'id': 'tvb_CRE', 'name': '創世電視 (免費)', 'id0': '368329', 'source': 'epg.pw'},
        {'id': 'tvb_FBX', 'name': 'FashionBox', 'id0': '368374', 'source': 'epg.pw'},
        {'id': 'tvb_CMEZ', 'name': 'Mezzo Live HD', 'id0': '368341', 'source': 'epg.pw'},
        {'id': 'tvb_CC1', 'name': '中央電視台綜合頻道 (港澳版) (免費)', 'id0': '368375', 'source': 'epg.pw'},
        {'id': 'tvb_CGD', 'name': 'CGTN (中國環球電視網)記錄頻道 (免費)', 'id0': '368347', 'source': 'epg.pw'},
        {'id': 'tvb_CGE', 'name': 'CGTN (中國環球電視網)英語頻道 (免費)', 'id0': '368346', 'source': 'epg.pw'},
        {'id': 'tvb_DTV', 'name': '東方衛視國際頻道 (免費)', 'id0': '368340', 'source': 'epg.pw'},
        {'id': 'tvb_PCC', 'name': '鳳凰衛視中文台 (免費)', 'id0': '368338', 'source': 'epg.pw'},
        {'id': 'tvb_PIN', 'name': '鳳凰衛視資訊台 (免費)', 'id0': '368343', 'source': 'epg.pw'},
        {'id': 'tvb_PHK', 'name': '鳳凰衛視香港台 (免費)', 'id0': '368372', 'source': 'epg.pw'},
        {'id': 'tvb_CC4', 'name': '中國中央電視台中文國際頻道 (免費)', 'id0': '425931', 'source': 'epg.pw'},
        {'id': 'tvb_CCE', 'name': '中國中央電視台娛樂頻道 (免費)', 'id0': '425925', 'source': 'epg.pw'},
        {'id': 'tvb_CCO', 'name': '中國中央電視台戲曲頻道 (免費)', 'id0': '425924', 'source': 'epg.pw'},
        {'id': 'tvb_YNTV', 'name': '雲南瀾湄國際衛視 (免費)', 'id0': '425933', 'source': 'epg.pw'},
        {'id': 'tvb_AHTV', 'name': '安徽廣播電視台國際頻道 (免費)', 'id0': '425930', 'source': 'epg.pw'},
        {'id': 'tvb_BJTV', 'name': '北京電視台國際頻道 (免費)', 'id0': '425922', 'source': 'epg.pw'},
        {'id': 'tvb_GXTV', 'name': '廣西電視台國際頻道 (免費)', 'id0': '425929', 'source': 'epg.pw'},
        {'id': 'tvb_FJTV', 'name': '福建海峽衛視國際頻道 (免費)', 'id0': '425921', 'source': 'epg.pw'},
        {'id': 'tvb_HNTV', 'name': '湖南電視台國際頻道 (免費)', 'id0': '425923', 'source': 'epg.pw'},
        {'id': 'tvb_JSTV', 'name': '江蘇電視台國際頻道 (免費)', 'id0': '425928', 'source': 'epg.pw'},
        {'id': 'tvb_GBTV', 'name': '廣東廣播電視台大灣區衛視頻道 (免費)', 'id0': '425926', 'source': 'epg.pw'},
        {'id': 'tvb_ZJTV', 'name': '浙江電視台國際頻道 (免費)', 'id0': '425932', 'source': 'epg.pw'},
        {'id': 'tvb_SZTV', 'name': '深圳衛視國際頻道 (免費)', 'id0': '425927', 'source': 'epg.pw'},
        {'id': 'tvb_NOW7', 'name': 'NOW 70s (免費)', 'id0': '430253', 'source': 'epg.pw'},
        {'id': 'tvb_NOW8', 'name': 'NOW 80s (免費)', 'id0': '430251', 'source': 'epg.pw'},
        {'id': 'tvb_NOWR', 'name': 'NOW ROCK (免費)', 'id0': '430258', 'source': 'epg.pw'},
        {'id': 'tvb_NOW9', 'name': 'NOW 90s00s (免費)', 'id0': '430252', 'source': 'epg.pw'},
        {'id': 'tvb_CONC', 'name': 'Concerto (免費)', 'id0': '430246', 'source': 'epg.pw'},
        {'id': 'tvb_TRUR', 'name': 'TRACE Urban (免費)', 'id0': '430245', 'source': 'epg.pw'},
        {'id': 'tvb_CTSN', 'name': '無線衛星新聞台', 'id0': '368363', 'source': 'epg.pw'},
        {'id': 'tvb_CCNA', 'name': '亞洲新聞台', 'id0': '368377', 'source': 'epg.pw'},
        {'id': 'tvb_CJAZ', 'name': '半島電視台英語頻道', 'id0': '368327', 'source': 'epg.pw'},
        {'id': 'tvb_CF24', 'name': 'France 24', 'id0': '368342', 'source': 'epg.pw'},
        {'id': 'tvb_CDW1', 'name': 'DW', 'id0': '368373', 'source': 'epg.pw'},
        {'id': 'tvb_CNHK', 'name': 'NHK World-Japan', 'id0': '368337', 'source': 'epg.pw'},
        {'id': 'tvb_CARI', 'name': 'Arirang TV', 'id0': '368370', 'source': 'epg.pw'},
        {'id': 'tvb_NSWD', 'name': 'NewsWorld (免費)', 'id0': '430247', 'source': 'epg.pw'},
        {'id': 'tvb_EVT2', 'name': 'myTV SUPER直播足球2台', 'id0': '397763', 'source': 'epg.pw'},
        {'id': 'tvb_EVT3', 'name': 'myTV SUPER直播足球3台', 'id0': '368345', 'source': 'epg.pw'},
        {'id': 'tvb_EVT4', 'name': 'myTV SUPER直播足球4台', 'id0': '368328', 'source': 'epg.pw'},
        {'id': 'tvb_EVT5', 'name': 'myTV SUPER直播足球5台', 'id0': '368379', 'source': 'epg.pw'},
        {'id': 'tvb_EVT6', 'name': 'myTV SUPER直播足球6台', 'id0': '398976', 'source': 'epg.pw'},
        {'id': 'tvb_EVT7', 'name': 'myTV SUPER直播足球7台', 'id0': '416310', 'source': 'epg.pw'},
        {'id': 'tvb_TEST', 'name': '測試頻道', 'id0': '368378', 'source': 'epg.pw'},
        {'id': 'tdm_1', 'name': '澳視澳門 Ch. 91', 'id0': '1', 'source': 'tdm'},
        {'id': 'tdm_2', 'name': '澳視葡文 Ch. 92', 'id0': '2', 'source': 'tdm'},
        {'id': 'tdm_3', 'name': '澳門電台 FM100.7', 'id0': '3', 'source': 'tdm'},
        {'id': 'tdm_4', 'name': 'Rádio Macau FM98', 'id0': '4', 'source': 'tdm'},
        {'id': 'tdm_5', 'name': '澳門資訊 Ch.94', 'id0': '5', 'source': 'tdm'},
        {'id': 'tdm_6', 'name': '澳門體育 Ch.93', 'id0': '6', 'source': 'tdm'},
        {'id': 'tdm_7', 'name': '澳門綜藝 Ch.95', 'id0': '7', 'source': 'tdm'},
        {'id': 'tdm_8', 'name': '澳門 - MACAU 衛星頻道 Ch.96', 'id0': '8', 'source': 'tdm'},
        {'id': 'mod_006', 'name': '006 民視', 'id0': '006', 'source': 'mod'},
        {'id': 'mod_008', 'name': '008 台視', 'id0': '008', 'source': 'mod'},
        {'id': 'mod_010', 'name': '010 中視', 'id0': '010', 'source': 'mod'},
        {'id': 'mod_012', 'name': '012 華視', 'id0': '012', 'source': 'mod'},
        {'id': 'mod_013', 'name': '013 公視', 'id0': '013', 'source': 'mod'},
        {'id': 'mod_014', 'name': '014 公視台語台', 'id0': '014', 'source': 'mod'},
        {'id': 'mod_016', 'name': '016 原住民族電視台', 'id0': '016', 'source': 'mod'},
        {'id': 'mod_017', 'name': '017 客家電視', 'id0': '017', 'source': 'mod'},
        {'id': 'mod_098', 'name': '098 公視兒少台', 'id0': '098', 'source': 'mod'},
        {'id': 'mod_123', 'name': '123 國會頻道1', 'id0': '123', 'source': 'mod'},
        {'id': 'mod_124', 'name': '124 國會頻道2', 'id0': '124', 'source': 'mod'},
        {'id': 'mod_200', 'name': '200 愛爾達體育1台', 'id0': '200', 'source': 'mod'},
        {'id': 'mod_201', 'name': '201 愛爾達體育2台', 'id0': '201', 'source': 'mod'},
        {'id': 'mod_202', 'name': '202 愛爾達體育3台', 'id0': '202', 'source': 'mod'},
        {'id': 'mod_203', 'name': '203 愛爾達體育4台', 'id0': '203', 'source': 'mod'},
        {'id': 'mod_204', 'name': '204 博斯高球一台', 'id0': '204', 'source': 'mod'},
        {'id': 'mod_205', 'name': '205 博斯高球二台', 'id0': '205', 'source': 'mod'},
        {'id': 'mod_206', 'name': '206 博斯網球台', 'id0': '206', 'source': 'mod'},
        {'id': 'mod_207', 'name': '207 博斯魅力網', 'id0': '207', 'source': 'mod'},
        {'id': 'mod_208', 'name': '208 博斯無限台', 'id0': '208', 'source': 'mod'},
        {'id': 'mod_209', 'name': '209 博斯無限二台', 'id0': '209', 'source': 'mod'},
        {'id': 'mod_210', 'name': '210 TRACE Sport Stars', 'id0': '210', 'source': 'mod'},
        {'id': 'mod_212', 'name': '212 博斯運動一台', 'id0': '212', 'source': 'mod'},
        {'id': 'mod_213', 'name': '213 博斯運動二台', 'id0': '213', 'source': 'mod'},
        {'id': 'mod_310', 'name': '310 中視菁采台', 'id0': '310', 'source': 'mod'},
        {'id': 'mod_316', 'name': '316 民視第一台', 'id0': '316', 'source': 'mod'},
        {'id': 'mod_317', 'name': '317 民視台灣台', 'id0': '317', 'source': 'mod'},
        {'id': 'mod_320', 'name': '320 新唐人亞太台', 'id0': '320', 'source': 'mod'},
        {'id': 'mod_500', 'name': '500 中視新聞台', 'id0': '500', 'source': 'mod'},
        {'id': 'mod_501', 'name': '501 寰宇新聞台', 'id0': '501', 'source': 'mod'},
        {'id': 'mod_502', 'name': '502 寰宇新聞台灣台', 'id0': '502', 'source': 'mod'},
        {'id': 'mod_503', 'name': '503 台視新聞台', 'id0': '503', 'source': 'mod'},
        {'id': 'mod_504', 'name': '504 三立財經新聞台', 'id0': '504', 'source': 'mod'},
        {'id': 'mod_505', 'name': '505 華視新聞資訊台', 'id0': '505', 'source': 'mod'},
        {'id': 'mod_506', 'name': '506 壹電視新聞台', 'id0': '506', 'source': 'mod'},
        {'id': 'mod_507', 'name': '507 民視新聞台', 'id0': '507', 'source': 'mod'},
        {'id': 'mod_508', 'name': '508 鏡電視新聞台', 'id0': '508', 'source': 'mod'},
        {'id': 'mod_520', 'name': '520 寰宇財經台', 'id0': '520', 'source': 'mod'},
        {'id': 'mod_521', 'name': '521 台視財經台', 'id0': '521', 'source': 'mod'},
        {'id': 'mod_551', 'name': '551 BBC NEWS', 'id0': '551', 'source': 'mod'},
        {'id': 'mod_558', 'name': '558 TaiwanPlus', 'id0': '558', 'source': 'mod'},
        {'id': 'mod_600', 'name': '600 視納華仁紀實台', 'id0': '600', 'source': 'mod'},
        {'id': 'mod_601', 'name': '601 影迷數位紀實台', 'id0': '601', 'source': 'mod'},
        {'id': 'mod_610', 'name': '610 美亞電影台', 'id0': '610', 'source': 'mod'},
        {'id': 'mod_619', 'name': '619 amc電影台', 'id0': '619', 'source': 'mod'},
        {'id': 'mod_626', 'name': '626 CatchPlay電影台', 'id0': '626', 'source': 'mod'},
        {'id': 'mod_627', 'name': '627 CinemaWorld', 'id0': '627', 'source': 'mod'},
        {'id': 'mod_628', 'name': '628 壹電視電影台', 'id0': '628', 'source': 'mod'},
        {'id': 'mod_629', 'name': '629 采昌影劇台', 'id0': '629', 'source': 'mod'},
        {'id': 'mod_630', 'name': '630 影迷數位電影台', 'id0': '630', 'source': 'mod'},
        {'id': 'mod_633', 'name': '633 My Cinema Europe HD 我的歐洲電影', 'id0': '633', 'source': 'mod'},
        {'id': 'tbc_025', 'name': '東森幼幼台', 'id0': '368941', 'source': 'epg.pw'},
        {'id': 'tbc_029', 'name': '三立台灣台', 'id0': '368952', 'source': 'epg.pw'},
        {'id': 'tbc_030', 'name': '三立都會台', 'id0': '369190', 'source': 'epg.pw'},
        {'id': 'tbc_032', 'name': '東森綜合台', 'id0': '369188', 'source': 'epg.pw'},
        {'id': 'tbc_033', 'name': '東森超視', 'id0': '369189', 'source': 'epg.pw'},
        {'id': 'tbc_036', 'name': '中天綜合台', 'id0': '369192', 'source': 'epg.pw'},
        {'id': 'tbc_038', 'name': '年代MUCH TV', 'id0': '369182', 'source': 'epg.pw'},
        {'id': 'tbc_039', 'name': '中天娛樂台', 'id0': '369183', 'source': 'epg.pw'},
        {'id': 'tbc_040', 'name': '東森戲劇台', 'id0': '369227', 'source': 'epg.pw'},
        {'id': 'tbc_042', 'name': 'TVBS歡樂台', 'id0': '369225', 'source': 'epg.pw'},
        {'id': 'tbc_050', 'name': '年代新聞台', 'id0': '369247', 'source': 'epg.pw'},
        {'id': 'tbc_051', 'name': '東森新聞台', 'id0': '369248', 'source': 'epg.pw'},
        {'id': 'tbc_054', 'name': '三立新聞台', 'id0': '369243', 'source': 'epg.pw'},
        {'id': 'tbc_055', 'name': 'TVBS 新聞台', 'id0': '369244', 'source': 'epg.pw'},
        {'id': 'tbc_056', 'name': 'TVBS', 'id0': '369245', 'source': 'epg.pw'},
        {'id': 'tbc_057', 'name': '東森財經新聞台', 'id0': '369246', 'source': 'epg.pw'},
        {'id': 'tbc_058', 'name': '非凡新聞台', 'id0': '369240', 'source': 'epg.pw'},
        {'id': 'tbc_062', 'name': '東森電影台', 'id0': '369263', 'source': 'epg.pw'},
        {'id': 'tbc_063', 'name': '緯來電影台', 'id0': '369262', 'source': 'epg.pw'},
        {'id': 'tbc_064', 'name': 'LS Time電影台', 'id0': '369265', 'source': 'epg.pw'},
        {'id': 'tbc_065', 'name': 'HBO', 'id0': '369264', 'source': 'epg.pw'},
        {'id': 'tbc_066', 'name': '東森洋片台', 'id0': '369267', 'source': 'epg.pw'},
        {'id': 'tbc_067', 'name': 'AXN', 'id0': '369266', 'source': 'epg.pw'},
        {'id': 'tbc_068', 'name': '好萊塢電影台', 'id0': '369269', 'source': 'epg.pw'},
        {'id': 'tbc_072', 'name': '緯來體育台', 'id0': '369287', 'source': 'epg.pw'},
        {'id': 'tbc_089', 'name': '非凡商業台', 'id0': '369309', 'source': 'epg.pw'},
        {'id': 'tbc_127', 'name': 'Channel NewsAsia', 'id0': '408109', 'source': 'epg.pw'},
        {'id': 'tbc_207', 'name': 'HBO HD', 'id0': '369313', 'source': 'epg.pw'},
        {'id': 'tbc_208', 'name': 'HBO 強檔鉅獻', 'id0': '369199', 'source': 'epg.pw'},
        {'id': 'tbc_209', 'name': 'HBO 原創鉅獻', 'id0': '369197', 'source': 'epg.pw'},
        {'id': 'tbc_210', 'name': 'HBO 溫馨家庭', 'id0': '368911', 'source': 'epg.pw'},
        {'id': 'tbc_217', 'name': '韓國娛樂台KMTV', 'id0': '368912', 'source': 'epg.pw'},
        {'id': 'tbc_219', 'name': 'Lifetime', 'id0': '368951', 'source': 'epg.pw'},
        {'id': 'tbc_220', 'name': '罪案偵緝頻道', 'id0': '369278', 'source': 'epg.pw'},
        {'id': 'tbc_221', 'name': '寵物頻道', 'id0': '369277', 'source': 'epg.pw'},
        {'id': 'tbc_222', 'name': '歷史頻道', 'id0': '369276', 'source': 'epg.pw'},
        {'id': 'tbc_249', 'name': 'Euronews', 'id0': '369329', 'source': 'epg.pw'},
        {'id': 'hami_OTT_LIVE_0000001853', 'name': '愛爾達體育MAX1台', 'id0': 'OTT_LIVE_0000001853', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001854', 'name': '愛爾達體育MAX2台', 'id0': 'OTT_LIVE_0000001854', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001855', 'name': '愛爾達體育MAX3台', 'id0': 'OTT_LIVE_0000001855', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001856', 'name': '愛爾達體育MAX4台', 'id0': 'OTT_LIVE_0000001856', 'source': 'hami'},
        {'id': 'litv_4gtv-4gtv009', 'name': '中天新聞台', 'id0': 'ch52', 'source': 'litv'},
        {'id': 'litv_litv-longturn01', 'name': '龍華卡通台', 'id0': 'ch1040', 'source': 'litv'},
        {'id': 'litv_litv-longturn18', 'name': '龍華戲劇台', 'id0': 'ch1042', 'source': 'litv'},
        {'id': 'litv_litv-longturn12', 'name': '龍華偶像台', 'id0': 'ch1077', 'source': 'litv'},
        {'id': 'litv_litv-longturn11', 'name': '龍華日韓台', 'id0': 'ch1078', 'source': 'litv'},
        {'id': 'litv_litv-longturn03', 'name': '龍華電影台', 'id0': 'ch1166', 'source': 'litv'},
        {'id': 'litv_litv-longturn21', 'name': '龍華經典台', 'id0': 'ch1188', 'source': 'litv'},
        {'id': 'litv_litv-longturn02', 'name': '龍華洋片台', 'id0': 'ch1231', 'source': 'litv'},
        {'id': 'ETTVAmerica_China', 'name': '東森中國台', 'id0': '1-中國台', 'source': 'ETTVAmerica'},
        {'id': 'ETTVAmerica_East', 'name': '東森美東衛視台', 'id0': '20-美東衛視台', 'source': 'ETTVAmerica'},
        {'id': 'ntd_china', 'name': '新唐人中國台', 'id0': 'ntd_china', 'source': 'ntdtv'},
        {'id': 'chinasuntv', 'name': '陽光衛視', 'id0': 'chinasuntv', 'source': 'suntv'},
        {'id': 'astro_101', 'name': 'TV1 HD', 'id0': '3683', 'source': 'epg.pw'},
        {'id': 'astro_102', 'name': 'TV2 HD', 'id0': '3711', 'source': 'epg.pw'},
        {'id': 'astro_103', 'name': 'TV3', 'id0': '1072', 'source': 'epg.pw'},
        {'id': 'astro_104', 'name': 'Astro Ria HD', 'id0': '2384', 'source': 'epg.pw'},
        {'id': 'astro_105', 'name': 'Astro Prima HD', 'id0': '3158', 'source': 'epg.pw'},
        {'id': 'astro_106', 'name': 'Astro Oasis HD', 'id0': '3145', 'source': 'epg.pw'},
        {'id': 'astro_108', 'name': 'Astro Citra HD', 'id0': '2937', 'source': 'epg.pw'},
        {'id': 'astro_112', 'name': 'Astro Rania HD', 'id0': '3784', 'source': 'epg.pw'},
        {'id': 'astro_114', 'name': 'Al-Hijrah', 'id0': '1584', 'source': 'epg.pw'},
        {'id': 'astro_116', 'name': 'Colors Hindi HD', 'id0': '3325', 'source': 'epg.pw'},
        {'id': 'astro_122', 'name': 'TVS', 'id0': '3942', 'source': 'epg.pw'},
        {'id': 'astro_146', 'name': 'TV Okey HD', 'id0': '4160', 'source': 'epg.pw'},
        {'id': 'astro_148', 'name': '8TV', 'id0': '1122', 'source': 'epg.pw'},
        {'id': 'astro_149', 'name': 'TV9', 'id0': '902', 'source': 'epg.pw'},
        {'id': 'astro_201', 'name': 'Astro Vaanavil HD', 'id0': '3735', 'source': 'epg.pw'},
        {'id': 'astro_202', 'name': 'Astro Vinmeen HD', 'id0': '2058', 'source': 'epg.pw'},
        {'id': 'astro_203', 'name': 'Astro Vellithirai HD', 'id0': '3760', 'source': 'epg.pw'},
        {'id': 'astro_211', 'name': 'SUN TV HD', 'id0': '3313', 'source': 'epg.pw'},
        {'id': 'astro_212', 'name': 'Sun Music HD', 'id0': '3835', 'source': 'epg.pw'},
        {'id': 'astro_214', 'name': 'Adithya', 'id0': '946', 'source': 'epg.pw'},
        {'id': 'astro_215', 'name': 'Sun News', 'id0': '4185', 'source': 'epg.pw'},
        {'id': 'astro_216', 'name': 'KTV', 'id0': '4183', 'source': 'epg.pw'},
        {'id': 'astro_217', 'name': 'Sun Life', 'id0': '4181', 'source': 'epg.pw'},
        {'id': 'astro_221', 'name': 'Star Vijay HD', 'id0': '3308', 'source': 'epg.pw'},
        {'id': 'astro_222', 'name': 'Colors Tamil HD', 'id0': '2917', 'source': 'epg.pw'},
        {'id': 'astro_223', 'name': 'Zee Tamil HD', 'id0': '2885', 'source': 'epg.pw'},
        {'id': 'astro_241', 'name': 'ABO Movies Thangathirai HD', 'id0': '2181', 'source': 'epg.pw'},
        {'id': 'astro_251', 'name': 'Zee Cinema', 'id0': '4221', 'source': 'epg.pw'},
        {'id': 'astro_300', 'name': 'iQIYI HD', 'id0': '3290', 'source': 'epg.pw'},
        {'id': 'astro_305', 'name': 'TVB Classic HD', 'id0': '3895', 'source': 'epg.pw'},
        {'id': 'astro_306', 'name': 'Astro AEC', 'id0': '2226', 'source': 'epg.pw'},
        {'id': 'astro_308', 'name': 'Astro QJ', 'id0': '1781', 'source': 'epg.pw'},
        {'id': 'astro_309', 'name': 'Celestial Movies HD', 'id0': '1298', 'source': 'epg.pw'},
        {'id': 'astro_310', 'name': 'TVB Jade', 'id0': '2524', 'source': 'epg.pw'},
        {'id': 'astro_311', 'name': 'Astro AOD', 'id0': '2124', 'source': 'epg.pw'},
        {'id': 'astro_316', 'name': 'CTI Asia HD', 'id0': '3885', 'source': 'epg.pw'},
        {'id': 'astro_317', 'name': 'TVB Entertainment News HD', 'id0': '3920', 'source': 'epg.pw'},
        {'id': 'astro_319', 'name': 'TVB Xing He HD', 'id0': '3493', 'source': 'epg.pw'},
        {'id': 'astro_320', 'name': 'TVBS Asia HD', 'id0': '3509', 'source': 'epg.pw'},
        {'id': 'astro_321', 'name': 'Celestial Classic Movies', 'id0': '2280', 'source': 'epg.pw'},
        {'id': 'astro_325', 'name': 'Phoenix Chinese Channel HD', 'id0': '3478', 'source': 'epg.pw'},
        {'id': 'astro_326', 'name': 'Phoenix Info News HD', 'id0': '878', 'source': 'epg.pw'},
        {'id': 'astro_333', 'name': 'Astro Hua Hee Dai', 'id0': '1951', 'source': 'epg.pw'},
        {'id': 'astro_335', 'name': 'CCTV4 HD', 'id0': '3518', 'source': 'epg.pw'},
        {'id': 'astro_392', 'name': 'KBS World HD', 'id0': '1889', 'source': 'epg.pw'},
        {'id': 'astro_393', 'name': 'ONE HD', 'id0': '1242', 'source': 'epg.pw'},
        {'id': 'astro_395', 'name': 'tvN HD', 'id0': '2323', 'source': 'epg.pw'},
        {'id': 'astro_396', 'name': 'K-Plus HD', 'id0': '2652', 'source': 'epg.pw'},
        {'id': 'astro_398', 'name': 'NHK World Premium', 'id0': '3929', 'source': 'epg.pw'},
        {'id': 'astro_401', 'name': 'HITS Movies HD', 'id0': '3575', 'source': 'epg.pw'},
        {'id': 'astro_404', 'name': 'BOO HD', 'id0': '2636', 'source': 'epg.pw'},
        {'id': 'astro_411', 'name': 'HBO HD', 'id0': '1425', 'source': 'epg.pw'},
        {'id': 'astro_412', 'name': 'CINEMAX HD', 'id0': '3200', 'source': 'epg.pw'},
        {'id': 'astro_413', 'name': 'SHOWCASE MOVIES', 'id0': '4057', 'source': 'epg.pw'},
        {'id': 'astro_414', 'name': 'HBO Family', 'id0': '4008', 'source': 'epg.pw'},
        {'id': 'astro_415', 'name': 'HBO Hits', 'id0': '3994', 'source': 'epg.pw'},
        {'id': 'astro_416', 'name': 'tvN Movies HD', 'id0': '2726', 'source': 'epg.pw'},
        {'id': 'astro_501', 'name': 'Astro Awani HD', 'id0': '3958', 'source': 'epg.pw'},
        {'id': 'astro_502', 'name': 'BERNAMA', 'id0': '1835', 'source': 'epg.pw'},
        {'id': 'astro_503', 'name': 'CGTN HD', 'id0': '3906', 'source': 'epg.pw'},
        {'id': 'astro_511', 'name': 'CNN HD', 'id0': '3179', 'source': 'epg.pw'},
        {'id': 'astro_512', 'name': 'BBC News HD', 'id0': '3329', 'source': 'epg.pw'},
        {'id': 'astro_513', 'name': 'Al Jazeera English HD', 'id0': '3416', 'source': 'epg.pw'},
        {'id': 'astro_514', 'name': 'Sky News HD', 'id0': '1744', 'source': 'epg.pw'},
        {'id': 'astro_515', 'name': 'CNA HD', 'id0': '2852', 'source': 'epg.pw'},
        {'id': 'astro_516', 'name': 'CNBC Asia HD', 'id0': '3873', 'source': 'epg.pw'},
        {'id': 'astro_517', 'name': 'Bloomberg TV HD', 'id0': '3858', 'source': 'epg.pw'},
        {'id': 'astro_518', 'name': 'ABC Australia HD', 'id0': '4130', 'source': 'epg.pw'},
        {'id': 'astro_521', 'name': 'DW English', 'id0': '2756', 'source': 'epg.pw'},
        {'id': 'astro_522', 'name': 'France24', 'id0': '2781', 'source': 'epg.pw'},
        {'id': 'astro_549', 'name': 'Love Nature 4K', 'id0': '4171', 'source': 'epg.pw'},
        {'id': 'astro_550', 'name': 'Love Nature', 'id0': '4196', 'source': 'epg.pw'},
        {'id': 'astro_551', 'name': 'Global Trekker', 'id0': '4189', 'source': 'epg.pw'},
        {'id': 'astro_552', 'name': 'Discovery Channel HD', 'id0': '3437', 'source': 'epg.pw'},
        {'id': 'astro_553', 'name': 'Discovery Asia HD', 'id0': '1358', 'source': 'epg.pw'},
        {'id': 'astro_554', 'name': 'BBC Earth', 'id0': '4030', 'source': 'epg.pw'},
        {'id': 'astro_555', 'name': 'History HD', 'id0': '1477', 'source': 'epg.pw'},
        {'id': 'astro_603', 'name': 'Astro Tutor TV SMK HD', 'id0': '3809', 'source': 'epg.pw'},
        {'id': 'astro_611', 'name': 'Astro Ceria HD', 'id0': '3533', 'source': 'epg.pw'},
        {'id': 'astro_615', 'name': 'Cartoon Network HD', 'id0': '3403', 'source': 'epg.pw'},
        {'id': 'astro_616', 'name': 'Nickelodeon HD', 'id0': '3385', 'source': 'epg.pw'},
        {'id': 'astro_617', 'name': 'Nick Jr.', 'id0': '3600', 'source': 'epg.pw'},
        {'id': 'astro_618', 'name': 'Moonbug', 'id0': '4136', 'source': 'epg.pw'},
        {'id': 'astro_619', 'name': 'Blippi & Friends', 'id0': '400446', 'source': 'epg.pw'},
        {'id': 'astro_620', 'name': 'CBeebies', 'id0': '4187', 'source': 'epg.pw'},
        {'id': 'astro_701', 'name': 'AXN HD', 'id0': '1205', 'source': 'epg.pw'},
        {'id': 'astro_702', 'name': 'HITS NOW', 'id0': '186250', 'source': 'epg.pw'},
        {'id': 'astro_703', 'name': 'Lifetime HD', 'id0': '3968', 'source': 'epg.pw'},
        {'id': 'astro_706', 'name': 'HITS HD', 'id0': '2208', 'source': 'epg.pw'},
        {'id': 'astro_707', 'name': 'TLC HD', 'id0': '3234', 'source': 'epg.pw'},
        {'id': 'astro_709', 'name': 'Asian Food Network HD', 'id0': '997', 'source': 'epg.pw'},
        {'id': 'astro_714', 'name': 'Crime & Investigation HD', 'id0': '3362', 'source': 'epg.pw'},
        {'id': 'astro_715', 'name': 'HGTV HD', 'id0': '2473', 'source': 'epg.pw'},
        {'id': 'astro_717', 'name': 'BBC Lifestyle HD', 'id0': '4019', 'source': 'epg.pw'},
        {'id': 'astro_718', 'name': 'MTV Live', 'id0': '3849', 'source': 'epg.pw'},
        {'id': 'astro_801', 'name': 'Astro Arena HD', 'id0': '2552', 'source': 'epg.pw'},
        {'id': 'astro_802', 'name': 'Astro Arena 2 HD', 'id0': '4100', 'source': 'epg.pw'},
        {'id': 'astro_803', 'name': 'Arena Bola', 'id0': '4209', 'source': 'epg.pw'},
        {'id': 'astro_804', 'name': 'Arena Bola 2', 'id0': '4215', 'source': 'epg.pw'},
        {'id': 'astro_805', 'name': 'Astro SuperSport UHD 1', 'id0': '3018', 'source': 'epg.pw'},
        {'id': 'astro_808', 'name': 'Astro Sports Plus', 'id0': '397402', 'source': 'epg.pw'},
        {'id': 'astro_810', 'name': 'Astro Grandstand', 'id0': '397403', 'source': 'epg.pw'},
        {'id': 'astro_811', 'name': 'Astro Premier League', 'id0': '397396', 'source': 'epg.pw'},
        {'id': 'astro_812', 'name': 'Astro Premier League 2', 'id0': '397397', 'source': 'epg.pw'},
        {'id': 'astro_814', 'name': 'Astro Football', 'id0': '397399', 'source': 'epg.pw'},
        {'id': 'astro_815', 'name': 'Astro Badminton', 'id0': '397400', 'source': 'epg.pw'},
        {'id': 'astro_817', 'name': 'Astro Sports Plus', 'id0': '397402', 'source': 'epg.pw'},
        {'id': 'astro_820', 'name': 'beIN Sports HD', 'id0': '2580', 'source': 'epg.pw'},
        {'id': 'astro_821', 'name': 'beIN Sports 2', 'id0': '4146', 'source': 'epg.pw'},
        {'id': 'astro_822', 'name': 'beIN Sports 3', 'id0': '3118', 'source': 'epg.pw'},
        {'id': 'astro_823', 'name': 'SPOTV', 'id0': '4085', 'source': 'epg.pw'},
        {'id': 'astro_824', 'name': 'SPOTV2', 'id0': '4179', 'source': 'epg.pw'},
        {'id': 'astro_826', 'name': 'W-Sport', 'id0': '48630', 'source': 'epg.pw'},
        {'id': 'astro_831', 'name': 'Golf Channel HD', 'id0': '2300', 'source': 'epg.pw'},
        {'id': 'astro_832', 'name': 'Astro Cricket HD', 'id0': '2442', 'source': 'epg.pw'},
        {'id': 'astro_833', 'name': 'Premier Sports', 'id0': '3625', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_101', 'name': 'Preview Channel', 'id0': '412148', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_111', 'name': 'Hub E City HD', 'id0': '412191', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_115', 'name': 'Citra Entertainment', 'id0': '412104', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_116', 'name': 'Karisma', 'id0': '412117', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_118', 'name': 'Astro Warna HD', 'id0': '412155', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_123', 'name': 'Astro Sensasi HD', 'id0': '412113', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_124', 'name': 'ONE (Malay)', 'id0': '412102', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_125', 'name': 'Zee TV HD', 'id0': '412110', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_127', 'name': 'Sony Entertainment Television', 'id0': '412170', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_128', 'name': 'COLORS', 'id0': '412150', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_130', 'name': 'Zee Cinema', 'id0': '412185', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_131', 'name': 'SONY MAX', 'id0': '412138', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_132', 'name': 'COLORS Tamil HD', 'id0': '412090', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_133', 'name': 'Sun TV HD', 'id0': '412128', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_134', 'name': 'Sun Music', 'id0': '412094', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_135', 'name': 'Vijay TV HD', 'id0': '412141', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_136', 'name': 'Vannathirai', 'id0': '412097', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_137', 'name': 'Zee Thirai', 'id0': '412192', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_138', 'name': 'Zee Tamil', 'id0': '412115', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_139', 'name': 'Asianet', 'id0': '412103', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_140', 'name': 'Asianet Movies', 'id0': '412126', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_141', 'name': 'Kalaignar TV', 'id0': '412116', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_143', 'name': 'ANC', 'id0': '412127', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_144', 'name': 'The Filipino Channel HD', 'id0': '412143', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_145', 'name': 'Cinema One Global', 'id0': '412186', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_152', 'name': 'TV5MONDE HD', 'id0': '412183', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_153', 'name': 'DW English HD', 'id0': '412178', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_158', 'name': 'ADITHYA TV', 'id0': '412123', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_159', 'name': 'KTV HD', 'id0': '412203', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_201', 'name': 'Hub Sports 1 HD', 'id0': '412169', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_202', 'name': 'Hub Sports 2 HD', 'id0': '412154', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_203', 'name': 'Hub Sports 3 HD', 'id0': '412105', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_204', 'name': 'Hub Sports 4 HD', 'id0': '412198', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_205', 'name': 'Hub Sports 5 HD', 'id0': '412160', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_206', 'name': 'Hub Sports 6', 'id0': '412182', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_207', 'name': 'Hub Sports 7', 'id0': '446706', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_209', 'name': 'SPOTV', 'id0': '412181', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_210', 'name': 'SPOTV2', 'id0': '412187', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_211', 'name': 'beIN Sports 2 HD', 'id0': '412129', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_213', 'name': 'beIN Sports HD', 'id0': '412167', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_214', 'name': 'beIN Sports 3', 'id0': '412175', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_217', 'name': 'Cricbuzz', 'id0': '430462', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_218', 'name': 'Cricbuzz 2', 'id0': '430760', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_221', 'name': 'Hub Premier 1', 'id0': '412140', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_222', 'name': 'Hub Premier 2 (HD)', 'id0': '412164', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_241', 'name': 'FIGHT SPORTS HD', 'id0': '412165', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_247', 'name': 'Premier Sports', 'id0': '412133', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_303', 'name': 'Cbeebies HD', 'id0': '412174', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_304', 'name': 'Nick Jr', 'id0': '412136', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_307', 'name': 'DreamWorks Channel HD', 'id0': '412095', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_314', 'name': 'Nickelodeon Asia HD', 'id0': '412119', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_316', 'name': 'Cartoon Network', 'id0': '412124', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_317', 'name': 'Cartoonito HD', 'id0': '412137', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_401', 'name': 'HISTORY HD', 'id0': '412172', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_403', 'name': 'Crime + Investigation HD', 'id0': '412125', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_407', 'name': 'BBC Earth HD', 'id0': '412146', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_422', 'name': 'Discovery HD', 'id0': '412161', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_427', 'name': 'Travelxp HD', 'id0': '412120', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_432', 'name': 'BBC Lifestyle', 'id0': '412089', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_437', 'name': 'HGTV', 'id0': '412153', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_443', 'name': 'FashionTV HD', 'id0': '412197', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_447', 'name': 'ABC Australia HD', 'id0': '412157', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_509', 'name': 'Rock Entertainment', 'id0': '412091', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_511', 'name': 'AXN HD', 'id0': '412188', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_512', 'name': 'HITS MOVIES HD', 'id0': '412134', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_514', 'name': 'Lifetime HD', 'id0': '412184', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_519', 'name': 'Hits HD', 'id0': '412194', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_532', 'name': 'Animax HD', 'id0': '412144', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_601', 'name': 'HBO HD', 'id0': '412088', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_603', 'name': 'HBO Signature HD', 'id0': '412112', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_604', 'name': 'HBO Family HD', 'id0': '412195', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_605', 'name': 'HBO Hits HD', 'id0': '412093', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_611', 'name': 'Cinemax HD', 'id0': '412096', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_701', 'name': 'BBC World News HD', 'id0': '412098', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_702', 'name': 'Fox News Channel', 'id0': '412132', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_703', 'name': 'Sky News HD', 'id0': '429984', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_704', 'name': 'Euronews HD', 'id0': '412122', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_707', 'name': 'CNBC HD', 'id0': '412151', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_708', 'name': 'Bloomberg Television HD', 'id0': '412092', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_709', 'name': 'Bloomberg Originals', 'id0': '412199', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_711', 'name': 'CNN HD', 'id0': '412201', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_720', 'name': 'SEA Today', 'id0': '412196', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_722', 'name': 'CGTN', 'id0': '412109', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_724', 'name': 'France24', 'id0': '412190', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_801', 'name': 'CCTV-4', 'id0': '412139', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_805', 'name': 'Phoenix Chinese Channel HD', 'id0': '412189', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_806', 'name': 'Phoenix InfoNews Channel HD', 'id0': '412145', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_808', 'name': 'TVBS-NEWS', 'id0': '412149', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_811', 'name': 'NHK World Premium HD', 'id0': '412130', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_812', 'name': 'NHK WORLD - JAPAN HD', 'id0': '412179', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_815', 'name': 'KBS World HD', 'id0': '412101', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_817', 'name': 'Arirang TV HD', 'id0': '412147', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_820', 'name': 'ETTV ASIA HD', 'id0': '412168', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_823', 'name': 'ONE HD', 'id0': '412180', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_825', 'name': 'Hub E City HD', 'id0': '412200', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_827', 'name': 'CTI TV HD', 'id0': '412176', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_828', 'name': 'TVBS Asia', 'id0': '412193', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_832', 'name': 'Dragon TV', 'id0': '412142', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_838', 'name': 'TVB Jade HD', 'id0': '412135', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_855', 'name': 'Hub VVDrama', 'id0': '412156', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_859', 'name': 'TVB Xing He', 'id0': '412106', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_868', 'name': 'Celestial Movies HD', 'id0': '412099', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_869', 'name': 'CCM', 'id0': '412162', 'source': 'epg.pw'}
    ]
    asyncio.run(gen_xml(channels, 'epg0.xml'))
