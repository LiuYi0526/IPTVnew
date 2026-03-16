# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import time
import asyncio

async def get_epgs_bfgd(channel, dt):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    date_str = dt.strftime("%Y%m%d")
    starttime = int(time.mktime(time.strptime(f"{date_str}000000", "%Y%m%d%H%M%S")))
    endtime = int(time.mktime(time.strptime(f"{date_str}235959", "%Y%m%d%H%M%S")))
    accesstoken = "R5F2408FEU3198804BK78052214IE73560DFP2BF4M340CE68V0Z339CBW1626D4D261E46FEA"
    try:
        url = f"http://slave.bfgd.com.cn/media/event/get_list?chnlid={channel_id0}&pageidx=1&vcontrol=0&attachdesc=1&repeat=1&accesstoken={accesstoken}&starttime={starttime}&endtime={endtime}&pagenum=100&flagposter=0"
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        res.encoding = "utf-8"
        event_list = res.json()["event_list"]
        for event in event_list:
            starttime = datetime.datetime.fromtimestamp(event["start_time"])
            endtime = datetime.datetime.fromtimestamp(event["end_time"])
            epg = {
                "channel_id": channel_id,
                "starttime": starttime,
                "endtime": endtime,
                "title": event["event_name"],
                "desc": event["desc"]
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


async def get_channels_bfgd():
    url = "http://slave.bfgd.com.cn/media/channel/get_list?accesstoken=R5F2408FEU3198804BK78052214IE73560DFP2BF4M340CE68V0Z339CBW1626D4D261E46FEA&pageidx=1&pagenum=100"
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    chnl_list = res.json()["chnl_list"]
    channels = []
    for chnl in chnl_list:
        name = chnl["chnl_name"]
        id = chnl["chnl_id"]
        channel = {
            "id": f"bfgd_{id}",
            "name": name,
            "id0": id,
            "source": "bfgd",
        }
        print(channel)
        channels.append(channel)
    return channels


# asyncio.run(get_channels_bfgd())
# asyncio.run(get_epgs_bfgd({'id': 'bfgd_4200000636', 'name': '重温经典', 'id0': 4200000636, 'source': 'bfgd'}, datetime.datetime.now().date()))
