# -*- coding:utf-8 -*-
import httpx
import datetime
import os
import re
from bs4 import BeautifulSoup
import asyncio


async def get_epgs_mod(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            res = await client.get('https://modp.cht.com.tw/modinfo/epginfob.php', params={'w': 0, 'id': channel_id0}, timeout=10)
        res.raise_for_status()
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        epgs = []
        current_date = None
        for epgday in soup.find_all('div', class_='epgdays'):
            for item in epgday.find_all('div', class_='item', recursive=False):
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', item.get_text(' ', strip=True))
                if date_match:
                    current_date = datetime.date.fromisoformat(date_match.group(1))
                if current_date is None:
                    continue

                for row in item.find_all("div", class_=["past", "now", "future"]):
                    time_node = row.select_one('div.time')
                    title_node = row.select_one('div.channelTitle')
                    time_match = re.search(r'(\d{1,2}):(\d{2})', time_node.get_text(strip=True))

                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))
                    starttime = datetime.datetime(
                        current_date.year,
                        current_date.month,
                        current_date.day,
                        hour,
                        minute,
                    )
                    epg = {
                        'channel_id': channel_id,
                        'starttime': starttime,
                        'endtime': None,
                        'title': title_node.get_text(strip=True),
                        'desc': '',
                        'program_date': current_date
                    }
                    epgs.append(epg)
                    # print(epg)

        for index, epg in enumerate(epgs):
            if index + 1 < len(epgs) and epgs[index + 1]['starttime'] > epg['starttime']:
                epg['endtime'] = epgs[index + 1]['starttime']
            else:
                next_midnight = datetime.datetime.combine(
                    epg['program_date'] + datetime.timedelta(days=1),
                    datetime.time.min,
                )
                epg['endtime'] = next_midnight if next_midnight > epg['starttime'] else epg['starttime'] + datetime.timedelta(minutes=30)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban':0,
    }
    return ret


async def get_channels_mod():
    # http://mod.cht.com.tw/tv/channel.php?id=006   采集节目表地址
    url = 'https://modweb2.chtmod.tv/bepg2/'
    async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
    res.raise_for_status()
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

if __name__ == '__main__':
    # print(get_epgs_mod({'name': '006 民視', 'id': '006', 'source': 'mod'}, datetime.datetime.now().date()))
    asyncio.run(get_channels_mod())
