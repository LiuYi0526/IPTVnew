#-*- coding:utf-8 -*-
#广西网络广播电视台-官网来源,2023-06-05添加到数据库，广西卫视及地方6个频道

#POST请求数据
# channelName: 广西卫视
# dateStr: 2023-06-05
# programName:
# deptId: 0a509685ba1a11e884e55cf3fc49331c
# platformId: bd7d620a502d43c09b35469b3cd8c211
#deptid及PLATFORMID为固定值，来源  https://www.gxtv.cn/static/httpRequestOfParams.js  webDeptId = "0a509685ba1a11e884e55cf3fc49331c"  webType = "bd7d620a502d43c09b35469b3cd8c211";

import httpx
import datetime
import os
from bs4 import BeautifulSoup
import asyncio

async def get_epgs_gxntv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    dt_str = dt.strftime('%Y-%m-%d')
    data = {
        'channelName':channel_id0 ,
        'dateStr': dt_str,
        'programName': '',
        'deptId': '0a509685ba1a11e884e55cf3fc49331c',
        'platformId': 'bd7d620a502d43c09b35469b3cd8c211'
    }
    try:
        url = 'https://api2019.gxtv.cn/memberApi/programList/selectListByChannelId'
        async with httpx.AsyncClient() as client:
            res = await client.post(url, data=data)
        res.encoding = 'utf-8'
        res_json = res.json()
        epgs_contents = res_json['data']
        epgs = []
        for epga in epgs_contents:
            starttime_str = epga['programTime']
            time_delay = epga['programmeLength']
            starttime = datetime.datetime.strptime(starttime_str, '%Y-%m-%d %H:%M:%S')
            endtime = starttime + datetime.timedelta(seconds=time_delay)
            title = epga['programName'].strip()
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

async def get_channels_gxntv():
    url = 'https://program.gxtv.cn/'
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    contents = soup.select('#TV_tab > ul > li')
    channels = []
    for content in contents:
        id = content.attrs['id']
        name = content.text
        channel = {
            'id': f'gxntv_{id}',
            'name': name,
            'id0': id,
            'source': 'gxntv'
        }
        channels.append(channel)
        print(channel)
    return channels

# asyncio.run(get_channels_gxntv())
# asyncio.run(get_epgs_gxntv({'id': 'gxntv_广西卫视', 'name': '广西卫视', 'id0': '广西卫视', 'source': 'gxntv'}, datetime.datetime.now().date()))
