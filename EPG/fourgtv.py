# -*- coding:utf-8 -*-
import httpx
import datetime
import os


async def get_epgs_4gtv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'https://www.4gtv.tv/proglist/%s.txt' % (channel_id0)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=8)
        res.encoding = 'utf-8'
        res_json = res.json()
        for j in res_json:
            title = j['title']
            start_date = j['sdate']
            start_time = j['stime']
            end_date = j['edate']
            end_time = j['etime']
            starttime = datetime.datetime.strptime(
                '%s%s' % (start_date, start_time), '%Y-%m-%d%H:%M:%S')
            endtime = datetime.datetime.strptime(
                '%s%s' % (end_date, end_time), '%Y-%m-%d%H:%M:%S')
            epg = {'channel_id': channel_id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': '',
                   'program_date': starttime.date(),
                   }
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


async def get_channels_4gtv():
    url = 'http://api2.4gtv.tv/Channel/GetAllChannel/pc/L'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-CA;q=0.8,en;q=0.7,zh-TW;q=0.6',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    }
    async with httpx.AsyncClient() as client:
        res = await client(url, headers=headers)
    res.encoding = 'utf-8'
    js = res.json()['Data']
    channels = []
    for j in js:
        id = str(j['fnID'])
        type = j['fsTYPE']
        name = j['fsNAME']
        gtvid = j['fs4GTV_ID']
        logo = j['fsLOGO_MOBILE']
        desc = j['fsDESCRIPTION'] if 'fsDESCRIPTION' in j else ''
        all = [name, gtvid, logo]

        channel = {
            'name': name,
            'id': [gtvid],
            'url': 'https://www.4gtv.tv/channel',
            'source': '4gtv',
            'logo': logo,
            'desc': desc,
        }
        channels.append(channel)
        print(channel)
    return channels

# ret = await get_epgs_4gtv({'id': '4gtv_litv-ftv03', 'name': 'VOA美國之音', 'id0': '4gtv-live050', 'source': '4gtv'})
