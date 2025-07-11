# -*- coding:utf-8 -*-
import os
import httpx
import datetime
import asyncio


async def get_epgs_cctvplus(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get('https://secure.cctvplus.com/livenotice/getNotice.do?&pageSize=10&pageNo=1&Time=0&Live_Status=All')
        res.encoding = 'utf-8'
        items = res.json()
        for item in items:
            if item['CHANNEL'] == channel_id0:
                title = item['TITLE']
                desc = item['REMARKS']
                starttime = datetime.datetime.strptime(item['dateTime1'], '%Y-%m-%d %H:%M')
                endtime = datetime.datetime.strptime(item['dateTime2'], '%Y-%m-%d %H:%M')
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': endtime,
                    'title': title,
                    'desc': desc,
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

# asyncio.run(get_epgs_cctvplus({'id': 'cctvplus_channel2', 'name': 'CCTV+ Channel 2', 'id0': 'channel2', 'source': 'cctvplus'}))
