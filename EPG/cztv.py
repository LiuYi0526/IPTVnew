# -*- coding:utf-8 -*-
import os
import httpx
import datetime
import asyncio
import hmac
import base64
import time
import hashlib
import json

async def get_epgs_cztv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    starttime = datetime.datetime(dt.year, dt.month, dt.day, 0, 0) + datetime.timedelta(days=1)
    dt = dt.strftime('%Y%m%d')
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"https://p.cztv.com/api/paas/program/{channel_id0}/{dt}")
        res.encoding = 'utf-8'
        items = res.json()["content"]["list"][0]["list"]
        for item in items[::-1]:
            title = item['program_title']
            endtime=starttime
            starttime = datetime.datetime.fromtimestamp(int(item['play_time']) / 1000)
            epg = {
                'channel_id': channel_id,
                'starttime': starttime,
                'endtime': endtime,
                'title': title,
                'desc': '',
            }
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

# asyncio.run(get_epgs_cztv({'id': 'cztv_101', 'name': '浙江卫视', 'id0': '101', 'source': 'cztv'}, datetime.datetime.now().date()))
