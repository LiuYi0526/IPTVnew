# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import asyncio
from bs4 import BeautifulSoup
import json


async def get_epgs_ntdtv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get('https://www.ntdtv.com/b5/program-schedule')
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        data_schedules = soup.find('div', class_="json-data")['data-schedules']
        data_schedules = json.loads(data_schedules)
        items = []
        for channel in data_schedules:
            if channel == channel_id0:
                for date in data_schedules[channel]:
                    for item in data_schedules[channel][date]:
                        items.append(item)
        enddate = datetime.datetime.fromtimestamp(item['time_start']).date()
        endtime = datetime.datetime(enddate.year, enddate.month, enddate.day, 13, 0)
        for item in items[::-1]:
            title = item['title']
            starttime = datetime.datetime.fromtimestamp(item['time_start'])
            epg = {'channel_id': channel_id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': '',
                   }
            endtime = starttime
            epgs.append(epg)
            # print(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs[::-1],
        'msg': msg,
        'ban': 0,
    }
    return ret

# asyncio.run(get_epgs_ntdtv({'id': 'ntd_china', 'name': '新唐人中國台', 'id0': 'ntd_china', 'source': 'ntdtv'}))
