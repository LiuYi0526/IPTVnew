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

async def get_epgs_hntv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    dt_ts = int(datetime.datetime.combine(dt, datetime.datetime.min.time()).timestamp())
    try:
        ts = int(time.time())
        sign = hashlib.sha256(f'6ca114a836ac7d73{ts}'.encode()).hexdigest()
        headers = {
            'tenant_id': '1',
            'timestamp': str(ts),
            'sign': sign,
            'User-Agent': 'okhttp/3.12.0'
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(f'https://pubmod.hntv.tv/program/getAuth/vod/originStream/program/{channel_id0}/{dt_ts}', headers=headers)
        res.encoding = 'utf-8'
        programs = res.json()['programs']
        for program in programs:
            title = program['title']
            starttime = datetime.datetime.fromtimestamp(int(program['beginTime']))
            endtime = datetime.datetime.fromtimestamp(int(program['endTime']))
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
        'epgs': epgs,
        'msg': msg,
        'ban': 0,
    }
    return ret

# asyncio.run(get_epgs_hntv({'id': 'hntv_145', 'name': '河南卫视', 'id0': '145', 'source': 'hntv'}, datetime.datetime.now().date()))
