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
from radiocn import *
from RTHK import *
from gdtv import *
from hnntv import *
from hntv import *
from cztv import *
from gxntv import *
from iqilu import *
from kankanews import *
from jstv import *
from hebtv import *
from fjtv import *
from wisetv import *
from sztv import *
from gehua import *
from sc96655 import *
from bfgd import *
from sxtvs import *
from xmtv import *
from fengshows import *
from starhub import *
from btzx import *
from astro import *
from ysp_jce import get_epgs_ysp_jce
from nhk import get_epgs_nhk
from singtel import get_epgs_singtel

beijing_tz = pytz.timezone('Asia/Shanghai')

MAX_RETRIES = 5
MODE_PLAIN = 'plain'
MODE_DATE = 'date'
MODE_OFFSET = 'offset'
MODE_OFFSETS = 'offsets'

THREE_DAY_OFFSETS = (-1, 0, 1)

EPG_SOURCE_CONFIGS = {
    'cctv': (get_epgs_cctv, MODE_DATE, range(-6, 2)),
    'tvmao': (get_epgs_tvmao, MODE_DATE, range(-6, 2)),
    'radiocn': (get_epgs_radiocn, MODE_DATE, range(-6, 2)),
    'xjtvs': (get_epgs_xjtvs, MODE_DATE, THREE_DAY_OFFSETS),
    'nowtv': (get_epgs_nowtv, MODE_OFFSETS, THREE_DAY_OFFSETS),
    'mod': (get_epgs_mod, MODE_PLAIN, None),
    'hami': (get_epgs_hami, MODE_DATE, THREE_DAY_OFFSETS),
    'ETTVAmerica': (get_epgs_ettvamerica, MODE_DATE, THREE_DAY_OFFSETS),
    'tdm': (get_epgs_tdm, MODE_DATE, THREE_DAY_OFFSETS),
    'tbc': (get_epgs_tbc, MODE_PLAIN, None),
    'jxgdw': (get_epgs_jxgdw, MODE_DATE, (0,)),
    'epg.pw': (get_epgs_epgpw, MODE_PLAIN, None),
    'ntdtv': (get_epgs_ntdtv, MODE_PLAIN, None),
    'suntv': (get_epgs_suntv, MODE_PLAIN, None),
    '4gtv': (get_epgs_4gtv, MODE_PLAIN, None),
    'homeplus': (get_epgs_homeplus, MODE_PLAIN, None),
    'mytvsuper': (get_epgs_mytvsuper, MODE_DATE, (0,)),
    'cctvplus': (get_epgs_cctvplus, MODE_PLAIN, None),
    'hoy': (get_epgs_hoy, MODE_DATE, (0,)),
    'litv': (get_epgs_litv, MODE_PLAIN, None),
    '1905': (get_epgs_1905, MODE_DATE, (0,)),
    'RTHK': (get_epgs_RTHK, MODE_DATE, THREE_DAY_OFFSETS),
    'gdtv': (get_epgs_gdtv, MODE_DATE, THREE_DAY_OFFSETS),
    'hnntv': (get_epgs_hnntv, MODE_PLAIN, None),
    'hntv': (get_epgs_hntv, MODE_DATE, THREE_DAY_OFFSETS),
    'cztv': (get_epgs_cztv, MODE_DATE, THREE_DAY_OFFSETS),
    'gxntv': (get_epgs_gxntv, MODE_DATE, THREE_DAY_OFFSETS),
    'iqilu': (get_epgs_iqilu, MODE_DATE, (-2, -1, 0)),
    'kankanews': (get_epgs_kankanews, MODE_DATE, THREE_DAY_OFFSETS),
    'jstv': (get_epgs_jstv, MODE_PLAIN, None),
    'hebtv': (get_epgs_hebtv, MODE_DATE, (0,)),
    'fjtv': (get_epgs_fjtv, MODE_DATE, THREE_DAY_OFFSETS),
    'wisetv': (get_epgs_wisetv, MODE_DATE, THREE_DAY_OFFSETS),
    'sztv': (get_epgs_sztv, MODE_PLAIN, None),
    'gehua': (get_epgs_gehua, MODE_DATE, THREE_DAY_OFFSETS),
    'sc96655': (get_epgs_sc96655, MODE_DATE, THREE_DAY_OFFSETS),
    'bfgd': (get_epgs_bfgd, MODE_DATE, THREE_DAY_OFFSETS),
    'sxtvs': (get_epgs_sxtvs, MODE_PLAIN, None),
    'xmtv': (get_epgs_xmtv, MODE_OFFSET, THREE_DAY_OFFSETS),
    'fengshows': (get_epgs_fengshows, MODE_DATE, THREE_DAY_OFFSETS),
    'starhub': (get_epgs_starhub, MODE_DATE, THREE_DAY_OFFSETS),
    'btzx': (get_epgs_btzx, MODE_DATE, THREE_DAY_OFFSETS),
    'astro': (get_epgs_astro, MODE_DATE, (0, 1, 2)),
    'YSP_JCE': (get_epgs_ysp_jce, MODE_DATE, range(-6, 2)),
    'nhk': (get_epgs_nhk, MODE_DATE, THREE_DAY_OFFSETS),
    'singtel': (get_epgs_singtel, MODE_DATE, THREE_DAY_OFFSETS),
}


def _iter_fetch_targets(mode, offsets, today):
    if mode == MODE_PLAIN:
        yield None
    elif mode == MODE_DATE:
        for offset in offsets:
            yield today + datetime.timedelta(days=offset)
    elif mode == MODE_OFFSET:
        for offset in offsets:
            yield offset
    elif mode == MODE_OFFSETS:
        yield offsets
    else:
        raise ValueError(f'Unsupported EPG mode: {mode}')


async def _call_epg_handler(handler, c, mode, target):
    if mode == MODE_PLAIN:
        return await handler(c)
    return await handler(c, target)


async def _fetch_epgs_with_retries(c, handler, mode, target):
    fail_context = f'{c}' if mode == MODE_PLAIN else f'{c}, {target}'
    for retry in range(1, MAX_RETRIES + 1):
        ret = await _call_epg_handler(handler, c, mode, target)
        if ret.get('success'):
            return ret.get('epgs', []), True
        logging.warning(f"{ret.get('msg', '')}, 将进行第{retry}次重试！")

    logging.warning(f'{fail_context}获取失败！')
    return [], False


async def get_epgs(c):
    logging.info(c)
    config = EPG_SOURCE_CONFIGS.get(c['source'])
    if config is None:
        logging.warning(f"{c} 未配置 EPG 处理器，使用旧逻辑尝试获取。")
        return await _get_epgs_legacy(c)

    handler, mode, offsets = config
    today = datetime.datetime.now().date()
    epgs = []
    success = '✅'
    for target in _iter_fetch_targets(mode, offsets, today):
        channel_epgs, ok = await _fetch_epgs_with_retries(c, handler, mode, target)
        epgs.extend(channel_epgs)
        if not ok:
            success = '❌'

    return epgs, f"|{c['id']}|{c['name']}|{success}|\n"


