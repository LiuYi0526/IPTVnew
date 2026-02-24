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

async def get_epgs_hnntv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f'https://www.hnntv.cn/api/schedule/byDay?channelId={channel_id0}')
        res.encoding = 'utf-8'
        resultSet = res.json()['resultSet']
        for result in resultSet:
            for schedule in result["schedules"]:
                title = schedule['showName']
                starttime = datetime.datetime.strptime(schedule['startDatetime'], '%Y-%m-%d %H:%M:%S')
                endtime = datetime.datetime.strptime(schedule['endDatetime'], '%Y-%m-%d %H:%M:%S')
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

# asyncio.run(get_epgs_hnntv({'id': 'hnntv_13', 'name': '海南卫视', 'id0': '13', 'source': 'hnntv'}))
