# -*- coding:utf-8 -*-
import os
import httpx
import datetime
import asyncio
import xml.etree.ElementTree as ET
import pytz

async def get_epgs_hoy(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    need_date = dt.strftime('%Y%m%d')
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f'https://epg-file.hoy.tv/hoy/OTT{channel_id0}{need_date}.xml')
        res.encoding = 'utf-8'
        root = ET.fromstring(res.text)
        for channel in root.findall('./Channel'):
            for epg_item in channel.findall('./EpgItem'):
                starttime = datetime.datetime.strptime(epg_item.find('./EpgStartDateTime').text, "%Y-%m-%d %H:%M:%S")
                endtime = datetime.datetime.strptime(epg_item.find('./EpgEndDateTime').text, "%Y-%m-%d %H:%M:%S")
                episode_info = epg_item.find('./EpisodeInfo')
                title = episode_info.find('./EpisodeShortDescription').text
                episode_index = episode_info.find('./EpisodeIndex').text
                if int(episode_index) > 0:
                    title += f"-第{episode_index}集"
                EpgOtherInfo = epg_item.find('./EpgOtherInfo').text
                if EpgOtherInfo != None:
                    title += epg_item.find('./EpgOtherInfo').text
                desc = episode_info.find('./EpisodeLongDescription').text
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': endtime,
                    'title': title,
                    'desc': desc,
                }
                epgs.append(epg)
                # print(epg)
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

# asyncio.run(get_epgs_hoy({'id': 'HOY_77', 'name': 'HOY TV', 'id0': '77', 'source': 'hoy'}, datetime.datetime.now().date()))
