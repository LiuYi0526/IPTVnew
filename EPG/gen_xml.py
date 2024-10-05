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
    xmlhead = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'
    xmlbottom = '</tv>'
    tz = ' +0800'
    tasks = [get_epgs(c) for c in channels]
    epgs0 = await asyncio.gather(*tasks)
    epgs = []
    README = ['|tvg-id|tvg-name|EPG状态|\n', '|:---:|:---:|:---:|\n']
    for i, text in epgs0:
        README.append(text)
        for k in i:
            epgs.append(k)
    f = open('README.md', 'w', encoding='utf-8')
    f.writelines(README)
    f.close()
    f = open(filename, 'w', encoding='utf-8')
    f.write(xmlhead)
    for channel in channels:
        c = ('    <channel id="%s">\n'
             '        <display-name lang="zh">%s</display-name>\n'
             '    </channel>\n') % (channel['id'], channel['name'])
        f.write(c)
    # noepg_channel = '<channel id="9999"><display-name lang="zh">noepg</display-name></channel>'
    # f.write(noepg_channel)
    for epg in epgs:
        # print(epg)
        start = epg['starttime'].astimezone(tz=beijing_tz).strftime('%Y%m%d%H%M%S') + tz
        end = epg['endtime'].astimezone(tz=beijing_tz).strftime('%Y%m%d%H%M%S') + tz
        id = epg['channel_id']
        title = html.escape(epg['title'])
        desc = html.escape(epg['desc'])
        programinfo = ('    <programme start="%s" stop="%s" channel="%s">\n'
                       '        <title lang="zh">%s</title>\n'
                       '        <desc lang="zh">%s</desc>\n'
                       '    </programme>\n') % (start, end, id, title, desc)
        f.write(programinfo)
    # for x in range(10):
    #     noepg_program_day = noepg('noepg','9999',(datetime.datetime.now().date() + datetime.timedelta(days=x-5)))
    #     f.write(noepg_program_day)
    f.write(xmlbottom)
    f.close()

