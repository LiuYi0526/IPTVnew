import httpx
import datetime
import asyncio
import os
import datetime
import time
import re

def has_chinese(text):
    # 包含更多中文字符范围
    pattern = r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]'
    return bool(re.search(pattern, text))

async def get_epgs_starhub(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    date_str = dt.strftime("%Y%m%d")
    starttime = int(time.mktime(time.strptime(f"{date_str}000000", "%Y%m%d%H%M%S")))
    endtime = int(time.mktime(time.strptime(f"{date_str}235959", "%Y%m%d%H%M%S")))
    params = {
        "locale": "zh",
        "locale_default": "en_US",
        "device": "1",
        "limit": "500",
        "page": "1",
        "in_channel_id": channel_id0,
        "gt_end": str(starttime),
        "lt_start": str(endtime),
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("https://waf-starhub-metadata-api-p001.ifs.vubiquity.com/v3.1/epg/schedules", params=params)
        res.encoding = 'utf-8'
        data = res.json()
        for resource in data.get('resources', []):
            if resource.get('metatype') == 'Schedule':
                title = resource.get('title', '')
                description = resource.get('description', '')

                episode_number = resource.get('episode_number')
                if episode_number:
                    if has_chinese(title) or has_chinese(description):
                        title = f"{title} - E{episode_number}"
                    else:
                        title = f"E{episode_number} - {title}"
                
                serie_title = resource.get('serie_title', '')
                if serie_title:
                    title = f"{serie_title} - {title}"

                rating = resource.get('rating', '')
                if rating:
                    title = f"{title}[{rating}]"

                start_time = datetime.datetime.fromtimestamp(resource.get('start')).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                end_time = datetime.datetime.fromtimestamp(resource.get('end')).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
                epg = {
                    'channel_id': channel_id,
                    'starttime': start_time,
                    'endtime': end_time,
                    'title': title,
                    'desc': description
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
        'ban': 0
    }
    return ret


async def get_channels_starhub():
    channels = []
    params = {
        "locale": "zh",
        "locale_default": "en_US",
        "device": "1",
        "limit": "150",
        "page": "1"
    }
    async with httpx.AsyncClient() as client:
            res = await client.get("https://waf-starhub-metadata-api-p001.ifs.vubiquity.com/v3.1/epg/channels", params=params)
    res.encoding = 'utf-8'
    data = res.json()
    for resource in data.get('resources', []):
        if resource.get('metatype') == 'Channel':
            id = resource['id']
            number = resource['number']
            channel = {
                'id': f'starhubtvplus_{number}',
                'name': resource["title"],
                'id0': id,
                'source': 'starhub'
            }
            channels.append(channel)
            print(channel)
    return channels

# asyncio.run(get_channels_starhub())
# asyncio.run(get_epgs_starhub({'id': 'starhub_d440ee6e-6f9a-4d78-b37b-5be89051145a', 'name': 'Phoenix InfoNews Channel HD', 'id0': 'd440ee6e-6f9a-4d78-b37b-5be89051145a', 'source': 'starhub'}, dt=datetime.datetime.now()))
