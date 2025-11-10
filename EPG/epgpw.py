# -*- coding:utf-8 -*-
import httpx
import datetime
import os


async def get_epgs_epgpw(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = f'https://epg.pw/api/epg.json?channel_id={channel_id0}&timezone=QXNpYS9UYWlwZWk='
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        epg_list = res.json()['epg_list']
        starttime = datetime.datetime.strptime(epg_list[-1]['start_date'][:10], '%Y-%m-%d') + datetime.timedelta(days=1)
        for i in epg_list[::-1]:
            title = i['title']
            desc = i['desc'] if i['desc'] != None else ''
            endtime = starttime
            starttime = datetime.datetime.strptime(i['start_date'][:19], '%Y-%m-%dT%H:%M:%S')
            epg = {
                'channel_id': channel_id,
                'starttime': starttime,
                'endtime': endtime,
                'title': title,
                'desc': desc
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

# await get_epgs_epgpw({'id': 'tvb_CCCM', 'name': '天映經典頻道', 'id0': '368371', 'source': 'epg.pw'})
