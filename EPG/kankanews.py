# -*- coding:utf-8 -*-
import httpx, datetime, os, time, asyncio, random, hashlib


async def get_epgs_kankanews(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    dt_str = dt.strftime('%Y-%m-%d')
    try:
        timestamp = int(time.time())
        nonce = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))
        m_uuid = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=33))
        text = f"Api-Version=v1&channel_id={channel_id0}&date={dt_str}&nonce={nonce}&platform=android&timestamp={timestamp}&version=7.3.8&449e1a66579b23565f29b6bac451408522754c5f12301d7d6a334fc9a60dce03"
        sign = hashlib.md5(hashlib.md5(text.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; V2344A Build/ad8d58c.1) Knews/7.3.8",
            "platform": "android",
            "version": "7.3.8",
            "nonce": nonce,
            "timestamp": str(timestamp),
            "Api-Version": "v1",
            "sign": sign,
            "m-uuid": m_uuid,
            "Referer": "android.kankanews.com"
        }
        url = f"https://kapi.kankanews.com/content/app/tv/programs?channel_id={channel_id0}&date={dt_str}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res.encoding = 'utf-8'
        re_json = res.json()
        programs = re_json["result"]['list'][0]['programs']
        for program in programs:
            starttime = datetime.datetime.fromtimestamp(int(program['start']))
            endtime = datetime.datetime.fromtimestamp(int(program['end']))
            title = program['name'].strip()
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


async def get_channels_kankanews():
    channels = []
    timestamp = int(time.time())
    nonce = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))
    m_uuid = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=33))
    text = f"Api-Version=v1&nonce={nonce}&platform=android&timestamp={timestamp}&version=7.3.8&449e1a66579b23565f29b6bac451408522754c5f12301d7d6a334fc9a60dce03"
    sign = hashlib.md5(hashlib.md5(text.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest()
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; V2344A Build/ad8d58c.1) Knews/7.3.8",
        "platform": "android",
        "version": "7.3.8",
        "nonce": nonce,
        "timestamp": str(timestamp),
        "Api-Version": "v1",
        "sign": sign,
        "m-uuid": m_uuid,
        "Referer": "android.kankanews.com"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get("https://kapi.kankanews.com/content/app/tv/channels", headers=headers)
    res.encoding = 'utf-8'
    re_json = res.json()
    result_list = re_json["result"]['list']
    for i in result_list:
        id = i['id']
        channel = {
            'id': f'kankanews_{id}',
            'name': i["name"],
            'id0': id,
            'source': 'kankanews'
        }
        channels.append(channel)
        print(channel)
    return channels

# asyncio.run(get_channels_kankanews())
# asyncio.run(get_epgs_kankanews({'id': 'kankanews_1', 'name': '东方卫视', 'id0': 1, 'source': 'kankanews'}, datetime.datetime.now().date()))
