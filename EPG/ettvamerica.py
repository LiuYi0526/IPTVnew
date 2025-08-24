# -*- coding:utf-8 -*-
import datetime
import os
import httpx
from bs4 import BeautifulSoup
import asyncio
import pytz

pst = pytz.timezone('America/Los_Angeles')  # PST (UTC-8)
bjt = pytz.timezone('Asia/Shanghai')        # BJT (UTC+8)

async def get_epgs_ettvamerica(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    provider, channel_id0 = channel['id0'].split('-')
    try:
        for hour in range(0, 24, 3):
            channel_id = channel['id']
            url = f'https://www.ettvamerica.com/Schedule/ScheduleList.cshtml?Region=1&Provider={provider}&Y={dt.year}&M={dt.month}&D={dt.day}&H={hour}'
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            channel_list = res.text.split('; grid-column: 1; text-align: center;">')
            for ch in channel_list:
                if channel_id0 in ch:
                    epg_text = ch
            soup = BeautifulSoup(epg_text, 'html.parser')
            for item in soup.find_all('div', class_='ScheduleDiv'):
                span = item.select('span')
                title = span[0].text
                date = span[1].text.split(' ~ ')
                starttime0 = datetime.datetime.strptime(date[0], "%I:%M %p")
                starttime = pst.localize(datetime.datetime(dt.year, dt.month, dt.day, starttime0.hour, starttime0.minute)).astimezone(bjt)
                endtime0 = datetime.datetime.strptime(date[1], "%I:%M %p")
                if endtime0 > starttime0:
                    endtime = pst.localize(datetime.datetime(dt.year, dt.month, dt.day, endtime0.hour, endtime0.minute)).astimezone(bjt)
                else:
                    endtime = pst.localize(datetime.datetime(dt.year, dt.month, dt.day+1, endtime0.hour, endtime0.minute)).astimezone(bjt)
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': endtime,
                    'title': title,
                    'desc': ''
                }
                epgs.append(epg)
                # print(epg)
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


# asyncio.run(get_epgs_ettvamerica({'name': '東森中國台', 'id': 'ETTVAmerica_China', 'id0': '1-中國台', 'source': 'ETTVAmerica'}, datetime.datetime.now().date()))
# asyncio.run(get_epgs_ettvamerica({'name': '東森美東衛視台', 'id': 'ETTVAmerica_East', 'id0': '20-美東衛視台', 'source': 'ETTVAmerica'}, datetime.datetime.now().date()))