async def _get_epgs_legacy(c):
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'radiocn':
        for get_days in range(-6, 2):  # 7+1天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_radiocn(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
                logging.warning(f"{c}, {need_date}获取失败！")
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
            logging.warning(f"{c}, {need_date}获取失败！")
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
            logging.warning(f"{c}, {need_date}获取失败！")
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
            logging.warning(f"{c}, {need_date}获取失败！")
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
            logging.warning(f"{c}, {need_date}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'RTHK':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_RTHK(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'gdtv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_gdtv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'hnntv':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_hnntv(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}, {need_date}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'hntv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_hntv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'cztv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_cztv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'gxntv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_gxntv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'iqilu':
        for get_days in [-2, -1, 0]:
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_iqilu(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'kankanews':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_kankanews(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'jstv':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_jstv(c)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}, {need_date}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'hebtv':
        need_date = datetime.datetime.now().date()
        while times < 5:
            ret = await get_epgs_hebtv(c, need_date)
            if ret['success'] == True:
                epg = ret['epgs']
                break
            else:
                msg = ret['msg']
                times += 1
                logging.warning(f"{msg}, 将进行第{times}次重试！")
        else:
            logging.warning(f"{c}, {need_date}获取失败！")
            epg = []
            success = '❌'
        for i in epg:
            epgs.append(i)
    elif c['source'] == 'fjtv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_fjtv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'wisetv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_wisetv(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'sztv':
        while times < 5:
            ret = await get_epgs_sztv(c)
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
    elif c['source'] == 'gehua':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_gehua(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'sc96655':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_sc96655(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'bfgd':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_bfgd(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'sxtvs':
        while times < 5:
            ret = await get_epgs_sxtvs(c)
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
    elif c['source'] == 'xmtv':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            while times < 5:
                ret = await get_epgs_xmtv(c, get_days)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {get_days}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'fengshows':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_fengshows(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {get_days}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'starhub':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_starhub(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'btzx':
        for get_days in [-1, 0, 1]:  # 昨今明3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_btzx(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)
    elif c['source'] == 'astro':
        for get_days in [0, 1, 2]:  # 今明后3天
            need_date = datetime.datetime.now().date() + datetime.timedelta(days=get_days)
            while times < 5:
                ret = await get_epgs_astro(c, need_date)
                if ret['success'] == True:
                    epg = ret['epgs']
                    break
                else:
                    msg = ret['msg']
                    times += 1
                    logging.warning(f"{msg}, 将进行第{times}次重试！")
            else:
                logging.warning(f"{c}, {need_date}获取失败！")
                epg = []
                success = '❌'
            for i in epg:
                epgs.append(i)

    return epgs, f"|{c['id']}|{c['name']}|{success}|\n"


async def limited_get_epgs(c, semaphore):
    async with semaphore:
        result = await get_epgs(c)
        return result


async def gen_xml(channels, filename, max_concurrency=3):
    tz = ' +0800'
    if max_concurrency > 1:
        semaphore = asyncio.Semaphore(max_concurrency)
        tasks = [limited_get_epgs(c, semaphore) for c in channels]
        epgs0 = await asyncio.gather(*tasks)
    else:
        epgs0 = [await get_epgs(c) for c in channels]
    epgs = []
    README = ['|tvg-id|tvg-name|EPG状态|\n', '|:---:|:---:|:---:|\n']
    for i, text in epgs0:
        README.append(text)
        epgs.extend(i)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.writelines(README)
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
        {'id': 'cctv_cctv4k', 'name': 'CCTV-4K', 'id0': 'cctv4k', 'source': 'cctv'},
        {'id': 'cctv_cctv8k', 'name': 'CCTV-8K', 'id0': 'cctv8k', 'source': 'cctv'},
        {'id': 'cctv_cctveurope', 'name': 'CCTV-4 (欧洲)', 'id0': 'cctveurope', 'source': 'cctv'},
        {'id': 'cctv_cctvamerica', 'name': 'CCTV-4 (美洲)', 'id0': 'cctvamerica', 'source': 'cctv'},
        {'id': 'cctv_cctvfyzq', 'name': 'CCTV风云足球', 'id0': 'cctvfyzq', 'source': 'cctv'},
        {'id': 'cctv_cctvgaowang', 'name': 'CCTV高尔夫网球', 'id0': 'cctvgaowang', 'source': 'cctv'},
        {'id': 'cctv_cctvlaogushi', 'name': 'CCTV老故事', 'id0': 'cctvlaogushi', 'source': 'cctv'},
        {'id': 'cctv_cctvqixiang', 'name': 'CCTV气象', 'id0': 'cctvqixiang', 'source': 'cctv'},
        {'id': 'cctv_cctvxiqu', 'name': 'CCTV戏曲', 'id0': 'cctvxiqu', 'source': 'cctv'},
        {'id': 'cctv_cctvyule', 'name': 'CCTV娱乐', 'id0': 'cctvyule', 'source': 'cctv'},
        {'id': 'cctv_diyijuchang', 'name': 'CCTV第一剧场', 'id0': 'diyijuchang', 'source': 'cctv'},
        {'id': 'cctv_dianshigouwu', 'name': 'CCTV中视购物', 'id0': 'dianshigouwu', 'source': 'cctv'},
        {'id': 'cctv_fyjc', 'name': 'CCTV风云剧场', 'id0': 'fyjc', 'source': 'cctv'},
        {'id': 'cctv_fyyy', 'name': 'CCTV风云音乐', 'id0': '600099660', 'source': 'YSP_JCE'},
        {'id': 'cctv_guofang', 'name': 'CCTV国防军事', 'id0': 'guofang', 'source': 'cctv'},
        {'id': 'cctv_hjjc', 'name': 'CCTV怀旧剧场', 'id0': 'hjjc', 'source': 'cctv'},
        {'id': 'cctv_jingpin', 'name': 'CCTV央视文化精品', 'id0': 'jingpin', 'source': 'cctv'},
        {'id': 'cctv_shijiedili', 'name': 'CCTV世界地理', 'id0': 'shijiedili', 'source': 'cctv'},
        {'id': 'cctv_shishang', 'name': 'CCTV女性时尚', 'id0': 'shishang', 'source': 'cctv'},
        {'id': 'cctv_taiqiu', 'name': 'CCTV央视台球', 'id0': 'taiqiu', 'source': 'cctv'},
        {'id': 'cctv_wsjk', 'name': '卫生健康', 'id0': 'wsjk', 'source': 'cctv'},
        {'id': 'cctv_zhinan', 'name': 'CCTV电视指南', 'id0': 'zhinan', 'source': 'cctv'},
        {'id': 'cctv_cetv1', 'name': 'CETV-1', 'id0': 'cetv1', 'source': 'cctv'},
        {'id': 'cctv_cetv2', 'name': 'CETV-2', 'id0': 'cetv2', 'source': 'cctv'},
        {'id': 'cctv_cetv3', 'name': 'CETV-3', 'id0': 'cetv3', 'source': 'cctv'},
        {'id': 'cctv_cetv4', 'name': 'CETV-4', 'id0': 'cetv4', 'source': 'cctv'},
        {'id': 'cctv_zaoqijiaoyu', 'name': '早期教育', 'id0': 'zaoqijiaoyu', 'source': 'cctv'},
        {'id': 'cctv_cctv9', 'name': 'CGTN', 'id0': '600014550', 'source': 'YSP_JCE'},
        {'id': 'cctv_cctvfrench', 'name': 'CGTN法语频道', 'id0': '600084704', 'source': 'YSP_JCE'},
        {'id': 'cctv_cctvrussian', 'name': 'CGTN俄语频道', 'id0': '600084758', 'source': 'YSP_JCE'},
        {'id': 'cctv_cctvarabic', 'name': 'CGTN阿拉伯语频道', 'id0': '600084782', 'source': 'YSP_JCE'},
        {'id': 'cctv_cctvxiyu', 'name': 'CGTN西班牙语频道', 'id0': '600084744', 'source': 'YSP_JCE'},
        {'id': 'cctv_cctvdoc', 'name': 'CGTN外语纪录频道', 'id0': '600084781', 'source': 'YSP_JCE'},
        {'id': 'cctvplus_channel1', 'name': 'CCTV+ Channel 1', 'id0': 'channel1', 'source': 'cctvplus'},
        {'id': 'cctvplus_channel2', 'name': 'CCTV+ Channel 2', 'id0': 'channel2', 'source': 'cctvplus'},
        {'id': 'cctvplus_channel3', 'name': 'CCTV+ Channel 3', 'id0': 'channel3', 'source': 'cctvplus'},
        {'id': 'cctvplus_channel4', 'name': 'CCTV+ Channel 4', 'id0': 'channel4', 'source': 'cctvplus'},
        {'id': 'tvmao_NANCHANG-NANCHANG1', 'name': '南昌电视台新闻综合频道', 'id0': 'NANCHANG-NANCHANG1', 'source': 'tvmao'},
        {'id': 'tvmao_NANCHANG-NANCHANG4', 'name': '南昌电视台都市频道', 'id0': 'NANCHANG-NANCHANG4', 'source': 'tvmao'},
        {'id': 'tvmao_NANCHANG-NANCHANG3', 'name': '南昌电视台资讯频道', 'id0': 'NANCHANG-NANCHANG3', 'source': 'tvmao'},
        {'id': '1905_xl', 'name': '会员专享放映厅', 'id0': 'xl', 'source': '1905'},
        {'id': '1905_1905tv', 'name': '环球经典', 'id0': '1905tv', 'source': '1905'},
        {'id': 'guhua_620', 'name': 'BRTV体育休闲高清', 'id0': '620', 'source': 'gehua'},
        {'id': 'guhua_621', 'name': '北京卫视高清', 'id0': '621', 'source': 'gehua'},
        {'id': 'guhua_622', 'name': 'BRTV文艺高清', 'id0': '622', 'source': 'gehua'},
        {'id': 'guhua_23', 'name': 'BRTV纪实科教', 'id0': '23', 'source': 'gehua'},
        {'id': 'guhua_624', 'name': 'BRTV影视高清', 'id0': '624', 'source': 'gehua'},
        {'id': 'guhua_25', 'name': 'BRTV财经', 'id0': '25', 'source': 'gehua'},
        {'id': 'guhua_27', 'name': 'BRTV生活', 'id0': '27', 'source': 'gehua'},
        {'id': 'guhua_629', 'name': 'BRTV新闻高清', 'id0': '629', 'source': 'gehua'},
        {'id': 'guhua_30', 'name': '卡酷少儿', 'id0': '30', 'source': 'gehua'},
        {'id': 'btzx', 'name': "兵团卫视", 'id0': 'TvCh1540979167111228', 'source': 'btzx'},
        {'id': 'fjtv_665248990102917120', 'name': '福建综合频道', 'id0': '665248990102917120', 'source': 'fjtv'},
        {'id': 'fjtv_665248966136664064', 'name': '东南卫视', 'id0': '665248966136664064', 'source': 'fjtv'},
        {'id': 'fjtv_665248914378952704', 'name': '福建新闻频道', 'id0': '665248914378952704', 'source': 'fjtv'},
        {'id': 'fjtv_665248752898248704', 'name': '福建文旅·体育频道', 'id0': '665248752898248704', 'source': 'fjtv'},
        {'id': 'fjtv_665248553475870720', 'name': '福建少儿频道', 'id0': '665248553475870720', 'source': 'fjtv'},
        {'id': 'fjtv_665248523855695872', 'name': '海峡卫视', 'id0': '665248523855695872', 'source': 'fjtv'},
        {'id': 'jxgdw_87', 'name': '江西卫视', 'id0': '87', 'source': 'jxgdw'},
        {'id': 'jxgdw_86', 'name': '都市频道', 'id0': '86', 'source': 'jxgdw'},
        {'id': 'jxgdw_153', 'name': '经济生活', 'id0': '153', 'source': 'jxgdw'},
        {'id': 'jxgdw_83', 'name': '公共农业', 'id0': '83', 'source': 'jxgdw'},
        {'id': 'jxgdw_82', 'name': '少儿频道', 'id0': '82', 'source': 'jxgdw'},
        {'id': 'jxgdw_81', 'name': '新闻频道', 'id0': '81', 'source': 'jxgdw'},
        {'id': 'jxgdw_112', 'name': '移动电视', 'id0': '112', 'source': 'jxgdw'},
        {'id': 'jxgdw_78', 'name': '陶瓷频道', 'id0': '78', 'source': 'jxgdw'},
        {'id': 'jxgdw_79', 'name': '风尚购物', 'id0': '79', 'source': 'jxgdw'},
        {'id': 'gdtv_34', 'name': '广东卫视4K', 'id0': '34', 'source': 'gdtv'},
        {'id': 'gdtv_1', 'name': '广东卫视', 'id0': '1', 'source': 'gdtv'},
        {'id': 'gdtv_2', 'name': '广东珠江', 'id0': '2', 'source': 'gdtv'},
        {'id': 'gdtv_6', 'name': '广东新闻', 'id0': '6', 'source': 'gdtv'},
        {'id': 'gdtv_4', 'name': '广东民生', 'id0': '4', 'source': 'gdtv'},
        {'id': 'gdtv_3', 'name': '广东体育', 'id0': '3', 'source': 'gdtv'},
        {'id': 'gdtv_14', 'name': '大湾区卫视', 'id0': '14', 'source': 'gdtv'},
        {'id': 'gdtv_17', 'name': '广东影视', 'id0': '17', 'source': 'gdtv'},
        {'id': 'gdtv_16', 'name': '广东4K超高清', 'id0': '16', 'source': 'gdtv'},
        {'id': 'gdtv_18', 'name': '广东少儿', 'id0': '18', 'source': 'gdtv'},
        {'id': 'gdtv_7', 'name': '嘉佳卡通', 'id0': '7', 'source': 'gdtv'},
        {'id': 'gdtv_32', 'name': '广东移动', 'id0': '32', 'source': 'gdtv'},
        {'id': 'gxntv_广西卫视', 'name': '广西卫视', 'id0': '广西卫视', 'source': 'gxntv'},
        {'id': 'gxntv_综艺旅游频道', 'name': '广西综艺旅游频道', 'id0': '综艺旅游频道', 'source': 'gxntv'},
        {'id': 'gxntv_都市频道', 'name': '广西都市频道', 'id0': '都市频道', 'source': 'gxntv'},
        {'id': 'gxntv_新闻频道', 'name': '广西新闻频道', 'id0': '新闻频道', 'source': 'gxntv'},
        {'id': 'gxntv_影视频道', 'name': '广西影视频道', 'id0': '影视频道', 'source': 'gxntv'},
        {'id': 'gxntv_国际频道', 'name': '广西国际频道', 'id0': '国际频道', 'source': 'gxntv'},
        {'id': 'gxntv_乐思购频道', 'name': '广西乐思购频道', 'id0': '乐思购频道', 'source': 'gxntv'},
        {'id': 'hnntv_13', 'name': '海南卫视', 'id0': '13', 'source': 'hnntv'},
        {'id': 'hnntv_5', 'name': '三沙卫视', 'id0': '5', 'source': 'hnntv'},
        {'id': 'hnntv_1', 'name': '海南自贸', 'id0': '1', 'source': 'hnntv'},
        {'id': 'hnntv_3', 'name': '海南新闻', 'id0': '3', 'source': 'hnntv'},
        {'id': 'hnntv_4', 'name': '海南社会与法', 'id0': '4', 'source': 'hnntv'},
        {'id': 'hnntv_6', 'name': '海南文旅', 'id0': '6', 'source': 'hnntv'},
        {'id': 'hnntv_7', 'name': '海南少儿', 'id0': '7', 'source': 'hnntv'},
        {'id': 'hebtv_462', 'name': "河北卫视", 'id0': '462', 'source': 'hebtv'},
        {'id': 'hebtv_114', 'name': "河北经济生活", 'id0': '114', 'source': 'hebtv'},
        {'id': 'hebtv_118', 'name': "农民频道", 'id0': '118', 'source': 'hebtv'},
        {'id': 'hebtv_62', 'name': "河北都市", 'id0': '62', 'source': 'hebtv'},
        {'id': 'hebtv_334', 'name': "河北影视剧", 'id0': '334', 'source': 'hebtv'},
        {'id': 'hebtv_70', 'name': "河北少儿科教", 'id0': '70', 'source': 'hebtv'},
        {'id': 'hebtv_338', 'name': "河北文旅·公共", 'id0': '338', 'source': 'hebtv'},
        {'id': 'hebtv_330', 'name': "三佳购物", 'id0': '330', 'source': 'hebtv'},
        {'id': 'hntv_145', 'name': '河南卫视', 'id0': '145', 'source': 'hntv'},
        {'id': 'hntv_149', 'name': '河南新闻频道', 'id0': '149', 'source': 'hntv'},
        {'id': 'hntv_141', 'name': '河南都市频道', 'id0': '141', 'source': 'hntv'},
        {'id': 'hntv_146', 'name': '河南民生频道', 'id0': '146', 'source': 'hntv'},
        {'id': 'hntv_147', 'name': '河南法治频道', 'id0': '147', 'source': 'hntv'},
        {'id': 'hntv_151', 'name': '河南公共频道', 'id0': '151', 'source': 'hntv'},
        {'id': 'hntv_152', 'name': '河南乡村频道', 'id0': '152', 'source': 'hntv'},
        {'id': 'hntv_148', 'name': '河南电视剧频道', 'id0': '148', 'source': 'hntv'},
        {'id': 'hntv_154', 'name': '梨园频道', 'id0': '154', 'source': 'hntv'},
        {'id': 'hntv_155', 'name': '文物宝库', 'id0': '155', 'source': 'hntv'},
        {'id': 'hntv_156', 'name': '武术世界', 'id0': '156', 'source': 'hntv'},
        {'id': 'hntv_157', 'name': '睛彩中原', 'id0': '157', 'source': 'hntv'},
        {'id': 'hntv_183', 'name': '象视界', 'id0': '183', 'source': 'hntv'},
        {'id': 'hntv_194', 'name': '国学频道', 'id0': '194', 'source': 'hntv'},
        {'id': 'hntv_150', 'name': '欢腾购物', 'id0': '150', 'source': 'hntv'},
        {'id': 'jstv_670', 'name': '江苏卫视', 'id0': '670', 'source': 'jstv'},
        {'id': 'jstv_676', 'name': '江苏卫视4K超高清', 'id0': '676', 'source': 'jstv'},
        {'id': 'jstv_669', 'name': '江苏城市', 'id0': '669', 'source': 'jstv'},
        {'id': 'jstv_663', 'name': '江苏综艺', 'id0': '663', 'source': 'jstv'},
        {'id': 'jstv_664', 'name': '江苏影视', 'id0': '664', 'source': 'jstv'},
        {'id': 'jstv_668', 'name': '江苏新闻', 'id0': '668', 'source': 'jstv'},
        {'id': 'jstv_666', 'name': '江苏教育', 'id0': '666', 'source': 'jstv'},
        {'id': 'jstv_665', 'name': '江苏体育休闲', 'id0': '665', 'source': 'jstv'},
        {'id': 'jstv_667', 'name': '优漫卡通', 'id0': '667', 'source': 'jstv'},
        {'id': 'jstv_671', 'name': '江苏国际', 'id0': '671', 'source': 'jstv'},
        {'id': 'iqilu_24', 'name': '山东卫视', 'id0': '24', 'source': 'iqilu'},
        {'id': 'iqilu_25', 'name': '齐鲁频道', 'id0': '25', 'source': 'iqilu'},
        {'id': 'bfgd_4200000058', 'name': '辽宁卫视高清', 'id0': 4200000058, 'source': 'bfgd'},
        {'id': 'bfgd_4200000070', 'name': '辽宁影视剧高清', 'id0': 4200000070, 'source': 'bfgd'},
        {'id': 'bfgd_4200000704', 'name': '辽宁北方高清', 'id0': 4200000704, 'source': 'bfgd'},
        {'id': 'bfgd_4200000073', 'name': '辽宁生活高清', 'id0': 4200000073, 'source': 'bfgd'},
        {'id': 'bfgd_4200000075', 'name': '辽宁教育青少高清', 'id0': 4200000075, 'source': 'bfgd'},
        {'id': 'bfgd_4200000076', 'name': '辽宁经济高清', 'id0': 4200000076, 'source': 'bfgd'},
        {'id': 'bfgd_4200000077', 'name': '辽宁公共高清', 'id0': 4200000077, 'source': 'bfgd'},
        {'id': 'bfgd_4200000610', 'name': '辽宁都市高清', 'id0': 4200000610, 'source': 'bfgd'},
        {'id': 'bfgd_4200000611', 'name': '辽宁体育休闲高清', 'id0': 4200000611, 'source': 'bfgd'},
        {'id': 'bfgd_4200000636', 'name': '重温经典', 'id0': 4200000636, 'source': 'bfgd'},
        {'id': 'iqilu_26', 'name': '山东体育休闲频道', 'id0': '26', 'source': 'iqilu'},
        {'id': 'iqilu_27', 'name': '山东文旅频道', 'id0': '27', 'source': 'iqilu'},
        {'id': 'iqilu_28', 'name': '山东综艺频道', 'id0': '28', 'source': 'iqilu'},
        {'id': 'iqilu_29', 'name': '山东生活频道', 'id0': '29', 'source': 'iqilu'},
        {'id': 'iqilu_30', 'name': '山东农科频道', 'id0': '30', 'source': 'iqilu'},
        {'id': 'iqilu_31', 'name': '山东新闻频道', 'id0': '31', 'source': 'iqilu'},
        {'id': 'iqilu_32', 'name': '山东少儿频道', 'id0': '32', 'source': 'iqilu'},
        {'id': 'sxtvs_star','name': '陕西卫视', 'id0': 'star', 'source': 'sxtvs'},
        {'id': 'sxtvs_1', 'name': '陕西新闻资讯', 'id0': '1', 'source': 'sxtvs'},
        {'id': 'sxtvs_2', 'name': '陕西都市青春', 'id0': '2', 'source': 'sxtvs'},
        {'id': 'sxtvs_3', 'name': '陕西银龄频道', 'id0': '3', 'source': 'sxtvs'},
        {'id': 'sxtvs_5', 'name': '陕西秦腔频道', 'id0': '5', 'source': 'sxtvs'},
        {'id': 'sxtvs_7', 'name': '陕西体育休闲', 'id0': '7', 'source': 'sxtvs'},
        {'id': 'sxtvs_nl', 'name': '陕西农林', 'id0': 'nl', 'source': 'sxtvs'},
        {'id': 'sxtvs_11', 'name': '陕西移动电视', 'id0': '11', 'source': 'sxtvs'},
        {'id': 'kankanews_1', 'name': '东方卫视', 'id0': '1', 'source': 'kankanews'},
        {'id': 'kankanews_2', 'name': '上海新闻综合', 'id0': '2', 'source': 'kankanews'},
        {'id': 'kankanews_5', 'name': '第一财经', 'id0': '5', 'source': 'kankanews'},
        {'id': 'kankanews_10', 'name': '五星体育', 'id0': '10', 'source': 'kankanews'},
        {'id': 'kankanews_4', 'name': '上海都市频道', 'id0': '4', 'source': 'kankanews'},
        {'id': 'kankanews_9', 'name': '哈哈炫动', 'id0': '9', 'source': 'kankanews'},
        {'id': 'sztv_24725', 'name': '深圳卫视4K超高清', 'id0': 24725, 'source': 'sztv'},
        {'id': 'sztv_7867', 'name': '深圳卫视', 'id0': 7867, 'source': 'sztv'},
        {'id': 'sztv_7868', 'name': '深圳都市频道', 'id0': 7868, 'source': 'sztv'},
        {'id': 'sztv_7880', 'name': '深圳电视剧频道', 'id0': 7880, 'source': 'sztv'},
        {'id': 'sztv_7881', 'name': '深圳少儿频道', 'id0': 7881, 'source': 'sztv'},
        {'id': 'sztv_7869', 'name': '深圳移动电视', 'id0': 7869, 'source': 'sztv'},
        {'id': 'sztv_7878', 'name': '深圳宜和购物频道', 'id0': 7878, 'source': 'sztv'},
        {'id': 'sztv_7944', 'name': '深圳国际频道', 'id0': 7944, 'source': 'sztv'},
        {'id': 'sc96655_3492', 'name': '四川峨眉电影', 'id0': 3492, 'source': 'sc96655'},
        {'id': 'sc96655_3494', 'name': '康巴卫视', 'id0': 3494, 'source': 'sc96655'},
        {'id': 'sc96655_3496', 'name': '四川卫视', 'id0': 3496, 'source': 'sc96655'},
        {'id': 'sc96655_3498', 'name': '四川文化旅游', 'id0': 3498, 'source': 'sc96655'},
        {'id': 'sc96655_3500', 'name': '四川经济', 'id0': 3500, 'source': 'sc96655'},
        {'id': 'sc96655_3501', 'name': '四川新闻资讯', 'id0': 3501, 'source': 'sc96655'},
        {'id': 'sc96655_3504', 'name': '四川影视文艺', 'id0': 3504, 'source': 'sc96655'},
        {'id': 'sc96655_3506', 'name': '四川妇女儿童', 'id0': 3506, 'source': 'sc96655'},
        {'id': 'sc96655_3508', 'name': '四川科教', 'id0': 3508, 'source': 'sc96655'},
        {'id': 'sc96655_3509', 'name': '四川乡村', 'id0': 3509, 'source': 'sc96655'},
        {'id': 'sc96655_3789', 'name': '四川星空购物（高清）', 'id0': 3789, 'source': 'sc96655'},
        {'id': 'wisetv_698', 'name': '天津卫视', 'id0': '30001110000000000000000000000698', 'source': 'wisetv'},
        {'id': 'wisetv_699', 'name': '天津新闻', 'id0': '30001110000000000000000000000699', 'source': 'wisetv'},
        {'id': 'wisetv_700', 'name': '天津文艺', 'id0': '30001110000000000000000000000700', 'source': 'wisetv'},
        {'id': 'wisetv_701', 'name': '天津影视', 'id0': '30001110000000000000000000000701', 'source': 'wisetv'},
        {'id': 'wisetv_702', 'name': '天津都市', 'id0': '30001110000000000000000000000702', 'source': 'wisetv'},
        {'id': 'wisetv_692', 'name': '天津体育', 'id0': '30001110000000000000000000000692', 'source': 'wisetv'},
        {'id': 'wisetv_693', 'name': '天津教育', 'id0': '30001110000000000000000000000693', 'source': 'wisetv'},
        {'id': 'wisetv_697', 'name': '三佳购物', 'id0': '30001110000000000000000000000697', 'source': 'wisetv'},
        {'id': 'xmtv_84', 'name': '厦门卫视', 'id0': '84', 'source': 'xmtv'},
        {'id': 'xmtv_16', 'name': '厦门一套', 'id0': '16', 'source': 'xmtv'},
        {'id': 'xmtv_17', 'name': '厦门二套', 'id0': '17', 'source': 'xmtv'},
        {'id': 'XJTV-1', 'name': 'XJTV-1', 'id0': '1', 'source': 'xjtvs'},
        {'id': 'XJTV-2', 'name': 'XJTV-2', 'id0': '3', 'source': 'xjtvs'},
        {'id': 'XJTV-3', 'name': 'XJTV-3', 'id0': '4', 'source': 'xjtvs'},
        {'id': 'XJTV-4', 'name': 'XJTV-4', 'id0': '16', 'source': 'xjtvs'},
        {'id': 'XJTV-5', 'name': 'XJTV-5', 'id0': '17', 'source': 'xjtvs'},
        {'id': 'XJTV-7', 'name': 'XJTV-7', 'id0': '21', 'source': 'xjtvs'},
        {'id': 'XJTV-8', 'name': 'XJTV-8', 'id0': '23', 'source': 'xjtvs'},
        {'id': 'cztv_101', 'name': '浙江卫视', 'id0': '101', 'source': 'cztv'},
        {'id': 'cztv_102', 'name': '钱江都市', 'id0': '102', 'source': 'cztv'},
        {'id': 'cztv_103', 'name': '浙江经济生活', 'id0': '103', 'source': 'cztv'},
        {'id': 'cztv_104', 'name': '浙江教科影视', 'id0': '104', 'source': 'cztv'},
        {'id': 'cztv_106', 'name': '浙江民生休闲', 'id0': '106', 'source': 'cztv'},
        {'id': 'cztv_107', 'name': '浙江新闻', 'id0': '107', 'source': 'cztv'},
        {'id': 'cztv_108', 'name': '浙江少儿', 'id0': '108', 'source': 'cztv'},
        {'id': 'cztv_110', 'name': '浙江国际', 'id0': '110', 'source': 'cztv'},
        {'id': 'cztv_111', 'name': '浙江好易购', 'id0': '111', 'source': 'cztv'},
        {'id': 'cztv_112', 'name': '之江纪录', 'id0': '112', 'source': 'cztv'},
        {'id': 'radiocn_639', 'name': '中国之声', 'id0': '639', 'source': 'radiocn'},
        {'id': 'radiocn_640', 'name': '经济之声', 'id0': '640', 'source': 'radiocn'},
        {'id': 'radiocn_692', 'name': '环球资讯广播', 'id0': '692', 'source': 'radiocn'},
        {'id': 'radiocn_641', 'name': '音乐之声', 'id0': '641', 'source': 'radiocn'},
        {'id': 'radiocn_653', 'name': '中国交通广播', 'id0': '653', 'source': 'radiocn'},
        {'id': 'radiocn_648', 'name': '文艺之声', 'id0': '648', 'source': 'radiocn'},
        {'id': 'radiocn_645', 'name': '大湾区之声', 'id0': '645', 'source': 'radiocn'},
        {'id': 'radiocn_642', 'name': '经典音乐广播', 'id0': '642', 'source': 'radiocn'},
        {'id': 'radiocn_643', 'name': '台海之声', 'id0': '643', 'source': 'radiocn'},
        {'id': 'radiocn_644', 'name': '神州之声', 'id0': '644', 'source': 'radiocn'},
        {'id': 'radiocn_646', 'name': '香港之声', 'id0': '646', 'source': 'radiocn'},
        {'id': 'radiocn_647', 'name': '民族之声', 'id0': '647', 'source': 'radiocn'},
        {'id': 'radiocn_649', 'name': '老年之声', 'id0': '649', 'source': 'radiocn'},
        {'id': 'radiocn_650', 'name': '藏语广播', 'id0': '650', 'source': 'radiocn'},
        {'id': 'radiocn_651', 'name': '维吾尔语广播', 'id0': '651', 'source': 'radiocn'},
        {'id': 'radiocn_652', 'name': '阅读之声', 'id0': '652', 'source': 'radiocn'},
        {'id': 'radiocn_654', 'name': '中国乡村之声', 'id0': '654', 'source': 'radiocn'},
        {'id': 'radiocn_655', 'name': '哈萨克语广播', 'id0': '655', 'source': 'radiocn'},
        {'id': 'radiocn_662', 'name': 'HITFM劲曲调频', 'id0': '662', 'source': 'radiocn'},
        {'id': 'radiocn_689', 'name': '轻松调频', 'id0': '689', 'source': 'radiocn'},
        {'id': 'radiocn_664', 'name': '南海之声', 'id0': '664', 'source': 'radiocn'},
        {'id': 'radiocn_734', 'name': '英语资讯广播 CGTN Radio', 'id0': '734', 'source': 'radiocn'},
        {'id': 'RTHK_tv31', 'name': '港台電視 31', 'id0': 'tv31', 'source': 'RTHK'},
        {'id': 'RTHK_tv32', 'name': '港台電視 32', 'id0': 'tv32', 'source': 'RTHK'},
        {'id': 'RTHK_tv33', 'name': '港台電視 33', 'id0': 'tv33', 'source': 'RTHK'},
        {'id': 'RTHK_tv34', 'name': '港台電視 34', 'id0': 'tv34', 'source': 'RTHK'},
        {'id': 'RTHK_tv35', 'name': '港台電視 35', 'id0': 'tv35', 'source': 'RTHK'},
        {'id': 'RTHK_tv36', 'name': '港台電視 36', 'id0': 'tv36', 'source': 'RTHK'},
        {'id': 'RTHK_pth', 'name': '香港電台普通話台', 'id0': 'pth', 'source': 'RTHK'},
        {'id': 'HOY_76', 'name': 'HOY 國際財經台', 'id0': '76', 'source': 'hoy'},
        {'id': 'HOY_77', 'name': 'HOY TV', 'id0': '77', 'source': 'hoy'},
        {'id': 'HOY_78', 'name': 'HOY TV 資訊台', 'id0': '78', 'source': 'hoy'},
        {'id': 'nowtv_096', 'name': 'ViuTVsix', 'id0': '096', 'source': 'nowtv'},
        {'id': 'nowtv_099', 'name': 'ViuTV', 'id0': '099', 'source': 'nowtv'},
        {'id': 'nowtv_102', 'name': 'Viu 頻道', 'id0': '102', 'source': 'nowtv'},
        {'id': 'nowtv_105', 'name': 'Now華劇台', 'id0': '105', 'source': 'nowtv'},
        {'id': 'nowtv_108', 'name': 'NowJelli', 'id0': '108', 'source': 'nowtv'},
        {'id': 'nowtv_111', 'name': 'HBO Hits', 'id0': '111', 'source': 'nowtv'},
        {'id': 'nowtv_112', 'name': 'HBO Family', 'id0': '112', 'source': 'nowtv'},
        {'id': 'nowtv_113', 'name': 'CINEMAX', 'id0': '113', 'source': 'nowtv'},
        {'id': 'nowtv_114', 'name': 'HBO Signature', 'id0': '114', 'source': 'nowtv'},
        {'id': 'nowtv_115', 'name': 'HBO', 'id0': '115', 'source': 'nowtv'},
        {'id': 'nowtv_116', 'name': 'MOVIE MOVIE', 'id0': '116', 'source': 'nowtv'},
        {'id': 'nowtv_119', 'name': 'HITS MOVIES', 'id0': '119', 'source': 'nowtv'},
        {'id': 'nowtv_133', 'name': 'Now 爆谷台', 'id0': '133', 'source': 'nowtv'},
        {'id': 'nowtv_138', 'name': 'Now爆谷星影台', 'id0': '138', 'source': 'nowtv'},
        {'id': 'nowtv_155', 'name': 'tvN', 'id0': '410288', 'source': 'epg.pw'},
        {'id': 'nowtv_200', 'name': '熊貓 TV', 'id0': '200', 'source': 'nowtv'},
        {'id': 'nowtv_208', 'name': 'Discovery Asia', 'id0': '208', 'source': 'nowtv'},
        {'id': 'nowtv_209', 'name': 'Discovery Channel', 'id0': '209', 'source': 'nowtv'},
        {'id': 'nowtv_210', 'name': '動物星球頻道', 'id0': '210', 'source': 'nowtv'},
        {'id': 'nowtv_211', 'name': 'Discovery 科學頻道', 'id0': '211', 'source': 'nowtv'},
        {'id': 'nowtv_212', 'name': 'DMAX', 'id0': '212', 'source': 'nowtv'},
        {'id': 'nowtv_213', 'name': 'TLC旅遊生活頻道', 'id0': '213', 'source': 'nowtv'},
        {'id': 'nowtv_217', 'name': 'Love Nature', 'id0': '217', 'source': 'nowtv'},
        {'id': 'nowtv_218', 'name': 'Love Nature 4K', 'id0': '218', 'source': 'nowtv'},
        {'id': 'nowtv_221', 'name': '戶外頻道', 'id0': '221', 'source': 'nowtv'},
        {'id': 'nowtv_316', 'name': 'CNN 國際新聞網絡', 'id0': '316', 'source': 'nowtv'},
        {'id': 'nowtv_321', 'name': 'Bloomberg Television', 'id0': '321', 'source': 'nowtv'},
        {'id': 'nowtv_325', 'name': '半島電視台英語頻道', 'id0': '325', 'source': 'nowtv'},
        {'id': 'nowtv_328', 'name': 'NHK WORLD-JAPAN', 'id0': '328', 'source': 'nowtv'},
        {'id': 'nowtv_329', 'name': 'RT', 'id0': '329', 'source': 'nowtv'},
        {'id': 'nowtv_330', 'name': '中國環球電視網', 'id0': '330', 'source': 'nowtv'},
        {'id': 'nowtv_331', 'name': 'Now直播台', 'id0': '331', 'source': 'nowtv'},
        {'id': 'nowtv_332', 'name': 'Now新聞台', 'id0': '332', 'source': 'nowtv'},
        {'id': 'nowtv_333', 'name': 'Now財經台', 'id0': '333', 'source': 'nowtv'},
        {'id': 'nowtv_336', 'name': 'Now報價台', 'id0': '410346', 'source': 'epg.pw'},
        {'id': 'nowtv_366', 'name': '鳳凰衛視資訊台', 'id0': '366', 'source': 'nowtv'},
        {'id': 'nowtv_502', 'name': 'BBC Lifestyle', 'id0': '410365', 'source': 'epg.pw'},
        {'id': 'nowtv_513', 'name': 'HITS', 'id0': '513', 'source': 'nowtv'},
        {'id': 'nowtv_517', 'name': 'ROCK Entertainment', 'id0': '410367', 'source': 'epg.pw'},
        {'id': 'nowtv_525', 'name': 'Lifetime', 'id0': '410368', 'source': 'epg.pw'},
        {'id': 'nowtv_538', 'name': '中天亞洲台', 'id0': '538', 'source': 'nowtv'},
        {'id': 'nowtv_540', 'name': '深圳衛視', 'id0': '540', 'source': 'nowtv'},
        {'id': 'nowtv_541', 'name': 'CCTV-1', 'id0': '541', 'source': 'nowtv'},
        {'id': 'nowtv_542', 'name': 'CCTV-4', 'id0': '542', 'source': 'nowtv'},
        {'id': 'nowtv_543', 'name': '大灣區衛視', 'id0': '543', 'source': 'nowtv'},
        {'id': 'nowtv_545', 'name': '中央電視台新聞頻道', 'id0': '545', 'source': 'nowtv'},
        {'id': 'nowtv_548', 'name': '鳳凰衛視中文台', 'id0': '548', 'source': 'nowtv'},
        {'id': 'nowtv_551', 'name': '東方衛視國際頻道', 'id0': '551', 'source': 'nowtv'},
        {'id': 'nowtv_553', 'name': '三沙衛視', 'id0': '553', 'source': 'nowtv'},
        {'id': 'nowtv_561', 'name': 'ABC Australia', 'id0': '561', 'source': 'nowtv'},
        {'id': 'nowtv_611', 'name': 'Now Sports 4K 1', 'id0': '611', 'source': 'nowtv'},
        {'id': 'nowtv_612', 'name': 'Now Sports 4K 2', 'id0': '410385', 'source': 'epg.pw'},
        {'id': 'nowtv_613', 'name': 'Now Sports 4K 3', 'id0': '410386', 'source': 'epg.pw'},
        {'id': 'nowtv_620', 'name': 'Now Sports Premier League TV', 'id0': '410387', 'source': 'epg.pw'},
        {'id': 'nowtv_621', 'name': 'Now Sports 英超1台', 'id0': '621', 'source': 'nowtv'},
        {'id': 'nowtv_622', 'name': 'Now Sports 英超2台', 'id0': '410389', 'source': 'epg.pw'},
        {'id': 'nowtv_623', 'name': 'Now Sports 英超3台', 'id0': '410390', 'source': 'epg.pw'},
        {'id': 'nowtv_624', 'name': 'Now Sports 英超4台', 'id0': '410391', 'source': 'epg.pw'},
        {'id': 'nowtv_625', 'name': 'Now Sports 英超5台', 'id0': '410392', 'source': 'epg.pw'},
        {'id': 'nowtv_626', 'name': 'Now Sports 英超6台', 'id0': '415544', 'source': 'epg.pw'},
        {'id': 'nowtv_627', 'name': 'Now Sports 英超7台', 'id0': '415545', 'source': 'epg.pw'},
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
        {'id': 'nowtv_640', 'name': '曼聯電視頻道', 'id0': '410405', 'source': 'epg.pw'},
        {'id': 'nowtv_641', 'name': 'Now Sports 641', 'id0': '641', 'source': 'nowtv'},
        {'id': 'nowtv_642', 'name': 'NBA TV', 'id0': '642', 'source': 'nowtv'},
        {'id': 'nowtv_643', 'name': 'beIN SPORTS 3', 'id0': '410408', 'source': 'epg.pw'},
        {'id': 'nowtv_644', 'name': 'beIN SPORTS 4', 'id0': '410409', 'source': 'epg.pw'},
        {'id': 'nowtv_645', 'name': 'beIN SPORTS 5', 'id0': '410410', 'source': 'epg.pw'},
        {'id': 'nowtv_646', 'name': 'beIN SPORTS 6', 'id0': '410411', 'source': 'epg.pw'},
        {'id': 'nowtv_647', 'name': 'Now Sports 647', 'id0': '421332', 'source': 'epg.pw'},
        {'id': 'nowtv_651', 'name': 'Now Sports 651', 'id0': '410412', 'source': 'epg.pw'},
        {'id': 'nowtv_652', 'name': 'Now Sports 652', 'id0': '410413', 'source': 'epg.pw'},
        {'id': 'nowtv_668', 'name': 'Now668', 'id0': '410414', 'source': 'epg.pw'},
        {'id': 'nowtv_674', 'name': 'Cricbuzz', 'id0': '674', 'source': 'nowtv'},
        {'id': 'nowtv_679', 'name': 'Premier Sports', 'id0': '410418', 'source': 'epg.pw'},
        {'id': 'nowtv_680', 'name': 'Now Sports Plus', 'id0': '680', 'source': 'nowtv'},
        {'id': 'nowtv_683', 'name': 'Now Golf 2', 'id0': '683', 'source': 'nowtv'},
        {'id': 'nowtv_684', 'name': 'Now Golf 3', 'id0': '684', 'source': 'nowtv'},
        {'id': 'nowtv_688', 'name': 'Lucky 688', 'id0': '688', 'source': 'nowtv'},
        {'id': 'tvb_CWIN', 'name': 'SUPER FREE (免費)', 'id0': '368376', 'source': 'epg.pw'},
        {'id': 'tvb_SVAR', 'name': 'SUPER獎門人 (免費)', 'id0': '430854', 'source': 'epg.pw'},
        {'id': 'tvb_SEYT', 'name': '愛．回家SUPER煲 (免費)', 'id0': '430550', 'source': 'epg.pw'},
        {'id': 'tvb_SFOO', 'name': 'SUPER識食 (免費)', 'id0': '430554', 'source': 'epg.pw'},
        {'id': 'tvb_STRA', 'name': 'SUPER FUN (免費)', 'id0': '430552', 'source': 'epg.pw'},
        {'id': 'tvb_SMUS', 'name': 'SUPER Music (免費)', 'id0': '430553', 'source': 'epg.pw'},
        {'id': 'tvb_SGOL', 'name': 'SUPER驚 (免費)', 'id0': '431161', 'source': 'epg.pw'},
        {'id': 'tvb_SSIT', 'name': 'SUPER煲劇 (免費)', 'id0': '430551', 'source': 'epg.pw'},
        {'id': 'tvb_STVM', 'name': 'SUPER亞視劇 (免費)', 'id0': '430555', 'source': 'epg.pw'},
        {'id': 'tvb_SDOC', 'name': '真情SUPER煲 (免費)', 'id0': '431446', 'source': 'epg.pw'},
        {'id': 'tvb_SSPT', 'name': 'SUPER Sports (免費)', 'id0': '430853', 'source': 'epg.pw'},
        {'id': 'tvb_C18', 'name': 'myTV SUPER 18台', 'id0': '368334', 'source': 'epg.pw'},
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
        {'id': 'tvb_PULS', 'name': 'Wild Stuff (免費)', 'id0': '430250', 'source': 'epg.pw'},
        {'id': 'tvb_CRTE', 'name': 'ROCK綜藝娛樂', 'id0': '368332', 'source': 'epg.pw'},
        {'id': 'tvb_RKEX', 'name': 'ROCK X Stream', 'id0': '443416', 'source': 'epg.pw'},
        {'id': 'tvb_CJTV', 'name': 'tvN', 'id0': '368326', 'source': 'epg.pw'},
        {'id': 'tvb_CTS1', 'name': '無線衛星亞洲台', 'id0': '368357', 'source': 'epg.pw'},
        {'id': 'tvb_CRE', 'name': '創世電視 (免費)', 'id0': '368329', 'source': 'epg.pw'},
        {'id': 'tvb_FBX', 'name': 'FashionBox', 'id0': '368374', 'source': 'epg.pw'},
        {'id': 'tvb_CC1', 'name': '中央電視台綜合頻道 (港澳版) (免費)', 'id0': '368375', 'source': 'epg.pw'},
        {'id': 'tvb_CGD', 'name': 'CGTN (中國環球電視網)記錄頻道 (免費)', 'id0': '368347', 'source': 'epg.pw'},
        {'id': 'tvb_CGE', 'name': 'CGTN (中國環球電視網)英語頻道 (免費)', 'id0': '368346', 'source': 'epg.pw'},
        {'id': 'tvb_DTV', 'name': '東方衛視國際頻道 (免費)', 'id0': '368340', 'source': 'epg.pw'},
        {'id': 'tvb_CC4', 'name': '中國中央電視台中文國際頻道 (免費)', 'id0': '425931', 'source': 'epg.pw'},
        {'id': 'tvb_CCE', 'name': '中國中央電視台娛樂頻道 (免費)', 'id0': '425925', 'source': 'epg.pw'},
        {'id': 'tvb_CCO', 'name': '中國中央電視台戲曲頻道 (免費)', 'id0': '425924', 'source': 'epg.pw'},
        {'id': 'tvb_YNTV', 'name': '雲南瀾湄國際衛視 (免費)', 'id0': '425933', 'source': 'epg.pw'},
        {'id': 'tvb_AHTV', 'name': '安徽廣播電視台國際頻道 (免費)', 'id0': '425930', 'source': 'epg.pw'},
        {'id': 'tvb_BJTV', 'name': '北京電視台國際頻道 (免費)', 'id0': '425922', 'source': 'epg.pw'},
        {'id': 'tvb_FJTV', 'name': '福建海峽衛視國際頻道 (免費)', 'id0': '425921', 'source': 'epg.pw'},
        {'id': 'tvb_HNTV', 'name': '湖南電視台國際頻道 (免費)', 'id0': '425923', 'source': 'epg.pw'},
        {'id': 'tvb_JSTV', 'name': '江蘇電視台國際頻道 (免費)', 'id0': '425928', 'source': 'epg.pw'},
        {'id': 'tvb_GBTV', 'name': '廣東廣播電視台大灣區衛視頻道 (免費)', 'id0': '425926', 'source': 'epg.pw'},
        {'id': 'tvb_ZJTV', 'name': '浙江電視台國際頻道 (免費)', 'id0': '425932', 'source': 'epg.pw'},
        {'id': 'tvb_SZTV', 'name': '深圳衛視國際頻道 (免費)', 'id0': '425927', 'source': 'epg.pw'},
        {'id': 'tvb_NOW7', 'name': "that's 70s (免費)", 'id0': '430253', 'source': 'epg.pw'},
        {'id': 'tvb_NOW8', 'name': "that's 80s (免費)", 'id0': '430251', 'source': 'epg.pw'},
        {'id': 'tvb_NOWR', 'name': "that's Rock (免費)", 'id0': '430258', 'source': 'epg.pw'},
        {'id': 'tvb_NOW9', 'name': "that's 90s00s (免費)", 'id0': '430252', 'source': 'epg.pw'},
        {'id': 'tvb_CONC', 'name': 'Concerto (免費)', 'id0': '430246', 'source': 'epg.pw'},
        {'id': 'tvb_TRUR', 'name': 'TRACE Urban (免費)', 'id0': '430245', 'source': 'epg.pw'},
        {'id': 'tvb_NWDR', 'name': 'NewTV古裝劇場 (免費)', 'id0': '548540', 'source': 'epg.pw'},
        {'id': 'tvb_NWED', 'name': 'New TV科教 (免費)', 'id0': '548541', 'source': 'epg.pw'},
        {'id': 'tvb_NWHE', 'name': 'NewTV養生 (免費)', 'id0': '548543', 'source': 'epg.pw'},
        {'id': 'tvb_NWMA', 'name': 'NewTV功夫 (免費)', 'id0': '548542', 'source': 'epg.pw'},
        {'id': 'tvb_CTSN', 'name': '無線衛星新聞台', 'id0': '368363', 'source': 'epg.pw'},
        {'id': 'tvb_CCNA', 'name': '亞洲新聞台', 'id0': '368377', 'source': 'epg.pw'},
        {'id': 'tvb_CJAZ', 'name': '半島電視台英語頻道', 'id0': '368327', 'source': 'epg.pw'},
        {'id': 'tvb_CF24', 'name': 'France 24', 'id0': '368342', 'source': 'epg.pw'},
        {'id': 'tvb_CDW1', 'name': 'DW', 'id0': '368373', 'source': 'epg.pw'},
        {'id': 'tvb_CNHK', 'name': 'NHK World-Japan', 'id0': '368337', 'source': 'epg.pw'},
        {'id': 'tvb_CARI', 'name': 'Arirang TV', 'id0': '368370', 'source': 'epg.pw'},
        {'id': 'tvb_NSWD', 'name': 'NewsWorld (免費)', 'id0': '430247', 'source': 'epg.pw'},
        {'id': 'tvb_INDO', 'name': 'The Indonesia Channel (免費)', 'id0': '548544', 'source': 'epg.pw'},
        {'id': 'tvb_EVT2', 'name': 'myTV SUPER直播足球2台', 'id0': '397763', 'source': 'epg.pw'},
        {'id': 'tvb_EVT3', 'name': 'myTV SUPER直播足球3台', 'id0': '368345', 'source': 'epg.pw'},
        {'id': 'tvb_EVT4', 'name': 'myTV SUPER直播足球4台', 'id0': '368328', 'source': 'epg.pw'},
        {'id': 'tvb_EVT5', 'name': 'myTV SUPER直播足球5台', 'id0': '368379', 'source': 'epg.pw'},
        {'id': 'tvb_EVT6', 'name': 'myTV SUPER直播足球6台', 'id0': '398976', 'source': 'epg.pw'},
        {'id': 'tvb_EVT7', 'name': 'myTV SUPER直播足球7台', 'id0': '416310', 'source': 'epg.pw'},
        {'id': 'tvb_TEST', 'name': '測試頻道', 'id0': '368378', 'source': 'epg.pw'},
        {'id': 'fengshows_1', 'name': '資訊台', 'id0': "7c96b084-60e1-40a9-89c5-682b994fb680", 'source': 'fengshows'},
        {'id': 'fengshows_2', 'name': '中文台', 'id0': "f7f48462-9b13-485b-8101-7b54716411ec", 'source': 'fengshows'},
        {'id': 'fengshows_3', 'name': '香港台', 'id0': "15e02d92-1698-416c-af2f-3e9a872b4d78", 'source': 'fengshows'},
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
        {'id': 'mod_211', 'name': '211 DAZN 3', 'id0': '211', 'source': 'mod'},
        {'id': 'mod_212', 'name': '212 博斯運動一台', 'id0': '212', 'source': 'mod'},
        {'id': 'mod_213', 'name': '213 博斯運動二台', 'id0': '213', 'source': 'mod'},
        {'id': 'mod_214', 'name': '214 DAZN 2', 'id0': '214', 'source': 'mod'},
        {'id': 'mod_216', 'name': '216 EUROSPORT', 'id0': '216', 'source': 'mod'},
        {'id': 'mod_250', 'name': '250 麥哲倫頻道', 'id0': '250', 'source': 'mod'},
        {'id': 'mod_252', 'name': '252 BBC Earth', 'id0': '252', 'source': 'mod'},
        {'id': 'mod_253', 'name': '253 Discovery Asia', 'id0': '253', 'source': 'mod'},
        {'id': 'mod_254', 'name': '254 Discovery科學頻道', 'id0': '254', 'source': 'mod'},
        {'id': 'mod_255', 'name': '255 DMAX', 'id0': '255', 'source': 'mod'},
        {'id': 'mod_256', 'name': '256 EVE', 'id0': '256', 'source': 'mod'},
        {'id': 'mod_258', 'name': '258 歷史頻道', 'id0': '258', 'source': 'mod'},
        {'id': 'mod_259', 'name': '259 罪案偵緝頻道', 'id0': '259', 'source': 'mod'},
        {'id': 'mod_260', 'name': '260 BBC Lifestyle Channel', 'id0': '260', 'source': 'mod'},
        {'id': 'mod_262', 'name': '262 PET CLUB TV', 'id0': '262', 'source': 'mod'},
        {'id': 'mod_264', 'name': '264 Lifetime', 'id0': '264', 'source': 'mod'},
        {'id': 'mod_268', 'name': '268 HGTV 居家樂活頻道', 'id0': '268', 'source': 'mod'},
        {'id': 'mod_276', 'name': '276 Asian Food Network 亞洲美食頻道', 'id0': '276', 'source': 'mod'},
        {'id': 'mod_277', 'name': '277 Food Network 美食台頻道', 'id0': '277', 'source': 'mod'},
        {'id': 'mod_280', 'name': '280 Travel Channel', 'id0': '280', 'source': 'mod'},
        {'id': 'mod_310', 'name': '310 中視菁采台', 'id0': '310', 'source': 'mod'},
        {'id': 'mod_316', 'name': '316 民視第一台', 'id0': '316', 'source': 'mod'},
        {'id': 'mod_317', 'name': '317 民視台灣台', 'id0': '317', 'source': 'mod'},
        {'id': 'mod_320', 'name': '320 新唐人亞太台', 'id0': '320', 'source': 'mod'},
        {'id': 'mod_377', 'name': '377 韓國娛樂台KMTV', 'id0': '377', 'source': 'mod'},
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
        {'id': 'mod_553', 'name': '553 CNA', 'id0': '553', 'source': 'mod'},
        {'id': 'mod_558', 'name': '558 TaiwanPlus', 'id0': '558', 'source': 'mod'},
        {'id': 'mod_600', 'name': '600 視納華仁紀實台', 'id0': '600', 'source': 'mod'},
        {'id': 'mod_601', 'name': '601 影迷數位紀實台', 'id0': '601', 'source': 'mod'},
        {'id': 'mod_610', 'name': '610 美亞電影台', 'id0': '610', 'source': 'mod'},
        {'id': 'mod_616', 'name': '616 Warner TV', 'id0': '616', 'source': 'mod'},
        {'id': 'mod_619', 'name': '619 amc電影台', 'id0': '619', 'source': 'mod'},
        {'id': 'mod_626', 'name': '626 CatchPlay電影台', 'id0': '626', 'source': 'mod'},
        {'id': 'mod_627', 'name': '627 CinemaWorld', 'id0': '627', 'source': 'mod'},
        {'id': 'mod_628', 'name': '628 壹電視電影台', 'id0': '628', 'source': 'mod'},
        {'id': 'mod_629', 'name': '629 采昌影劇台', 'id0': '629', 'source': 'mod'},
        {'id': 'mod_630', 'name': '630 影迷數位電影台', 'id0': '630', 'source': 'mod'},
        {'id': 'mod_633', 'name': '633 My Cinema Europe HD 我的歐洲電影', 'id0': '633', 'source': 'mod'},
        {'id': 'tbc_019', 'name': 'Discovery', 'id0': '019', 'source': 'tbc'},
        {'id': 'tbc_020', 'name': 'TLC旅遊生活頻道', 'id0': '021', 'source': 'tbc'},
        {'id': 'tbc_021', 'name': '動物星球', 'id0': '022', 'source': 'tbc'},
        {'id': 'tbc_024', 'name': 'MOMO親子台', 'id0': '024', 'source': 'tbc'},
        {'id': 'tbc_025', 'name': '東森幼幼台', 'id0': '025', 'source': 'tbc'},
        {'id': 'tbc_026', 'name': '緯來綜合台', 'id0': '026', 'source': 'tbc'},
        {'id': 'tbc_027', 'name': '八大第一台', 'id0': '027', 'source': 'tbc'},
        {'id': 'tbc_028', 'name': '八大綜合台', 'id0': '028', 'source': 'tbc'},
        {'id': 'tbc_029', 'name': '三立台灣台', 'id0': '029', 'source': 'tbc'},
        {'id': 'tbc_030', 'name': '三立都會台', 'id0': '030', 'source': 'tbc'},
        {'id': 'tbc_032', 'name': '東森綜合台', 'id0': '032', 'source': 'tbc'},
        {'id': 'tbc_033', 'name': '東森超視', 'id0': '033', 'source': 'tbc'},
        {'id': 'tbc_036', 'name': '中天綜合台', 'id0': '036', 'source': 'tbc'},
        {'id': 'tbc_038', 'name': '年代MUCH TV', 'id0': '038', 'source': 'tbc'},
        {'id': 'tbc_039', 'name': '中天娛樂台', 'id0': '039', 'source': 'tbc'},
        {'id': 'tbc_040', 'name': '東森戲劇台', 'id0': '040', 'source': 'tbc'},
        {'id': 'tbc_041', 'name': '八大戲劇台', 'id0': '041', 'source': 'tbc'},
        {'id': 'tbc_042', 'name': 'TVBS歡樂台', 'id0': '042', 'source': 'tbc'},
        {'id': 'tbc_043', 'name': '緯來戲劇台', 'id0': '043', 'source': 'tbc'},
        {'id': 'tbc_050', 'name': '年代新聞台', 'id0': '050', 'source': 'tbc'},
        {'id': 'tbc_051', 'name': '東森新聞台', 'id0': '051', 'source': 'tbc'},
        {'id': 'tbc_054', 'name': '三立新聞台', 'id0': '054', 'source': 'tbc'},
        {'id': 'tbc_055', 'name': 'TVBS 新聞台', 'id0': '055', 'source': 'tbc'},
        {'id': 'tbc_056', 'name': 'TVBS', 'id0': '056', 'source': 'tbc'},
        {'id': 'tbc_057', 'name': '東森財經新聞台', 'id0': '057', 'source': 'tbc'},
        {'id': 'tbc_058', 'name': '非凡新聞台', 'id0': '058', 'source': 'tbc'},
        {'id': 'tbc_062', 'name': '東森電影台', 'id0': '062', 'source': 'tbc'},
        {'id': 'tbc_063', 'name': '緯來電影台', 'id0': '063', 'source': 'tbc'},
        {'id': 'tbc_064', 'name': 'LS Time電影台', 'id0': '064', 'source': 'tbc'},
        {'id': 'tbc_065', 'name': 'HBO', 'id0': '065', 'source': 'tbc'},
        {'id': 'tbc_066', 'name': '東森洋片台', 'id0': '066', 'source': 'tbc'},
        {'id': 'tbc_067', 'name': 'AXN', 'id0': '067', 'source': 'tbc'},
        {'id': 'tbc_068', 'name': '好萊塢電影台', 'id0': '068', 'source': 'tbc'},
        {'id': 'tbc_070', 'name': '緯來育樂台', 'id0': '070', 'source': 'tbc'},
        {'id': 'tbc_071', 'name': 'CINEMAX', 'id0': '071', 'source': 'tbc'},
        {'id': 'tbc_072', 'name': '緯來體育台', 'id0': '072', 'source': 'tbc'},
        {'id': 'tbc_073', 'name': 'DAZN 1', 'id0': '073', 'source': 'tbc'},
        {'id': 'tbc_074', 'name': 'DAZN 2', 'id0': '074', 'source': 'tbc'},
        {'id': 'tbc_077', 'name': '緯來日本台', 'id0': '077', 'source': 'tbc'},
        {'id': 'tbc_089', 'name': '非凡商業台', 'id0': '089', 'source': 'tbc'},
        {'id': 'tbc_207', 'name': 'HBO HD', 'id0': '207', 'source': 'tbc'},
        {'id': 'tbc_208', 'name': 'HBO 強檔鉅獻', 'id0': '208', 'source': 'tbc'},
        {'id': 'tbc_209', 'name': 'HBO 原創鉅獻', 'id0': '209', 'source': 'tbc'},
        {'id': 'tbc_210', 'name': 'HBO 溫馨家庭', 'id0': '210', 'source': 'tbc'},
        {'id': 'hami_OTT_LIVE_0000001853', 'name': '愛爾達體育MAX1台', 'id0': 'OTT_LIVE_0000001853', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001854', 'name': '愛爾達體育MAX2台', 'id0': 'OTT_LIVE_0000001854', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001855', 'name': '愛爾達體育MAX3台', 'id0': 'OTT_LIVE_0000001855', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001856', 'name': '愛爾達體育MAX4台', 'id0': 'OTT_LIVE_0000001856', 'source': 'hami'},
        {'id': 'hami_OTT_LIVE_0000001919', 'name': '動態雷達視角', 'id0': 'OTT_LIVE_0000001919', 'source': 'hami'},        
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
        {'id': 'ntd_usa_east', 'name': '新唐人美東', 'id0': 'ntd_usa_east', 'source': 'ntdtv'},
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
        {'id': 'astro_300', 'name': 'iQIYI HD', 'id0': '1006', 'source': 'astro'},
        {'id': 'astro_305', 'name': 'TVB Classic HD', 'id0': '3895', 'source': 'epg.pw'},
        {'id': 'astro_306', 'name': 'AEC HD', 'id0': '2400', 'source': 'astro'},
        {'id': 'astro_308', 'name': 'QJ HD', 'id0': '2507', 'source': 'astro'},
        {'id': 'astro_309', 'name': 'CELESTIAL HD', 'id0': '506', 'source': 'astro'},
        {'id': 'astro_310', 'name': 'TVBJ', 'id0': '2600', 'source': 'astro'},
        {'id': 'astro_311', 'name': 'AOD HD', 'id0': '2706', 'source': 'astro'},
        {'id': 'astro_316', 'name': 'CTI ASIA HD', 'id0': '5017', 'source': 'astro'},
        {'id': 'astro_317', 'name': 'TVB E-NEWS HD', 'id0': '5015', 'source': 'astro'},
        {'id': 'astro_319', 'name': 'TVB XING HE HD', 'id0': '401', 'source': 'astro'},
        {'id': 'astro_320', 'name': 'TVBS ASIA HD', 'id0': '402', 'source': 'astro'},
        {'id': 'astro_321', 'name': 'CCM', 'id0': '100', 'source': 'astro'},
        {'id': 'astro_325', 'name': 'PHOENIX HD', 'id0': '400', 'source': 'astro'},
        {'id': 'astro_326', 'name': 'PHOENIX NEWS HD', 'id0': '5009', 'source': 'astro'},
        {'id': 'astro_333', 'name': 'HUA HEE DAI HD', 'id0': '2308', 'source': 'astro'},
        {'id': 'astro_335', 'name': 'CCTV4 HD', 'id0': '403', 'source': 'astro'},
        {'id': 'astro_392', 'name': 'KBSW HD', 'id0': '2306', 'source': 'astro'},
        {'id': 'astro_395', 'name': 'tvN HD', 'id0': '2323', 'source': 'epg.pw'},
        {'id': 'astro_396', 'name': 'K-Plus HD', 'id0': '2652', 'source': 'epg.pw'},
        {'id': 'astro_398', 'name': 'NHK World Premium', 'id0': '3929', 'source': 'epg.pw'},
        {'id': 'astro_401', 'name': 'HITS Movies HD', 'id0': '3575', 'source': 'epg.pw'},
        {'id': 'astro_404', 'name': 'BOO HD', 'id0': '2636', 'source': 'epg.pw'},
        {'id': 'astro_413', 'name': 'SHOWCASE MOVIES', 'id0': '4057', 'source': 'epg.pw'},
        {'id': 'astro_416', 'name': 'tvN Movies HD', 'id0': '2726', 'source': 'epg.pw'},
        {'id': 'astro_501', 'name': 'Astro Awani HD', 'id0': '3958', 'source': 'epg.pw'},
        {'id': 'astro_502', 'name': 'BERNAMA', 'id0': '1835', 'source': 'epg.pw'},
        {'id': 'astro_503', 'name': 'CGTN HD', 'id0': '3906', 'source': 'epg.pw'},
        {'id': 'astro_511', 'name': 'CNN HD', 'id0': '3179', 'source': 'epg.pw'},
        {'id': 'astro_512', 'name': 'BBC News HD', 'id0': '3329', 'source': 'epg.pw'},
        {'id': 'astro_513', 'name': 'Al Jazeera English HD', 'id0': '3416', 'source': 'epg.pw'},
        {'id': 'astro_515', 'name': 'CNA HD', 'id0': '2852', 'source': 'epg.pw'},
        {'id': 'astro_516', 'name': 'CNBC Asia HD', 'id0': '3873', 'source': 'epg.pw'},
        {'id': 'astro_517', 'name': 'Bloomberg TV HD', 'id0': '3858', 'source': 'epg.pw'},
        {'id': 'astro_518', 'name': 'ABC Australia HD', 'id0': '4130', 'source': 'epg.pw'},
        {'id': 'astro_521', 'name': 'DW English', 'id0': '2756', 'source': 'epg.pw'},
        {'id': 'astro_522', 'name': 'France24', 'id0': '2781', 'source': 'epg.pw'},
        {'id': 'astro_549', 'name': 'Love Nature 4K', 'id0': '4171', 'source': 'epg.pw'},
        {'id': 'astro_550', 'name': 'Love Nature', 'id0': '4196', 'source': 'epg.pw'},
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
        {'id': 'astro_701', 'name': 'AXN HD', 'id0': '1205', 'source': 'epg.pw'},
        {'id': 'astro_702', 'name': 'HITS NOW', 'id0': '186250', 'source': 'epg.pw'},
        {'id': 'astro_703', 'name': 'Lifetime HD', 'id0': '3968', 'source': 'epg.pw'},
        {'id': 'astro_706', 'name': 'HITS HD', 'id0': '2208', 'source': 'epg.pw'},
        {'id': 'astro_707', 'name': 'TLC HD', 'id0': '3234', 'source': 'epg.pw'},
        {'id': 'astro_709', 'name': 'Asian Food Network HD', 'id0': '997', 'source': 'epg.pw'},
        {'id': 'astro_714', 'name': 'Crime & Investigation HD', 'id0': '3362', 'source': 'epg.pw'},
        {'id': 'astro_715', 'name': 'HGTV HD', 'id0': '2473', 'source': 'epg.pw'},
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
        {'id': 'astro_826', 'name': 'W-Sport', 'id0': '48630', 'source': 'epg.pw'},
        {'id': 'astro_831', 'name': 'Golf Channel HD', 'id0': '2300', 'source': 'epg.pw'},
        {'id': 'astro_832', 'name': 'CricBuzz', 'id0': '523496', 'source': 'epg.pw'},
        {'id': 'astro_833', 'name': 'Premier Sports', 'id0': '3625', 'source': 'epg.pw'},
        {'id': 'starhubtvplus_101', 'name': 'Preview Channel', 'id0': '7c9126e4-f92c-42d6-a381-3ba640da04b9', 'source': 'starhub'},
        {'id': 'starhubtvplus_111', 'name': 'Hub E City HD', 'id0': '3181b9a2-f8f4-489c-b8fd-d19f923c6f62', 'source': 'starhub'},
        {'id': 'starhubtvplus_115', 'name': 'Citra Entertainment', 'id0': 'f8b64a5d-438f-47e7-b516-2a902d7bc21d', 'source': 'starhub'},
        {'id': 'starhubtvplus_116', 'name': 'Karisma', 'id0': '9394fd45-230a-40cc-b19b-e1ba30972c04', 'source': 'starhub'},
        {'id': 'starhubtvplus_118', 'name': 'Astro Warna', 'id0': '1419f892-2abd-4717-a9e9-b2299fee00f5', 'source': 'starhub'},
        {'id': 'starhubtvplus_123', 'name': 'Hub Sensasi', 'id0': 'ee4fe8fa-b213-4dd7-8ccf-541065bb8d12', 'source': 'starhub'},
        {'id': 'starhubtvplus_125', 'name': 'Zee TV', 'id0': '051b7938-b79f-4fd2-80d3-ebf3ebcea931', 'source': 'starhub'},
        {'id': 'starhubtvplus_127', 'name': 'Sony Entertainment Television', 'id0': 'd66e833d-4c36-4989-83f7-777e7773d4bd', 'source': 'starhub'},
        {'id': 'starhubtvplus_128', 'name': 'COLORS', 'id0': 'c170ab01-3fe1-453e-850f-815b29931ff7', 'source': 'starhub'},
        {'id': 'starhubtvplus_130', 'name': 'Zee Cinema', 'id0': '5f52f2b3-e45a-40a5-bcf3-2dd75a5543f8', 'source': 'starhub'},
        {'id': 'starhubtvplus_131', 'name': 'SONY MAX', 'id0': '0a9604e3-35dc-4c90-a9e4-39ea7f39c9d6', 'source': 'starhub'},
        {'id': 'starhubtvplus_132', 'name': 'COLORS Tamil HD', 'id0': '32897913-6eff-45db-90e9-948b56bddbb6', 'source': 'starhub'},
        {'id': 'starhubtvplus_133', 'name': 'Sun TV', 'id0': '2a2b35a1-fbc2-44f0-8234-136fd6429b68', 'source': 'starhub'},
        {'id': 'starhubtvplus_134', 'name': 'Sun Music', 'id0': '9fbf2a7c-878f-4659-91c3-0b20db468d91', 'source': 'starhub'},
        {'id': 'starhubtvplus_135', 'name': 'Vijay TV', 'id0': 'c7fec37a-8cbe-4b56-84e2-1428c82910a4', 'source': 'starhub'},
        {'id': 'starhubtvplus_136', 'name': 'Vannathirai', 'id0': '4c802d42-f7e6-40cf-b424-3aab3f5f9761', 'source': 'starhub'},
        {'id': 'starhubtvplus_137', 'name': 'Zee Thirai', 'id0': 'e0483b3c-33fe-442e-b0bd-8747f6f04f6e', 'source': 'starhub'},
        {'id': 'starhubtvplus_138', 'name': 'Zee Tamil', 'id0': 'aebb3170-e2ec-42cd-ae26-af914bf34045', 'source': 'starhub'},
        {'id': 'starhubtvplus_139', 'name': 'Asianet', 'id0': '385da56a-d445-4711-a6a0-6a3a80daa9a8', 'source': 'starhub'},
        {'id': 'starhubtvplus_140', 'name': 'Asianet Movies', 'id0': 'aeac111e-e284-41d9-b6b5-ae13f6dbe67b', 'source': 'starhub'},
        {'id': 'starhubtvplus_141', 'name': 'Kalaignar TV', 'id0': '6ffaeb9f-2388-4f27-bd04-a71dba7c55a9', 'source': 'starhub'},
        {'id': 'starhubtvplus_143', 'name': 'ANC', 'id0': '5711b532-844b-441d-841a-18bdb1ef1094', 'source': 'starhub'},
        {'id': 'starhubtvplus_144', 'name': 'The Filipino Channel', 'id0': 'a16319f5-416e-4bc7-9ee0-42c7c3911f98', 'source': 'starhub'},
        {'id': 'starhubtvplus_145', 'name': 'Cinema One Global', 'id0': '50b86b7f-084e-4ea1-8610-22e86c733c1c', 'source': 'starhub'},
        {'id': 'starhubtvplus_152', 'name': 'TV5MONDE HD', 'id0': '0c28c445-abad-467d-9559-211174718745', 'source': 'starhub'},
        {'id': 'starhubtvplus_153', 'name': 'DW (Deutsch)', 'id0': '37494f1f-0748-4150-bfbc-eb24b0bf1a34', 'source': 'starhub'},
        {'id': 'starhubtvplus_158', 'name': 'ADITHYA TV', 'id0': '0e9b041d-8880-4b3d-8f6f-3863358c7eff', 'source': 'starhub'},
        {'id': 'starhubtvplus_159', 'name': 'KTV HD', 'id0': '2eb726de-6d6a-4af6-a1a7-08805cf783f9', 'source': 'starhub'},
        {'id': 'starhubtvplus_201', 'name': 'Hub Sports 1  HD', 'id0': 'b5c3d45b-e2c9-462b-bcf1-06a149d68f25', 'source': 'starhub'},
        {'id': 'starhubtvplus_202', 'name': 'Hub Sports 2 HD', 'id0': '347fa620-e966-423c-8d46-98469f0fc974', 'source': 'starhub'},
        {'id': 'starhubtvplus_203', 'name': 'Hub Sports 3 HD', 'id0': '4ff7b357-9338-41a3-b7be-ede530555279', 'source': 'starhub'},
        {'id': 'starhubtvplus_204', 'name': 'Hub Sports 4 HD', 'id0': '753b50fe-262e-48da-9b5e-3fd9894ff531', 'source': 'starhub'},
        {'id': 'starhubtvplus_205', 'name': 'Hub Sports 5 HD', 'id0': '38df8124-1bcd-49b6-abb3-ee230a1f40d2', 'source': 'starhub'},
        {'id': 'starhubtvplus_209', 'name': 'SPOTV', 'id0': 'e90f7070-37bc-431d-ae30-137a5ec5e8e4', 'source': 'starhub'},
        {'id': 'starhubtvplus_210', 'name': 'SPOTV2', 'id0': '0e9c2522-9489-43d9-ba57-cc8750937972', 'source': 'starhub'},
        {'id': 'starhubtvplus_211', 'name': 'beIN Sports 2 HD', 'id0': '6fb02848-2b74-4803-9661-ab4ff642764b', 'source': 'starhub'},
        {'id': 'starhubtvplus_213', 'name': 'beIN Sports HD', 'id0': '9f3a21bb-b934-4147-bfb9-888057ec0657', 'source': 'starhub'},
        {'id': 'starhubtvplus_214', 'name': 'beIN Sports 3', 'id0': '249f5236-ca5d-416d-98b2-7e6961f1bccd', 'source': 'starhub'},
        {'id': 'starhubtvplus_215', 'name': 'beIN SPORTS MAX 2 HD', 'id0': 'd27c53da-c95d-466f-8d31-f67acdc5528a', 'source': 'starhub'},
        {'id': 'starhubtvplus_216', 'name': 'beIN SPORTS MAX 3 HD', 'id0': 'ca9c0027-5619-406d-a6b5-a6eca8a9f291', 'source': 'starhub'},
        {'id': 'starhubtvplus_217', 'name': 'Cricbuzz', 'id0': 'c1b5b301-8e85-4ad3-a0f4-cd1a49ffbd4d', 'source': 'starhub'},
        {'id': 'starhubtvplus_218', 'name': 'Cricbuzz 2', 'id0': 'a68f6d1e-0141-4f5a-bbbc-fa81888e08a8', 'source': 'starhub'},
        {'id': 'starhubtvplus_221', 'name': 'Hub Premier 1', 'id0': '5cee1079-1bb5-4054-ae02-0322144a248b', 'source': 'starhub'},
        {'id': 'starhubtvplus_222', 'name': 'Hub Premier 2 (HD)', 'id0': '6f186614-28de-416a-b8a6-02fa5c579aa7', 'source': 'starhub'},
        {'id': 'starhubtvplus_223', 'name': 'Hub Premier 3', 'id0': '248a8c09-1327-44cc-b652-a66715cfc26d', 'source': 'starhub'},
        {'id': 'starhubtvplus_224', 'name': 'Hub Premier 4', 'id0': 'a8bfda3d-d820-4c40-ab75-2f8b9e905862', 'source': 'starhub'},
        {'id': 'starhubtvplus_225', 'name': 'Hub Premier 5', 'id0': '197b3e19-3bd0-4d1f-b531-d2c244587d89', 'source': 'starhub'},
        {'id': 'starhubtvplus_226', 'name': 'Hub Premier 6', 'id0': 'e2a12638-8168-44e7-8e2a-6c436186a085', 'source': 'starhub'},
        {'id': 'starhubtvplus_241', 'name': 'FIGHT SPORTS HD', 'id0': 'a258cd7c-b4d2-4e45-b050-1e30a9519ef9', 'source': 'starhub'},
        {'id': 'starhubtvplus_247', 'name': 'Premier Sports', 'id0': '6bdd83c0-d833-42a0-896c-8a94fbb35f73', 'source': 'starhub'},
        {'id': 'starhubtvplus_303', 'name': 'Cbeebies HD', 'id0': '219cc587-57ab-4b55-baf3-03810f46deeb', 'source': 'starhub'},
        {'id': 'starhubtvplus_304', 'name': 'Nick Jr', 'id0': '29d2b788-ae5c-4307-8ac8-dd0c5911ea38', 'source': 'starhub'},
        {'id': 'starhubtvplus_307', 'name': 'DreamWorks Channel HD', 'id0': '824bd5da-016e-4e10-9c8e-2c33fbc179d4', 'source': 'starhub'},
        {'id': 'starhubtvplus_314', 'name': 'Nickelodeon Asia HD', 'id0': 'c873d8db-2f77-4482-8074-b1d477455e91', 'source': 'starhub'},
        {'id': 'starhubtvplus_316', 'name': 'Cartoon Network', 'id0': '753cf54a-a4a2-4723-8709-c8ce14ec8254', 'source': 'starhub'},
        {'id': 'starhubtvplus_401', 'name': 'HISTORY HD', 'id0': 'ded93a12-883b-4ee0-9eaf-d137ebfe2da9', 'source': 'starhub'},
        {'id': 'starhubtvplus_403', 'name': 'Crime + Investigation HD', 'id0': '8a1f4f2d-29a7-4914-9214-40131ecb8d69', 'source': 'starhub'},
        {'id': 'starhubtvplus_407', 'name': 'BBC Earth HD', 'id0': 'f4658135-f4b4-4185-be9a-2ff976b54a8f', 'source': 'starhub'},
        {'id': 'starhubtvplus_422', 'name': 'Discovery HD', 'id0': 'd298c58f-9710-4a8d-b802-d799cb064aff', 'source': 'starhub'},
        {'id': 'starhubtvplus_427', 'name': 'Travelxp HD', 'id0': 'f2c840ad-38ec-46d1-9b7b-b4d534da3c88', 'source': 'starhub'},
        {'id': 'starhubtvplus_432', 'name': 'BBC Lifestyle', 'id0': '047b3a4a-5094-4802-82d4-b3863b6e2cdf', 'source': 'starhub'},
        {'id': 'starhubtvplus_435', 'name': 'AFN', 'id0': '14104a82-aecb-457a-a5c5-2d134c852ba2', 'source': 'starhub'},
        {'id': 'starhubtvplus_437', 'name': 'HGTV', 'id0': 'ca306145-694d-41c8-9f34-c2ce62eb06e9', 'source': 'starhub'},
        {'id': 'starhubtvplus_443', 'name': 'FashionTV HD', 'id0': 'a253b74a-ab9d-4545-9cdd-d81e2d9a056d', 'source': 'starhub'},
        {'id': 'starhubtvplus_447', 'name': 'ABC Australia', 'id0': '64da91df-f088-48ae-9994-99a846e0c1f8', 'source': 'starhub'},
        {'id': 'starhubtvplus_509', 'name': 'ROCK Entertainment', 'id0': 'ca5c1396-7135-426f-baf3-23e9eaef335e', 'source': 'starhub'},
        {'id': 'starhubtvplus_511', 'name': 'AXN HD', 'id0': '89ca2356-f022-4bc6-9ef4-be30d427988f', 'source': 'starhub'},
        {'id': 'starhubtvplus_512', 'name': 'HITS MOVIES HD', 'id0': 'f25d2d07-0303-4c95-be02-e9569d6c4f54', 'source': 'starhub'},
        {'id': 'starhubtvplus_513', 'name': 'HITSNOW', 'id0': '70c3dd0d-ccad-43ca-aed0-0c1234e0052e', 'source': 'starhub'},
        {'id': 'starhubtvplus_514', 'name': 'Lifetime HD', 'id0': '09e8b069-9fce-4a8d-b0cd-2bf77a8a71ba', 'source': 'starhub'},
        {'id': 'starhubtvplus_519', 'name': 'Hits HD', 'id0': 'afde6766-acb5-4c69-b147-dd8b98dea9d2', 'source': 'starhub'},
        {'id': 'starhubtvplus_532', 'name': 'Animax HD', 'id0': '57100d1f-5351-475e-bfef-bd9ae5793684', 'source': 'starhub'},
        {'id': 'starhubtvplus_601', 'name': 'HBO HD', 'id0': 'dea58cb4-eba4-4d53-a1c4-ff8e501e2adf', 'source': 'starhub'},
        {'id': 'starhubtvplus_603', 'name': 'HBO Signature HD', 'id0': '0ef9316c-9b57-42fb-80d2-49297d7a7bac', 'source': 'starhub'},
        {'id': 'starhubtvplus_604', 'name': 'HBO Family HD', 'id0': 'dddf00c0-b347-472d-bc30-d44fd837cde2', 'source': 'starhub'},
        {'id': 'starhubtvplus_605', 'name': 'HBO Hits HD', 'id0': 'd5fa461f-bbfc-4706-9b72-9ea67c946394', 'source': 'starhub'},
        {'id': 'starhubtvplus_611', 'name': 'Cinemax HD', 'id0': '3c85588c-262b-43de-b9c3-0f0fd51466d9', 'source': 'starhub'},
        {'id': 'starhubtvplus_701', 'name': 'BBC World News HD', 'id0': '1312f58d-752b-4d8a-879e-33a43de2d941', 'source': 'starhub'},
        {'id': 'starhubtvplus_702', 'name': 'Fox News Channel', 'id0': 'eb856acf-437e-470f-9161-eabd52e3de02', 'source': 'starhub'},
        {'id': 'starhubtvplus_703', 'name': 'Sky News HD', 'id0': '36453e0d-85cc-4ee7-816c-2e147541cecf', 'source': 'starhub'},
        {'id': 'starhubtvplus_704', 'name': 'Euronews HD', 'id0': 'f948f494-b2bd-4b92-8752-878938966e49', 'source': 'starhub'},
        {'id': 'starhubtvplus_707', 'name': 'CNBC HD', 'id0': '173fc873-1c01-4782-b0ee-f322fe23ef33', 'source': 'starhub'},
        {'id': 'starhubtvplus_708', 'name': 'Bloomberg Television HD', 'id0': 'f946f3d4-96c3-4e0f-924d-edac62433fd2', 'source': 'starhub'},
        {'id': 'starhubtvplus_709', 'name': 'Bloomberg Quicktake', 'id0': 'cbce770a-b029-425b-ac2e-7fb9b8d5510f', 'source': 'starhub'},
        {'id': 'starhubtvplus_711', 'name': 'CNN HD', 'id0': '8339731a-4928-4ff0-bf9d-9202ae59aea7', 'source': 'starhub'},
        {'id': 'starhubtvplus_722', 'name': 'CGTN', 'id0': 'b4554ec6-37d5-4936-943d-229e9df528e8', 'source': 'starhub'},
        {'id': 'starhubtvplus_724', 'name': 'France24', 'id0': '64864046-76a0-4de0-a65b-53fea57ee6bd', 'source': 'starhub'},
        {'id': 'starhubtvplus_801', 'name': 'CCTV-4', 'id0': '04c1e33b-520d-42b7-8d83-dc8650b758c0', 'source': 'starhub'},
        {'id': 'starhubtvplus_805', 'name': 'Phoenix Chinese Channel HD', 'id0': '3d4b11b5-c883-44ae-921b-4d7e07fe852f', 'source': 'starhub'},
        {'id': 'starhubtvplus_806', 'name': 'Phoenix InfoNews Channel HD', 'id0': 'd440ee6e-6f9a-4d78-b37b-5be89051145a', 'source': 'starhub'},
        {'id': 'starhubtvplus_808', 'name': 'TVBS-NEWS', 'id0': 'ea2a19ac-da50-4e86-8083-d8938112641f', 'source': 'starhub'},
        {'id': 'starhubtvplus_811', 'name': 'NHK World Premium HD', 'id0': '3d125b3f-26ea-4f0c-acb5-774b2f478352', 'source': 'starhub'},
        {'id': 'starhubtvplus_812', 'name': 'NHK WORLD - JAPAN', 'id0': '7b781d20-7138-4ffb-bd9d-6b12e473043b', 'source': 'starhub'},
        {'id': 'starhubtvplus_815', 'name': 'KBS World HD', 'id0': '52a80589-3613-4021-bcf6-6abb1c80bff4', 'source': 'starhub'},
        {'id': 'starhubtvplus_817', 'name': 'Arirang TV', 'id0': '4c25cb31-4a19-4d5b-9926-a51a8b289ae5', 'source': 'starhub'},
        {'id': 'starhubtvplus_820', 'name': 'ETTV ASIA HD', 'id0': '39a2d989-f51d-45de-b4e3-90cc58aa54f4', 'source': 'starhub'},
        {'id': 'starhubtvplus_824', 'name': 'tvN HD', 'id0': '9f62a679-b398-434b-b848-ca5f8b1063c9', 'source': 'starhub'},
        {'id': 'starhubtvplus_825', 'name': 'Hub E City HD', 'id0': 'aa5a523d-562b-499b-b04b-1d75fbbc88f5', 'source': 'starhub'},
        {'id': 'starhubtvplus_827', 'name': 'CTI TV HD', 'id0': '0629c0f2-b352-4b01-93aa-f37c91b07866', 'source': 'starhub'},
        {'id': 'starhubtvplus_828', 'name': 'TVBS Asia', 'id0': 'e1b53e0d-f371-4918-8cbd-6e99a4d79c76', 'source': 'starhub'},
        {'id': 'starhubtvplus_832', 'name': 'Dragon TV', 'id0': '69303210-3157-4dd2-b923-809c5ce2371a', 'source': 'starhub'},
        {'id': 'starhubtvplus_838', 'name': 'TVB Jade HD', 'id0': '38251a1a-9368-410c-9dc5-ab806d74420f', 'source': 'starhub'},
        {'id': 'starhubtvplus_852', 'name': 'Hub Ruyi', 'id0': '295f6562-21ae-498f-9971-0f5b76fae79d', 'source': 'starhub'},
        {'id': 'starhubtvplus_855', 'name': 'Hub VVDrama', 'id0': '792aa2b5-cb06-45b9-bf37-e919c27c097e', 'source': 'starhub'},
        {'id': 'starhubtvplus_859', 'name': 'TVB Xing He', 'id0': '8a0cfe88-6627-49e8-8eed-a2f73e609b5d', 'source': 'starhub'},
        {'id': 'starhubtvplus_868', 'name': 'Celestial Movies HD', 'id0': 'b8b921c8-3798-40b7-aab9-cb2eca3a5159', 'source': 'starhub'},
        {'id': 'starhubtvplus_869', 'name': 'CCM', 'id0': 'd2bac03e-7024-48be-83b2-d56cc3852a7c', 'source': 'starhub'},
        {'id': 'starhubtvplus_993', 'name': 'TestChannel 993..', 'id0': 'e2ae3508-e262-4046-abbf-bfbdfc3ef898', 'source': 'starhub'},
        {'id': 'starhubtvplus_996', 'name': 'TestChannel 996', 'id0': '3f4bb488-1eae-4b02-8d13-04931b021e09', 'source': 'starhub'},
        {'id': 'starhubtvplus_997', 'name': 'TestChannel2', 'id0': '12f8f777-7671-486d-a26b-5727cd9a5ff9', 'source': 'starhub'},
        {'id': 'starhubtvplus_998', 'name': 'Test 998', 'id0': '9e1ef59d-d235-497b-93b0-063c2231cae5', 'source': 'starhub'},
        {'id': 'singtel_5002', 'name': 'Ch 5 (HD)', 'id0': '5002', 'source': 'singtel'},
        {'id': 'singtel_5003', 'name': 'Ch 8 (HD)', 'id0': '5003', 'source': 'singtel'},
        {'id': 'singtel_5004', 'name': 'Suria (HD)', 'id0': '5004', 'source': 'singtel'},
        {'id': 'singtel_5005', 'name': 'Vasantham (HD)', 'id0': '5005', 'source': 'singtel'},
        {'id': 'singtel_5006', 'name': 'CNA', 'id0': '5006', 'source': 'singtel'},
        {'id': 'singtel_5007', 'name': 'MediaCorp Ch U', 'id0': '5007', 'source': 'singtel'},
        {'id': 'singtel_5111', 'name': 'mio Sports', 'id0': '5111', 'source': 'singtel'},
        {'id': 'singtel_5112', 'name': 'mio Sports 2', 'id0': '5112', 'source': 'singtel'},
        {'id': 'singtel_5113', 'name': 'mio Sports 3', 'id0': '5113', 'source': 'singtel'},
        {'id': 'singtel_6114', 'name': 'SPOTV (HD)', 'id0': '6114', 'source': 'singtel'},
        {'id': 'singtel_6115', 'name': 'SPOTV 2 (HD)', 'id0': '6115', 'source': 'singtel'},
        {'id': 'singtel_5118', 'name': 'Premier Sports', 'id0': '5118', 'source': 'singtel'},
        {'id': 'singtel_6119', 'name': 'Fight Sports (HD)', 'id0': '6119', 'source': 'singtel'},
        {'id': 'singtel_5120', 'name': 'Pickleball Now', 'id0': '5120', 'source': 'singtel'},
        {'id': 'singtel_6123', 'name': 'Cricbuzz (HD)', 'id0': '6123', 'source': 'singtel'},
        {'id': 'singtel_6124', 'name': 'Cricbuzz 2 (HD)', 'id0': '6124', 'source': 'singtel'},
        {'id': 'singtel_6126', 'name': 'beIN SPORTS (HD)', 'id0': '6126', 'source': 'singtel'},
        {'id': 'singtel_6127', 'name': 'beIN SPORTS 2 (HD)', 'id0': '6127', 'source': 'singtel'},
        {'id': 'singtel_6110', 'name': 'beIN SPORTS 3 (HD)', 'id0': '6110', 'source': 'singtel'},
        {'id': 'singtel_5151', 'name': 'Sky News HD', 'id0': '5151', 'source': 'singtel'},
        {'id': 'singtel_5155', 'name': 'CGTN (HD)', 'id0': '5155', 'source': 'singtel'},
        {'id': 'singtel_5157', 'name': 'NHK World - Japan', 'id0': '5157', 'source': 'singtel'},
        {'id': 'singtel_5041', 'name': 'France 24 (English)', 'id0': '5041', 'source': 'singtel'},
        {'id': 'singtel_5160', 'name': 'Vietnam Today', 'id0': '5160', 'source': 'singtel'},
        {'id': 'singtel_5161', 'name': 'DW (English)', 'id0': '5161', 'source': 'singtel'},
        {'id': 'singtel_5165', 'name': 'FOX News Channel HD', 'id0': '5165', 'source': 'singtel'},
        {'id': 'singtel_6166', 'name': 'BBC News (HD)', 'id0': '6166', 'source': 'singtel'},
        {'id': 'singtel_5167', 'name': 'CNN International', 'id0': '5167', 'source': 'singtel'},
        {'id': 'singtel_5171', 'name': 'Bloomberg TV (HD)', 'id0': '5171', 'source': 'singtel'},
        {'id': 'singtel_5172', 'name': 'Bloomberg Originals', 'id0': '5172', 'source': 'singtel'},
        {'id': 'singtel_5173', 'name': 'CNBC Asia (HD)', 'id0': '5173', 'source': 'singtel'},
        {'id': 'singtel_5202', 'name': 'Discovery Ch (HD)', 'id0': '5202', 'source': 'singtel'},
        {'id': 'singtel_6203', 'name': 'BBC Earth (HD)', 'id0': '6203', 'source': 'singtel'},
        {'id': 'singtel_5206', 'name': 'C+I (HD)', 'id0': '5206', 'source': 'singtel'},
        {'id': 'singtel_5208', 'name': 'Animal Planet (HD)', 'id0': '5208', 'source': 'singtel'},
        {'id': 'singtel_5209', 'name': 'HISTORY (HD)', 'id0': '5209', 'source': 'singtel'},
        {'id': 'singtel_5211', 'name': 'CGTN-Documentary', 'id0': '5211', 'source': 'singtel'},
        {'id': 'singtel_5212', 'name': 'Global Trekker (HD)', 'id0': '5212', 'source': 'singtel'},
        {'id': 'singtel_5215', 'name': 'Love Nature (HD)', 'id0': '5215', 'source': 'singtel'},
        {'id': 'singtel_5226', 'name': 'Cartoon Network (HD)', 'id0': '5226', 'source': 'singtel'},
        {'id': 'singtel_6236', 'name': 'CBeebies (HD)', 'id0': '6236', 'source': 'singtel'},
        {'id': 'singtel_5238', 'name': 'Nick Jr (HD)', 'id0': '5238', 'source': 'singtel'},
        {'id': 'singtel_5240', 'name': 'Nickelodeon Asia HD', 'id0': '5240', 'source': 'singtel'},
        {'id': 'singtel_5250', 'name': 'HGTV (HD)', 'id0': '5250', 'source': 'singtel'},
        {'id': 'singtel_5251', 'name': 'ABC Australia', 'id0': '5251', 'source': 'singtel'},
        {'id': 'singtel_5254', 'name': 'TLC (HD)', 'id0': '5254', 'source': 'singtel'},
        {'id': 'singtel_6255', 'name': 'BBC Lifestyle (HD)', 'id0': '6255', 'source': 'singtel'},
        {'id': 'singtel_5256', 'name': 'AFN (HD)', 'id0': '5256', 'source': 'singtel'},
        {'id': 'singtel_5257', 'name': 'TRACE Sport Stars HD', 'id0': '5257', 'source': 'singtel'},
        {'id': 'singtel_5258', 'name': 'Arirang TV (HD)', 'id0': '5258', 'source': 'singtel'},
        {'id': 'singtel_5260', 'name': 'Makeful (HD)', 'id0': '5260', 'source': 'singtel'},
        {'id': 'singtel_6301', 'name': 'HITS MOVIES (HD)', 'id0': '6301', 'source': 'singtel'},
        {'id': 'singtel_5302', 'name': 'Lifetime (HD)', 'id0': '5302', 'source': 'singtel'},
        {'id': 'singtel_5303', 'name': 'HITS NOW (HD)', 'id0': '5303', 'source': 'singtel'},
        {'id': 'singtel_5304', 'name': 'AXN (HD)', 'id0': '5304', 'source': 'singtel'},
        {'id': 'singtel_5310', 'name': 'ROCK Action (HD)', 'id0': '5310', 'source': 'singtel'},
        {'id': 'singtel_5318', 'name': 'ROCK ENT (HD)', 'id0': '5318', 'source': 'singtel'},
        {'id': 'singtel_5326', 'name': 'HITS (HD)', 'id0': '5326', 'source': 'singtel'},
        {'id': 'singtel_5340', 'name': 'ANIPLUS HD', 'id0': '5340', 'source': 'singtel'},
        {'id': 'singtel_5342', 'name': 'Animax (HD)', 'id0': '5342', 'source': 'singtel'},
        {'id': 'singtel_6420', 'name': 'HBO HD', 'id0': '6420', 'source': 'singtel'},
        {'id': 'singtel_6421', 'name': 'HBO Signature (HD)', 'id0': '6421', 'source': 'singtel'},
        {'id': 'singtel_6422', 'name': 'HBO Family (HD)', 'id0': '6422', 'source': 'singtel'},
        {'id': 'singtel_6423', 'name': 'HBO Hits (HD)', 'id0': '6423', 'source': 'singtel'},
        {'id': 'singtel_6424', 'name': 'CINEMAX (HD)', 'id0': '6424', 'source': 'singtel'},
        {'id': 'singtel_5501', 'name': 'e-Le (HD)', 'id0': '5501', 'source': 'singtel'},
        {'id': 'singtel_5502', 'name': 'Jia Le Channel (HD)', 'id0': '5502', 'source': 'singtel'},
        {'id': 'singtel_5503', 'name': 'Ju Le Cool', 'id0': '5503', 'source': 'singtel'},
        {'id': 'singtel_6507', 'name': 'TVBS Asia', 'id0': '6507', 'source': 'singtel'},
        {'id': 'singtel_5511', 'name': 'TVB Jade (HD)', 'id0': '5511', 'source': 'singtel'},
        {'id': 'singtel_5512', 'name': 'now Jelli (HD)', 'id0': '5512', 'source': 'singtel'},
        {'id': 'singtel_6516', 'name': 'TVBS News', 'id0': '6516', 'source': 'singtel'},
        {'id': 'singtel_5517', 'name': 'TVB Xing He (HD)', 'id0': '5517', 'source': 'singtel'},
        {'id': 'singtel_5518', 'name': 'tvN HD (Mandarin)', 'id0': '5518', 'source': 'singtel'},
        {'id': 'singtel_5521', 'name': 'ETTV Asia (HD)', 'id0': '5521', 'source': 'singtel'},
        {'id': 'singtel_5038', 'name': 'KBS World (HD)', 'id0': '5038', 'source': 'singtel'},
        {'id': 'singtel_5534', 'name': 'CCTV Entertainment', 'id0': '5534', 'source': 'singtel'},
        {'id': 'singtel_5535', 'name': 'Dragon TV Intl', 'id0': '5535', 'source': 'singtel'},
        {'id': 'singtel_5536', 'name': 'Hunan International', 'id0': '5536', 'source': 'singtel'},
        {'id': 'singtel_5537', 'name': 'BRTV International', 'id0': '5537', 'source': 'singtel'},
        {'id': 'singtel_5538', 'name': 'China Movie Channel', 'id0': '5538', 'source': 'singtel'},
        {'id': 'singtel_6547', 'name': 'Phoenix InfoNews', 'id0': '6547', 'source': 'singtel'},
        {'id': 'singtel_5555', 'name': 'CCTV-4 (HD)', 'id0': '5555', 'source': 'singtel'},
        {'id': 'singtel_5557', 'name': 'CTI Asia (HD)', 'id0': '5557', 'source': 'singtel'},
        {'id': 'singtel_5561', 'name': 'ETTV Asia News (HD)', 'id0': '5561', 'source': 'singtel'},
        {'id': 'singtel_6571', 'name': 'CM+', 'id0': '6571', 'source': 'singtel'},
        {'id': 'singtel_5580', 'name': 'CCM', 'id0': '5580', 'source': 'singtel'},
        {'id': 'singtel_5585', 'name': 'Celestial Movies(HD)', 'id0': '5585', 'source': 'singtel'},
        {'id': 'singtel_5602', 'name': 'Astro Prima HD', 'id0': '5602', 'source': 'singtel'},
        {'id': 'singtel_5607', 'name': 'Pesona HD', 'id0': '5607', 'source': 'singtel'},
        {'id': 'singtel_5608', 'name': 'Astro Ria HD', 'id0': '5608', 'source': 'singtel'},
        {'id': 'singtel_5610', 'name': 'Citra Drama (HD)', 'id0': '5610', 'source': 'singtel'},
        {'id': 'singtel_5618', 'name': 'Drama Channel', 'id0': '5618', 'source': 'singtel'},
        {'id': 'singtel_5619', 'name': 'tvN HD', 'id0': '5619', 'source': 'singtel'},
        {'id': 'singtel_5622', 'name': 'Sun TV HD', 'id0': '5622', 'source': 'singtel'},
        {'id': 'singtel_5623', 'name': 'Colors Tamil HD', 'id0': '5623', 'source': 'singtel'},
        {'id': 'singtel_5624', 'name': 'Zee Thirai', 'id0': '5624', 'source': 'singtel'},
        {'id': 'singtel_5625', 'name': 'KTV HD', 'id0': '5625', 'source': 'singtel'},
        {'id': 'singtel_5627', 'name': 'Sun Music HD', 'id0': '5627', 'source': 'singtel'},
        {'id': 'singtel_5628', 'name': 'Adithya TV', 'id0': '5628', 'source': 'singtel'},
        {'id': 'singtel_5630', 'name': 'Sony YAY', 'id0': '5630', 'source': 'singtel'},
        {'id': 'singtel_5632', 'name': 'Zee Tamil HD', 'id0': '5632', 'source': 'singtel'},
        {'id': 'singtel_5634', 'name': 'Vijay TV (HD)', 'id0': '5634', 'source': 'singtel'},
        {'id': 'singtel_5638', 'name': 'Asianet', 'id0': '5638', 'source': 'singtel'},
        {'id': 'singtel_5639', 'name': 'Asianet Movies', 'id0': '5639', 'source': 'singtel'},
        {'id': 'singtel_5644', 'name': 'SET (HINDI)', 'id0': '5644', 'source': 'singtel'},
        {'id': 'singtel_5646', 'name': 'Zee TV', 'id0': '5646', 'source': 'singtel'},
        {'id': 'singtel_5648', 'name': 'SAB TV', 'id0': '5648', 'source': 'singtel'},
        {'id': 'singtel_5652', 'name': 'Colors', 'id0': '5652', 'source': 'singtel'},
        {'id': 'singtel_5654', 'name': 'Star Bharat', 'id0': '5654', 'source': 'singtel'},
        {'id': 'singtel_5656', 'name': 'STAR Plus', 'id0': '5656', 'source': 'singtel'},
        {'id': 'singtel_5658', 'name': 'MTV India', 'id0': '5658', 'source': 'singtel'},
        {'id': 'singtel_5662', 'name': 'STAR Gold', 'id0': '5662', 'source': 'singtel'},
        {'id': 'singtel_5668', 'name': 'Sony MAX', 'id0': '5668', 'source': 'singtel'},
        {'id': 'singtel_5670', 'name': 'maa movies', 'id0': '5670', 'source': 'singtel'},
        {'id': 'singtel_5671', 'name': 'Star Maa', 'id0': '5671', 'source': 'singtel'},
        {'id': 'singtel_5676', 'name': 'Times Now', 'id0': '5676', 'source': 'singtel'},
        {'id': 'singtel_5677', 'name': 'Zoom TV', 'id0': '5677', 'source': 'singtel'},
        {'id': 'singtel_5680', 'name': 'WION', 'id0': '5680', 'source': 'singtel'},
        {'id': 'singtel_5682', 'name': 'NHK World Premium HD', 'id0': '5682', 'source': 'singtel'},
        {'id': 'singtel_5040', 'name': 'France 24 (French)', 'id0': '5040', 'source': 'singtel'},
        {'id': 'singtel_5056', 'name': 'GMA Pinoy TV', 'id0': '5056', 'source': 'singtel'},
        {'id': 'singtel_5689', 'name': 'GMA Life TV', 'id0': '5689', 'source': 'singtel'},
        {'id': 'singtel_5690', 'name': 'GMA News TV Intl', 'id0': '5690', 'source': 'singtel'},
        {'id': 'singtel_6692', 'name': 'Cinema One Global', 'id0': '6692', 'source': 'singtel'},
        {'id': 'singtel_5693', 'name': 'The Filipino Ch (HD)', 'id0': '5693', 'source': 'singtel'},
        {'id': 'singtel_6694', 'name': 'ABS-CBN News Channel', 'id0': '6694', 'source': 'singtel'},
        {'id': 'epgpw_6580', 'name': 'RT News', 'id0': '6580', 'source': 'epg.pw'},
        {'id': 'epgpw_6856', 'name': 'TVP World', 'id0': '6856', 'source': 'epg.pw'},
        {'id': 'epgpw_7374', 'name': 'RT Д English', 'id0': '7374', 'source': 'epg.pw'},
        {'id': 'nhk_g', 'name': 'NHK総合', 'id0': 'g1', 'source': 'nhk'},
        {'id': 'nhk_bsp4k', 'name': 'NHK BSP4K', 'id0': 's5', 'source': 'nhk'},
        {'id': 'nhk_bs8k', 'name': 'NHK BS8K', 'id0': 's6', 'source': 'nhk'},
        {'id': 'epgpw_12162', 'name': 'BBC NEWS HD', 'id0': '12162', 'source': 'epg.pw'},
        {'id': 'epgpw_12523', 'name': 'TRT World HD', 'id0': '12523', 'source': 'epg.pw'},
        {'id': 'epgpw_76619', 'name': 'Eurosport 1', 'id0': '76619', 'source': 'epg.pw'},
        {'id': 'epgpw_767447', 'name': 'Eurosport 2', 'id0': '6744', 'source': 'epg.pw'},
        {'id': 'epgpw_400477', 'name': 'TNT Sports 1 HD', 'id0': '400477', 'source': 'epg.pw'},
        {'id': 'epgpw_400478', 'name': 'TNT Sports 4 HD', 'id0': '400478', 'source': 'epg.pw'},
        {'id': 'epgpw_400479', 'name': 'TNT Sports 3 HD', 'id0': '400479', 'source': 'epg.pw'},
        {'id': 'epgpw_400480', 'name': 'TNT Sports 2 HD', 'id0': '400480', 'source': 'epg.pw'},
        {'id': 'epgpw_464835', 'name': 'CSPAN', 'id0': '464835', 'source': 'epg.pw'},
        {'id': 'epgpw_464889', 'name': 'MS NOW HD', 'id0': '464889', 'source': 'epg.pw'},
        {'id': 'epgpw_464920', 'name': 'i24 News English', 'id0': '464920', 'source': 'epg.pw'},
        {'id': 'epgpw_464941', 'name': 'CBS News National Stream', 'id0': '464941', 'source': 'epg.pw'},
        {'id': 'epgpw_465150', 'name': 'ABC News Live', 'id0': '465150', 'source': 'epg.pw'},
        {'id': 'epgpw_465243', 'name': 'CSPAN2', 'id0': '465243', 'source': 'epg.pw'},
        {'id': 'epgpw_486317', 'name': 'NBC News NOW', 'id0': '486317', 'source': 'epg.pw'},
        {'id': 'epgpw_543088', 'name': 'DD INDIA', 'id0': '543088', 'source': 'epg.pw'},
        {'id': 'epgpw_543155', 'name': 'WION', 'id0': '543155', 'source': 'epg.pw'}
    ]
    asyncio.run(gen_xml(channels, 'epg0.xml'))
