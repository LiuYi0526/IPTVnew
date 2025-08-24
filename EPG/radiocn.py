import asyncio
import datetime
import hashlib
import httpx
import time


async def get_epgs_radiocn(channel, dt):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    opts = 'broadcastId=%s&date=%s' % (channel_id0, need_date)
    url = f'https://ytmsout.radio.cn/web/appProgram/listByDate?{opts}'
    tm = str(int(time.time() * 1000))
    signText = f"{opts}&timestamp={tm}&key=f0fc4c668392f9f9a447e48584c214ee"
    headers = {
        "equipmentId": "0000",
        "timestamp": tm,
        "sign": hashlib.md5(signText.encode('utf-8')).hexdigest()
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, timeout=10)
        data = res.json()['data']
        for i in data:
            epg = {
                'channel_id': channel_id,
                'starttime': datetime.datetime.fromtimestamp(i['startTime'] / 1000),
                'endtime': datetime.datetime.fromtimestamp(i['endTime'] / 1000),
                'title': i['programName'],
                'desc': ''
            }
            # print(epg)
            epgs.append(epg)
    except Exception as e:
        success = 0
        msg = 'spider-%s-%s-%s' % (channel_id, need_date, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0
    }
    return ret


async def get_channels_radiocn():
    channels = []
    opts = 'categoryId=0&provinceCode=0'
    tm = str(int(time.time() * 1000))
    signText = f"{opts}&timestamp={tm}&key=f0fc4c668392f9f9a447e48584c214ee"
    headers = {
        "equipmentId": "0000",
        "timestamp": tm,
        "sign": hashlib.md5(signText.encode('utf-8')).hexdigest()
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(f'https://ytmsout.radio.cn/web/appBroadcast/list?{opts}', headers=headers)
    data = res.json()['data']
    for i in data:
        id = i['contentId']
        channel = {
            'id': 'radiocn_' + id,
            'name': i['title'],
            'id0': id,
            'source': 'radiocn'
        }
        channels.append(channel)
        print(channel)
    return channels


# asyncio.run(get_channels_radiocn())
# asyncio.run(get_epgs_radiocn({'id': 'radiocn_639', 'name': '中国之声', 'id0': '639', 'source': 'radiocn'}, datetime.datetime.now()))
