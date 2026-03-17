# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import json
import asyncio

async def get_epgs_sxtvs(channel):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    date_str = datetime.datetime.now().date().strftime("%Y-%m-%d")
    try:
        url = f"https://qidian.sxtvs.com/api/v3/program/tv?channel={channel_id0}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        res.encoding = "utf-8"
        snr_Playlist = json.loads(res.text[19:-1])
        for item in snr_Playlist:
            title = item["name"]
            starttime = datetime.datetime.strptime(date_str + item["start"], "%Y-%m-%d%H:%M")
            endtime = datetime.datetime.strptime(date_str + item["end"], "%Y-%m-%d%H:%M")
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


# asyncio.run(get_epgs_sxtvs({'id': 'sxtvs_star','name': '陕西卫视', 'id0': 'star', 'source': 'sxtvs'}))
