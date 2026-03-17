# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import json
import asyncio

async def get_epgs_xmtv(channel, get_days):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    date_str = (datetime.datetime.now().date() + datetime.timedelta(days=get_days)).strftime("%Y-%m-%d")
    try:
        url = f"https://mapi1.kxm.xmtv.cn/api/v1/tvshow_share.php?channel_id={channel_id0}&zone={get_days}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        res.encoding = "utf-8"
        for i in res.json():
            title = i["theme"]
            starttime = datetime.datetime.strptime(date_str + i["start"], "%Y-%m-%d%H:%M")
            endtime = datetime.datetime.strptime(date_str + i["end"], "%Y-%m-%d%H:%M")
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


# asyncio.run(get_epgs_xmtv({'id': 'xmtv_84', 'name': '厦门卫视', 'id0': '84', 'source': 'xmtv'}, get_days=-1))
