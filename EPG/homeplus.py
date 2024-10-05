# -*- coding:utf-8 -*-
import httpx
import datetime
import re
import os


async def get_epgs_homeplus(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    url = 'https://www.homeplus.net.tw/cable/Product_introduce/digital_tv/get_channel_content'
    payload = f"so=210&channelid={channel_id0}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url=url, headers=headers, data=payload, timeout=10)
        date_program = res.json()['date_program']
        for date in date_program:
            for i in date_program[date]:
                for j in i:
                    try:
                        name = j['name']
                    except:
                        j = i[j]
                        name = j['name']
                    description = j['description']
                    beginTime = datetime.datetime.strptime(date + j['beginTime'], '%Y-%m-%d%H:%M')
                    endTime = datetime.datetime.strptime(date + j['endTime'], '%Y-%m-%d%H:%M')
                    if beginTime > endTime:
                        beginTime = beginTime - datetime.timedelta(days=1)
                    epg = {'channel_id': channel_id,
                           'starttime': beginTime,
                           'endtime': endTime,
                           'title': name,
                           'desc': description
                           }
                    print(epg)
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


# 下载TBC所有频道ID及名称
async def get_channels_homeplus():
    channels = []
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    url = 'https://www.homeplus.net.tw/cable/Product_introduce/digital_tv/getCategoryAndContent'
    for i in range(7):
        payload = f"so=210&page={i}&category=all"
        async with httpx.AsyncClient() as client:
            res = await client.post(url=url, headers=headers, data=payload, timeout=10)
        for channel_list in res.json()['channel']['channel']:
            for ch in channel_list:
                id = ch['channelid']
                name = ch['name']
                channel = {
                    'id': 'homeplus_' + id,
                    'name': name,
                    'id0': id,
                    'source': 'homeplus',
                }
                print(channel)
                channels.append(channel)
    return channels


# await get_channels_homeplus()
# await get_epgs_homeplus({'id': 'homeplus_13', 'name': '公共電視台', 'id0': '13', 'source': 'homeplus'})
