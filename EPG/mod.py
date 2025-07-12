# -*- coding:utf-8 -*-
import httpx
import datetime
import os
from bs4 import BeautifulSoup
import asyncio


async def get_epgs_mod(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    days = (dt - datetime.datetime.now().date()).days
    url = 'https://modweb2.chtmod.tv/tv/channel.php?id=%s&d=%s' % (
        channel_id0, days)  # d=0表示当天，至少能获取最近七天数据  http://mod.cht.com.tw/tv/channel.php?id=6&d=2
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        lis = soup.select('ul.striped-time-table > li')
        starttime = datetime.datetime(dt.year, dt.month, dt.day, 0, 0) + datetime.timedelta(days=1)
        timestr0 = 2400
        for li in lis[::-1]:
            title = li.select('h4')[0].text.replace('\t', '').replace('\r', '').replace('\n', '').strip()
            endtime = starttime
            timestr = li.select('time.time')[0].text.strip().replace(':', '')
            if int(timestr) < int(timestr0):
                starttime = datetime.datetime(dt.year, dt.month, dt.day, int(timestr[:2]), int(timestr[-2:]))
            else:
                starttime = datetime.datetime(dt.year, dt.month, dt.day, int(timestr[:2]), int(timestr[-2:])) - datetime.timedelta(days=1)
            timestr0 = timestr
            epg = {'channel_id': channel_id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': '',
                   'program_date': dt,
                   }
            epgs.append(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs[::-1],
        'msg': msg,
        'ban':0,
    }
    return ret


async def get_channels_mod():
    # http://mod.cht.com.tw/tv/channel.php?id=006   采集节目表地址
    url = 'https://modweb2.chtmod.tv/bepg2/'
    async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.select('div.rowat')
    divs2 = soup.select('div.rowat_gray')
    divs += divs2
    channels = []
    for div in divs:
        try:
            # urlid = div.select('div > a')[0].attrs['href']
            name = div.select('div.channel_info')[0].text
            id = name[:3].strip()
            # img = 'http://mod.cht.com.tw' + \
            #     re.sub('\?rand=\d*', '', div.select('img')
            #            [0].attrs['src']).strip()
            channel = {
                'id': 'mod_' + id,
                'name': name,
                'id0': id,
                'source': 'mod',
            }
            print(channel)
            channels.append(channel)
        except Exception as e:
            print(div)
    return channels

# print(get_epgs_mod({'name': '006 民視', 'id': '006', 'source': 'mod'}, datetime.datetime.now().date()))
# asyncio.run(get_channels_mod())