#-*- coding:utf-8 -*-
#广东广播电视台-官网来源,2021-12-16添加到数据库，只有广东地区频道共10多个
import httpx
import datetime
import xml.etree.ElementTree as ET
import asyncio
import html

GDTv_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


async def get_epgs_gdtv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    retryable = True
    url = f'https://api.liuyi0526.com/gdtv/{channel_id0}/{need_date}.xml'
    try:
        async with httpx.AsyncClient(timeout=GDTv_TIMEOUT) as client:
            # res = await client.get(f'http://epg.gdtv.cn/f/{channel_id0}/{need_date}.xml')
            res = await client.get(url)
        res.raise_for_status()
        root = ET.fromstring(res.content)
        if root.tag != 'epg':
            raise ValueError(f'unexpected root element: {root.tag}')
        epgs_contents = root.findall('.//content')
        for epga in epgs_contents:
            starttime = datetime.datetime.fromtimestamp(int(epga.get('time1')))
            endtime = datetime.datetime.fromtimestamp(int(epga.get('time2')))
            title = html.unescape(
                (epga.text or '').replace("<br />", "\n").strip()
            )
            if not title or endtime <= starttime:
                continue
            epg = {
                'channel_id': channel_id,
                'starttime': starttime,
                'endtime': endtime,
                'title': title,
                'desc': ''
            }
            epgs.append(epg)
            # print(epg)
    except httpx.HTTPStatusError as e:
        success = 0
        status_code = e.response.status_code
        retryable = status_code in (408, 429)
        msg = f'spider-gdtv-HTTPStatusError-{status_code}-{url}'
    except Exception as e:
        success = 0
        msg = 'spider-gdtv-%s-%s' % (
            type(e).__name__,
            str(e) or repr(e),
        )
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'retryable': retryable,
        'ban':0,
    }
    return ret

async def get_channels_gdtv():
    async with httpx.AsyncClient() as client:
        res = await client.get('http://epg.gdtv.cn/f/1.xml')
    res.raise_for_status()
    root = ET.fromstring(res.content)
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
# asyncio.run(get_epgs_gdtv({'id': 'gdtv_7', 'name': '嘉佳卡通', 'id0': '7', 'source': 'gdtv'}, datetime.datetime.now().date()))
