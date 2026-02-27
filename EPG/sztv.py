import httpx
import datetime
import asyncio
import os
from bs4 import BeautifulSoup
import hashlib
import hmac
import time
import datetime
import base64
import random

async def get_epgs_sztv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    x_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    x_random = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=16))
    payload = f"""x-date: {x_date}\nx-random: {x_random}\nhost: apix.scms.sztv.com.cn"""
    h = base64.b64encode(hmac.new(bytes('xUJ7Gls45St0CTnatnwZwsH4UyYj0rpX', 'UTF-8'), payload.encode("utf-8"), hashlib.sha512).digest()).decode()
    url = f'https://apix.scms.sztv.com.cn/api/com/channelAct/getCutvChannelAct?types=2&id={channel_id0}&appVersion=10.0.3&client=Android&tenantId=ysz&tenantid=ysz'
    headers = {
        "x-date": x_date,
        "x-random": x_random,
        "host": "apix.scms.sztv.com.cn",
        "proxy-authorization": f'hmac username="onesz", algorithm="hmac-sha512", headers="x-date x-random host", signature="{h}"'
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res.encoding = 'utf-8'
        returnData = res.json()['returnData']['list']
        for day in returnData[::-1]:
            daytime = day['daytime']
            for i in day['programme']:
                epg = {
                    'channel_id': channel_id,
                    'starttime': datetime.datetime.fromtimestamp((daytime + i['s']) / 1000),
                    'endtime': '',
                    'title': i['t'],
                    'desc': ''
                }
                epgs.append(epg)
                # print(epg)
            for i in range(len(epgs) - 1):
                epgs[i]['endtime'] = epgs[i+1]['starttime']
            if epgs:
                epgs = epgs[:-1]
            # for i in epgs:
            #     print(i)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (spidername, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0
    }
    return ret


async def get_channels_sztv():
    channels = []
    x_date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    x_random = ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=16))
    payload = f"""x-date: {x_date}\nx-random: {x_random}\nhost: apix.scms.sztv.com.cn"""
    h = base64.b64encode(hmac.new(bytes('xUJ7Gls45St0CTnatnwZwsH4UyYj0rpX', 'UTF-8'), payload.encode("utf-8"), hashlib.sha512).digest()).decode()
    headers = {
        "x-date": x_date,
        "x-random": x_random,
        "host": "apix.scms.sztv.com.cn",
        "proxy-authorization": f'hmac username="onesz", algorithm="hmac-sha512", headers="x-date x-random host", signature="{h}"'
    }
    async with httpx.AsyncClient() as client:
        res = await client.get("https://apix.scms.sztv.com.cn/api/com/catalog/getCatalogList?types=2&appCode=201&isTree=0&appVersion=10.0.3&client=Android&tenantId=ysz&tenantid=ysz", headers=headers)
    returnData = res.json()['returnData']
    for i in returnData:
        id = i['id']
        channel = {
            'id': f'sztv_{id}',
            'name': i["name"],
            'id0': id,
            'source': 'sztv'
        }
        channels.append(channel)
        print(channel)
    return channels

# asyncio.run(get_channels_sztv())
# asyncio.run(get_epgs_sztv({'id': 'sztv_24725', 'name': '深圳卫视4K超高清', 'id0': 24725, 'source': 'sztv'}))