if __name__ == '__main__':
    channels = [{'id': 'cctv_cctv1', 'name': 'CCTV-1 综合', 'id0': 'cctv1', 'source': 'cctv'},
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
                {'id': 'tvmao_NANCHANG-NANCHANG1', 'name': '南昌电视台新闻综合频道', 'id0': 'NANCHANG-NANCHANG1', 'source': 'tvmao'},
                {'id': 'tvmao_NANCHANG-NANCHANG4', 'name': '南昌电视台都市频道', 'id0': 'NANCHANG-NANCHANG4', 'source': 'tvmao'},
                {'id': 'tvmao_NANCHANG-NANCHANG3', 'name': '南昌电视台资讯频道', 'id0': 'NANCHANG-NANCHANG3', 'source': 'tvmao'},
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
                {'id': 'mod_010', 'name': '010 中視', 'id0': '010', 'source': 'mod'},
                {'id': 'mod_098', 'name': '098 公視兒少台', 'id0': '098', 'source': 'mod'},
                {'id': 'mod_320', 'name': '320 新唐人亞太台', 'id0': '320', 'source': 'mod'},
                {'id': 'mod_551', 'name': '551 BBC NEWS', 'id0': '368825', 'source': 'epg.pw'},
                {'id': 'mod_558', 'name': '558 TaiwanPlus', 'id0': '558', 'source': 'mod'},
                {'id': 'mod_610', 'name': '610 美亞電影台', 'id0': '368837', 'source': 'epg.pw'},
                {'id': 'mod_619', 'name': '619 amc電影台', 'id0': '368844', 'source': 'epg.pw'},
                {'id': 'mod_628', 'name': '628 壹電視電影台', 'id0': '368850', 'source': 'epg.pw'},
                {'id': 'mod_626', 'name': '626 CatchPlay電影台', 'id0': '368848', 'source': 'epg.pw'},
                {'id': 'nowtv_102', 'name': 'Viu 頻道', 'id0': '102', 'source': 'nowtv'},
                {'id': 'nowtv_105', 'name': 'Now華劇台', 'id0': '105', 'source': 'nowtv'},
                {'id': 'nowtv_108', 'name': 'NowJelli', 'id0': '108', 'source': 'nowtv'},
                {'id': 'nowtv_133', 'name': 'Now 爆谷台', 'id0': '133', 'source': 'nowtv'},
                {'id': 'nowtv_138', 'name': 'Now爆谷星影台', 'id0': '138', 'source': 'nowtv'},
                {'id': 'nowtv_162', 'name': '東森亞洲衛視', 'id0': '162', 'source': 'nowtv'},
                {'id': 'nowtv_218', 'name': 'Love Nature 4K', 'id0': '218', 'source': 'nowtv'},
                {'id': 'nowtv_316', 'name': 'CNN 國際新聞網絡', 'id0': '316', 'source': 'nowtv'},
                {'id': 'nowtv_329', 'name': 'RT', 'id0': '329', 'source': 'nowtv'},
                {'id': 'nowtv_331', 'name': 'Now直播台', 'id0': '331', 'source': 'nowtv'},
                {'id': 'nowtv_332', 'name': 'Now新聞台', 'id0': '332', 'source': 'nowtv'},
                {'id': 'nowtv_333', 'name': 'Now財經台', 'id0': '333', 'source': 'nowtv'},
                {'id': 'nowtv_371', 'name': '東森亞洲新聞台', 'id0': '371', 'source': 'nowtv'},
                {'id': 'nowtv_538', 'name': '中天亞洲台', 'id0': '538', 'source': 'nowtv'},
                {'id': 'nowtv_552', 'name': 'OneTV 綜合頻道', 'id0': '552', 'source': 'nowtv'},
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
                {'id': 'astro_148', 'name': '8TV', 'id0': '1122', 'source': 'epg.pw'},
                {'id': 'astro_300', 'name': 'iQIYI HD', 'id0': '3290', 'source': 'epg.pw'},
                {'id': 'astro_306', 'name': 'Astro AEC', 'id0': '2226', 'source': 'epg.pw'},
                {'id': 'astro_308', 'name': 'Astro QJ', 'id0': '1781', 'source': 'epg.pw'},
                {'id': 'astro_309', 'name': 'Celestial Movies HD', 'id0': '1298', 'source': 'epg.pw'},
                {'id': 'astro_311', 'name': 'Astro AOD', 'id0': '2124', 'source': 'epg.pw'},
                {'id': 'astro_319', 'name': 'TVB Xing He HD', 'id0': '3493', 'source': 'epg.pw'},
                {'id': 'astro_333', 'name': 'Astro Hua Hee Dai', 'id0': '1951', 'source': 'epg.pw'},
                {'id': 'astro_393', 'name': 'ONE HD', 'id0': '1242', 'source': 'epg.pw'},
                {'id': 'astro_392', 'name': 'KBS World HD', 'id0': '1889', 'source': 'epg.pw'},
                {'id': 'astro_514', 'name': 'Sky News HD', 'id0': '1744', 'source': 'epg.pw'},
                {'id': 'tbc_025', 'name': '東森幼幼台', 'id0': '368941', 'source': 'epg.pw'},
                {'id': 'tbc_029', 'name': '三立台灣台', 'id0': '368952', 'source': 'epg.pw'},
                {'id': 'tbc_030', 'name': '三立都會台', 'id0': '369190', 'source': 'epg.pw'},
                {'id': 'tbc_032', 'name': '東森綜合台', 'id0': '369188', 'source': 'epg.pw'},
                {'id': 'tbc_033', 'name': '東森超視', 'id0': '369189', 'source': 'epg.pw'},
                {'id': 'tbc_036', 'name': '中天綜合台', 'id0': '369192', 'source': 'epg.pw'},
                {'id': 'tbc_038', 'name': '年代MUCH TV', 'id0': '369182', 'source': 'epg.pw'},
                {'id': 'tbc_039', 'name': '中天娛樂台', 'id0': '369183', 'source': 'epg.pw'},
                {'id': 'tbc_040', 'name': '東森戲劇台', 'id0': '369227', 'source': 'epg.pw'},
                {'id': 'tbc_050', 'name': '年代新聞台', 'id0': '369247', 'source': 'epg.pw'},
                {'id': 'tbc_054', 'name': '三立新聞台', 'id0': '369243', 'source': 'epg.pw'},
                {'id': 'tbc_055', 'name': 'TVBS 新聞台', 'id0': '369244', 'source': 'epg.pw'},
                {'id': 'tbc_056', 'name': 'TVBS', 'id0': '369245', 'source': 'epg.pw'},
                {'id': 'tbc_063', 'name': '緯來電影台', 'id0': '369262', 'source': 'epg.pw'},
                {'id': 'tbc_065', 'name': 'HBO', 'id0': '369264', 'source': 'epg.pw'},
                {'id': 'tbc_127', 'name': 'Channel NewsAsia', 'id0': '368931', 'source': 'epg.pw'},
                {'id': 'tbc_207', 'name': 'HBO HD', 'id0': '369313', 'source': 'epg.pw'},
                {'id': 'tbc_208', 'name': 'HBO 強檔鉅獻', 'id0': '369199', 'source': 'epg.pw'},
                {'id': 'tbc_209', 'name': 'HBO 原創鉅獻', 'id0': '369197', 'source': 'epg.pw'},
                {'id': 'tbc_210', 'name': 'HBO 溫馨家庭', 'id0': '368911', 'source': 'epg.pw'},
                {'id': 'tbc_249', 'name': 'Euronews', 'id0': '369329', 'source': 'epg.pw'},
                {'id': 'tbc_405', 'name': '彩虹e台', 'id0': '368936', 'source': 'epg.pw'},
                {'id': 'tbc_406', 'name': '彩虹電影台', 'id0': '368935', 'source': 'epg.pw'},
                {'id': 'tbc_408', 'name': '松視1台', 'id0': '368939', 'source': 'epg.pw'},
                {'id': 'tbc_409', 'name': '松視2台', 'id0': '368938', 'source': 'epg.pw'},
                {'id': 'tbc_410', 'name': '松視3台', 'id0': '369161', 'source': 'epg.pw'},
                {'id': 'tbc_412', 'name': '潘朵啦高畫質玩美台', 'id0': '369203', 'source': 'epg.pw'},
                {'id': 'tbc_415', 'name': '驚豔成人電影台', 'id0': '369158', 'source': 'epg.pw'},
                {'id': 'tbc_416', 'name': '香蕉台', 'id0': '369159', 'source': 'epg.pw'},
                {'id': 'tvb_CWIN', 'name': 'SUPER FREE', 'id0': '368376', 'source': 'epg.pw'},
                {'id': 'tvb_C28', 'name': '28AI智慧賽馬', 'id0': '394087', 'source': 'epg.pw'},
                {'id': 'tvb_TVG', 'name': '黃金翡翠台', 'id0': '368358', 'source': 'epg.pw'},
                {'id': 'tvb_J', 'name': '翡翠台', 'id0': '368366', 'source': 'epg.pw'},
                {'id': 'tvb_B', 'name': 'TVB Plus', 'id0': '368361', 'source': 'epg.pw'},
                {'id': 'tvb_C', 'name': '無綫新聞台', 'id0': '368359', 'source': 'epg.pw'},
                {'id': 'tvb_P', 'name': '明珠台', 'id0': '368369', 'source': 'epg.pw'},
                {'id': 'tvb_CTVC', 'name': '千禧經典台', 'id0': '368325', 'source': 'epg.pw'},
                {'id': 'tvb_CTVS', 'name': '亞洲劇台', 'id0': '368335', 'source': 'epg.pw'},
                {'id': 'tvb_CDR3', 'name': '華語劇台', 'id0': '368344', 'source': 'epg.pw'},
                {'id': 'tvb_TVO', 'name': '黃金華劇台', 'id0': '368351', 'source': 'epg.pw'},
                {'id': 'tvb_CTVE', 'name': '娛樂新聞台', 'id0': '368323', 'source': 'epg.pw'},
                {'id': 'tvb_CCOC', 'name': '戲曲台', 'id0': '368353', 'source': 'epg.pw'},
                {'id': 'tvb_KID', 'name': 'SUPER Kids Channel', 'id0': '368380', 'source': 'epg.pw'},
                {'id': 'tvb_CNIKO', 'name': 'Nickelodeon', 'id0': '368336', 'source': 'epg.pw'},
                {'id': 'tvb_CCLM', 'name': '粵語片台', 'id0': '368381', 'source': 'epg.pw'},
                {'id': 'tvb_CMAM', 'name': '美亞電影台', 'id0': '368348', 'source': 'epg.pw'},
                {'id': 'tvb_POPC', 'name': 'PopC', 'id0': '368322', 'source': 'epg.pw'},
                {'id': 'tvb_LN4', 'name': 'Love Nature 4K', 'id0': '368364', 'source': 'epg.pw'},
                {'id': 'tvb_CTS1', 'name': '無線衛星亞洲台', 'id0': '368357', 'source': 'epg.pw'},
                {'id': 'tvb_CMN1', 'name': '神州新聞台', 'id0': '368352', 'source': 'epg.pw'},
                {'id': 'tvb_CNHK', 'name': 'NHK World-Japan', 'id0': '368337', 'source': 'epg.pw'},
                {'id': 'tvb_EVT2', 'name': 'myTV SUPER直播足球2台', 'id0': '397763', 'source': 'epg.pw'},
                {'id': 'tvb_EVT3', 'name': 'myTV SUPER直播足球3台', 'id0': '368345', 'source': 'epg.pw'},
                {'id': 'tvb_EVT4', 'name': 'myTV SUPER直播足球4台', 'id0': '368328', 'source': 'epg.pw'},
                {'id': 'tvb_EVT5', 'name': 'myTV SUPER直播足球5台', 'id0': '368379', 'source': 'epg.pw'},
                {'id': 'tvb_EVT6', 'name': 'myTV SUPER直播足球6台', 'id0': '398976', 'source': 'epg.pw'},
                {'id': 'ETTVAmerica_China', 'name': '東森中國台', 'id0': '1-中國台', 'source': 'ETTVAmerica'},
                {'id': 'ETTVAmerica_East', 'name': '東森美東衛視台', 'id0': '20-美東衛視台', 'source': 'ETTVAmerica'},
                {'id': 'ntd_china', 'name': '新唐人中國台', 'id0': 'ntd_china', 'source': 'ntdtv'},
                {'id': '4gtv_litv-ftv03', 'name': 'VOA美國之音', 'id0': 'litv-ftv03', 'source': '4gtv'},
                {'id': 'tdm_1', 'name': '澳視澳門 Ch. 91', 'id0': '1', 'source': 'tdm'},
                {'id': 'tdm_2', 'name': '澳視葡文 Ch. 92', 'id0': '2', 'source': 'tdm'},
                {'id': 'tdm_3', 'name': '澳門電台 FM100.7', 'id0': '3', 'source': 'tdm'},
                {'id': 'tdm_4', 'name': 'Rádio Macau FM98', 'id0': '4', 'source': 'tdm'},
                {'id': 'tdm_5', 'name': '澳門資訊 Ch.94', 'id0': '5', 'source': 'tdm'},
                {'id': 'tdm_6', 'name': '澳門體育 Ch.93', 'id0': '6', 'source': 'tdm'},
                {'id': 'tdm_7', 'name': '澳門綜藝 Ch.95', 'id0': '7', 'source': 'tdm'},
                {'id': 'tdm_8', 'name': '澳門 - MACAU 衛星頻道 Ch.96', 'id0': '8', 'source': 'tdm'}
                ]
    asyncio.run(gen_xml(channels, 'epg0.xml'))
