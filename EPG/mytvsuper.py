# -*- coding:utf-8 -*-
import httpx
import datetime
import os
import asyncio

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    ' AppleWebKit/537.36 (KHTML, like Gecko)'
    ' Chrome/99.0.4844.82 Safari/537.36'
}


async def get_epgs_mytvsuper(channel, dt):  # channel_id, dt ，每次获取当天开始共7天数据
    epgs = []
    msg = ''
    success = 1
    start_date_str = dt.strftime('%Y%m%d')
    end_date = dt + datetime.timedelta(days=7)
    end_date_str = end_date.strftime('%Y%m%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'https://content-api.mytvsuper.com/v1/epg?network_code=%s&from=%s&to=%s&platform=web ' % (
        channel_id0, start_date_str, end_date_str)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=8, headers=headers)
        res.encoding = 'utf-8'
        res_j = res.json()
        items = res_j[0]['item']
        for item in items:
            epg_list = item['epg']
            firtst_line_date = 1
            for li in epg_list:
                starttime = datetime.datetime.strptime(li['start_datetime'], '%Y-%m-%d %H:%M:%S')
                title = li['programme_title_tc']
                title_en = li['programme_title_en']
                desc = li['episode_synopsis_tc']
                desc_en = li['episode_synopsis_en']
                url = 'https://www.mytvsuper.com/tc/programme/%s' % li['programme_path']
                program_date = starttime.date() if 'starttime' in locals() else dt
                if firtst_line_date:
                    last_program_date = starttime
                    first_line_date = 0
                # print(title,starttime,title_en)
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': None,
                    'title': title,
                    'desc': desc,
                    'program_date': program_date,
                }
                # print(epg)
                epgs.append(epg)
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


async def get_channels_mytvsuper():
    url = 'https://content-api.mytvsuper.com/v1/channel/list?platform=web'
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
    res_channels = res.json()['channels']
    channels = []
    for li in res_channels:
        name = li['name_tc']
        # name_en = li['name_en']
        cn = li['channel_no']
        # href = 'https://www.mytvsuper.com/tc/epg/%s/'%cn
        # logo = li['path'] if 'path' in li else ''
        id = li['network_code']
        # desc = ''
        channel = {
            'id': 'tvb_' + id,
            'name': name,
            'id0': id,
            'source': 'mytvsuper',
        }
        print(channel)
        channels.append(channel)
    return channels

# asyncio.run(get_channels_mytvsuper())
# asyncio.run(get_epgs_mytvsuper({'name': '亞洲劇台', 'name_en': 'Asian Drama', 'id0': 'CTVS', 'id': 'CTVS', 'source': 'mytvsuper'}, datetime.datetime.now().date()))
