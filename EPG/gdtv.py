#-*- coding:utf-8 -*-
#广东广播电视台-官网来源,2021-12-16添加到数据库，只有广东地区频道共10多个
import httpx
import datetime
import os
import xml.etree.ElementTree as ET
import asyncio
import html

async def get_epgs_gdtv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f'http://epg.gdtv.cn/f/{channel_id0}/{need_date}.xml')
        res.encoding = 'utf-8'
        root = ET.fromstring(res.text)
        epgs_contents = root.findall('.//content')
        epgs = []
        for epga in epgs_contents:
            starttime = datetime.datetime.fromtimestamp(int(epga.get('time1')))
            endtime = datetime.datetime.fromtimestamp(int(epga.get('time2')))
            title = html.unescape(epga.text.strip())
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
        'ban':0,
    }
    return ret

async def get_channels_gdtv():
    async with httpx.AsyncClient() as client:
        res = await client.get('http://epg.gdtv.cn/f/1.xml')
    res.encoding = 'utf-8'
    root = ET.fromstring(res.text)
    contents = root.findall('.//channel')
    channels = []
    for content in contents:
        id = content.get('id')
        name = content.find('ctitle').text
        channel = {
            'id': f'gdtv_{id}',
            'name': name,
            'id0': id,
            'source': 'gdtv'
        }
        channels.append(channel)
        print(channel)
    return channels


# asyncio.run(get_channels_gdtv())
# asyncio.run(get_epgs_gdtv({'id': 'gdtv_3', 'name': '广东体育', 'id0': '3', 'source': 'gdtv'}, datetime.datetime.now().date()))
