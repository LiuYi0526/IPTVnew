# -*- coding:utf-8 -*-
import datetime
import os
import httpx

async def get_epgs_jxgdw(channel, dt):  # channel_id,dt ，每次获取当天开始共7天数据
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    starttime = datetime.datetime(dt.year, dt.month, dt.day, 0, 0) + datetime.timedelta(days=2)
    try:
        for i in range(1, -6, -1):
            date = dt + datetime.timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            channel_id = channel['id']
            url = 'https://app.jxgdw.com/api/tv/channel/%s/menus?playDate=%s' % (channel_id0, date_str)
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10)
            res.encoding = 'utf-8'
            res_j = res.json()
            items = res_j['result']
            for item in items[::-1]:
                title = item['programName']
                endtime = starttime
                starttime = datetime.datetime.strptime(item['playTime'], '%Y-%m-%d %H:%M:%S')
                epg = {'channel_id': channel_id,
                       'starttime': starttime,
                       'endtime': endtime,
                       'title': title,
                       'desc': '',
                       'program_date': date,
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
        'ban': 0,
    }
    return ret


async def get_channels_jxgdw():
    url = 'https://app.jxgdw.com/api/tv/channel/page?pageSize=100'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    res_channels = res.json()['result']['list']
    channels = []
    for li in res_channels:
        name = li['channelName']
        id = li['id']
        channel = {
            'name': name,
            'id': str(id),
            'source': 'jxgdw',
        }
        # print(channel)
        channels.append(channel)
    return channels


# get_channels_jxgdw()
# await get_epgs_jxgdw({'name': '都市频道', 'id': '86', 'source': 'jxgdw'}, datetime.datetime.now().date())
