# -*- coding:utf-8 -*-
import asyncio
import httpx
import datetime
import re
import os
from bs4 import BeautifulSoup as bs


async def get_epgs_tbc(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'https://www.tbc.net.tw/EPG/Channel?channelId=%s' % channel_id0
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=30)
        res.encoding = 'utf-8'
        soup = bs(res.text, 'html.parser')
        uls = soup.select('ul.list_program2')
        for ul in uls:
            # n1 = 0  # 记录当天的节目数
            lis = ul.select('li')
            for li in lis:
                try:
                    title = li.attrs['title']
                except:
                    title = li.attrs['data.name']
                desc = li.attrs['desc']
                date_ = li.attrs['date']
                time_delay = li.attrs['time'].strip()
                time_delay_re = re.search(r'(\d+:\d+)~(\d+:\d+)', time_delay)
                if time_delay_re:  # 有节目信息则解析
                    start_str, end_str = time_delay_re.group(1), time_delay_re.group(2)  # 将开始与结束时间的文本分开
                    starttime = datetime.datetime.strptime(date_ + start_str, '%Y/%m/%d%H:%M')
                    endtime = datetime.datetime.strptime(date_ + end_str, '%Y/%m/%d%H:%M')
                    if starttime > endtime:
                        endtime = endtime + datetime.timedelta(days=1)
                    # if starttime.date() < dt:
                    #     continue
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': endtime,
                    'title': title,
                    'desc': desc
                }
                if epg not in epgs:
                    epgs.append(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0,
    }
    return ret


# 下载TBC所有频道ID及名称
async def get_channels_tbc():
    channels = []
    cookies = {
        'ASP.NET_SessionId': 'v111fiox1mzc0wpc0d4iue5c'
    }
    url = 'https://www.tbc.net.tw/EPG'
    async with httpx.AsyncClient() as client:
        res = await client.get(url=url, cookies=cookies, timeout=6)
    res.encoding = 'utf-8'
    soup = bs(res.text, 'html.parser')
    lis = soup.select('ul.list_tv > li')
    for li in lis:
        name = li['title']
        id = li['id']
        # img = li.select('img')[0]['src']
        # url = li.a['href']
        channel = {
            'id': 'tbc_' + id,
            'name': name,
            'id0': id,
            'source': 'tbc',
        }
        print(channel)
        channels.append(channel)
    return channels


# asyncio.run(get_channels_tbc())
# get_epgs_tbc({'name': '寰宇新聞台灣台', 'id': '227', 'source': 'tbc'})
