# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import asyncio
import json


async def get_epgs_suntv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get('https://www.chinasuntv.com/api/v1/chinasun/programlist')
        res.encoding = 'utf-8'
        programlist = json.loads(res.text)['payload']
        endtime = datetime.datetime.strptime(programlist[-1]['PlayTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
        for program in programlist[-2::-1]:
            title = program['prgName']
            starttime = datetime.datetime.strptime(program['PlayTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(hours=8)
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
        # print(msg)
    ret = {
        'success': success,
        'epgs': epgs[::-1],
        'msg': msg,
        'ban': 0,
    }
    return ret

# asyncio.run(get_epgs_suntv({'id': 'chinasuntv', 'name': '陽光衛視', 'id0': 'chinasuntv', 'source': 'suntv'}))