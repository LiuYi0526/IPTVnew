# -*- coding:utf-8 -*-
# 齐鲁网-官网来源,2023-08-07添加到数据库，只有山东地区12个频道
import httpx, datetime, os, re, time, json, asyncio


async def get_epgs_iqilu(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    dt_str = dt.strftime('%Y-%m-%d')
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0" 
    }
    url = f'http://sdxw.iqilu.com/v1/app/play/program/qilu?channelID={channel_id0}&date={dt_str}'
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res.encoding = 'utf-8'
        re_json = json.loads(res.text)
        contents = re_json['data']['infos']
        for content in contents:
            starttime = datetime.datetime.fromtimestamp(int(content['begintime']))
            endtime = datetime.datetime.fromtimestamp(int(content['endtime']))
            title = content['name'].strip()
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
        msg = 'spider-%s-%s' % (spidername, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


# asyncio.run(get_epgs_iqilu({'id': 'iqilu_24', 'name': '山东卫视', 'id0': '24', 'source': 'iqilu'}, datetime.datetime.now().date()))
