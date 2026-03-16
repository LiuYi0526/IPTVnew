# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import asyncio

async def get_epgs_sc96655(channel, dt):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    date_str = dt.strftime("%Y-%m-%d")
    try:
        url = f"http://epg.iqy.sc96655.com/v1/getPrograms?channel={channel_id0}&begin_time={date_str} 00:00:00&end_time={date_str} 23:59:59&partner=1"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5ODQwODlhNjc1OGU0ZjJlOTViMjk4NWM4YjA1MDNmYiIsImNvbXBhbnkiOiJxaXlpIiwibmFtZSI6InRlcm1pbmFsIn0.1gDPpBcHJIE8dLiq7UekUlPWMtJOYymI8zoIYlsVgc4",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res.encoding = "utf-8"
        ret_data = res.json()["ret_data"]
        for item in ret_data:
            title = item["name"]
            starttime = datetime.datetime.strptime(item["begin_time"], "%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(item["end_time"], "%Y-%m-%d %H:%M:%S")
            epg = {
                "channel_id": channel_id,
                "starttime": starttime,
                "endtime": endtime,
                "title": title,
                "desc": ""
            }
            # print(epg)
            epgs.append(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split(".")[0]
        msg = "spider-%s-%s" % (channel_id, e)
    ret = {
        "success": success,
        "epgs": epgs,
        "msg": msg,
        "ban": 0,
    }
    return ret


async def get_channels_sc96655():
    date_str = datetime.datetime.now().date().strftime("%Y-%m-%d")
    url = "http://epg.iqy.sc96655.com/v1/getChannels?partner=1&terminal=&definition=&citycode=&adcode=&charge_type=&channel_type="
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5ODQwODlhNjc1OGU0ZjJlOTViMjk4NWM4YjA1MDNmYiIsImNvbXBhbnkiOiJxaXlpIiwibmFtZSI6InRlcm1pbmFsIn0.1gDPpBcHJIE8dLiq7UekUlPWMtJOYymI8zoIYlsVgc4"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
    ret_data = res.json()["ret_data"]
    channels = []
    for li in ret_data:
        name = li["name"]
        id = li["id"]
        channel = {
            "id": f"sc96655_{id}",
            "name": name,
            "id0": str(id),
            "source": "sc96655",
        }
        print(channel)
        channels.append(channel)
    return channels


# asyncio.run(get_channels_sc96655())
# asyncio.run(get_epgs_sc96655({'id': 'sc96655_3916', 'name': 'CGTN-西班牙语', 'id0': 3916, 'source': 'sc96655'}, datetime.datetime.now().date()))
