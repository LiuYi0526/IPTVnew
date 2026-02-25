# -*- coding:utf-8 -*-
import httpx
import datetime
import os
import time
import asyncio
import hashlib
import ctypes


def transform_timestamp(timestamp: int) -> int:
    parts = [
        255 & timestamp,
        (timestamp & 65280) >> 8,
        (timestamp & 16711680) >> 16,
        (timestamp & 4278190080) >> 24,
    ]
    for i in range(len(parts)):
        parts[i] = ((240 & parts[i]) ^ 240) | ((1 + (parts[i] & 15)) & 15)
    res = (
        parts[3] |
        (parts[2] << 8) |
        (parts[1] << 16) |
        (parts[0] << 24)
    )
    return ctypes.c_int32(res).value


async def get_jstv_accessToken():
    APP_ID = '3b93c452b851431c8b3a076789ab1e14'
    SECRET = '9dd4b0400f6e4d558f2b3497d734c2b4'
    UUID = 'D5COmve6IQgwXvsJ4E3uxBstqxtDSCYW'
    tm = int(time.time())
    signStr = f'{SECRET}/JwtAuth/GetWebToken?AppID={APP_ID}appId{APP_ID}platform41uuid{UUID}{tm}'
    sign = hashlib.md5(signStr.encode('utf-8')).hexdigest()
    tt = transform_timestamp(tm)
    postData = {
        "platform": 41,
        "uuid": UUID,
        "appId": APP_ID,
    }
    headers = {'Content-Type': 'application/json', 'Referer': 'https://live.jstv.com/'}
    url = f"https://api-auth-lizhi.jstv.com/JwtAuth/GetWebToken?AppID={APP_ID}&TT={tt}&Sign={sign}"
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=postData)
    res.encoding = 'utf-8'
    accessToken = res.json()['data']['accessToken']
    return accessToken


async def get_epgs_jstv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    headers = {'Content-Type': 'application/json', 'Referer': 'https://live.jstv.com/'}
    try:
        accessToken = await get_jstv_accessToken()
        headers['Authorization'] = f"Bearer {accessToken}"
        async with httpx.AsyncClient() as client:
            res = await client.get(f'https://live-lizhi.jstv.com/api/Channel/Epg?channelId={channel_id0}&days=6&isNeedTomorrow=1', headers=headers)
        data_epg = res.json()["data"]['epg']
        for data in data_epg:
            for i in data["data"]:
                starttime = datetime.datetime.strptime(i['startTime'], "%Y-%m-%d %H:%M:%S")
                endtime = datetime.datetime.strptime(i['endTime'], "%Y-%m-%d %H:%M:%S")
                title = i['programName'].strip()
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
        'ban': 0,
    }
    return ret


async def get_channels_jstv():
    channels = []
    accessToken = await get_jstv_accessToken()
    headers = {'Content-Type': 'application/json', 'Referer': 'https://live.jstv.com/'}
    accessToken = await get_jstv_accessToken()
    headers['Authorization'] = f"Bearer {accessToken}"
    async with httpx.AsyncClient() as client:
        res = await client.get('https://publish-lizhi.jstv.com/nav/8385', headers=headers)
    res.encoding = 'utf-8'
    re_json = res.json()
    articles = re_json["data"]['articles']
    for i in articles:
        id = i['extraId']
        channel = {
            'id': f'jstv_{id}',
            'name': i["title"],
            'id0': id,
            'source': 'jstv'
        }
        channels.append(channel)
        print(channel)
    return channels

# asyncio.run(get_channels_jstv())
# asyncio.run(get_epgs_jstv({'id': 'jstv_676', 'name': '江苏卫视4K超高清', 'id0': '676', 'source': 'jstv'}))
