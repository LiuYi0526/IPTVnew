# -*- coding:utf-8 -*-
import asyncio
import time
import datetime
import os
import httpx


async def get_epgs_nowtv(channel, get_days):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    startDay = min(get_days)
    endDay = max(get_days)
    try:
        payload = {
            "channelIdList": [channel_id0],
            "startDay": startDay,
            "endDay": endDay,
            "lang": "zh",
            "callerReferenceNo": f"Ad449480d{int(time.time() * 1000)}",
            "platform": "NPX",
        }
        async with httpx.AsyncClient() as client:
            res = await client.post("https://catalogapi.nowtv.now.com/CatalogEngine/getEPGDetail", json=payload, timeout=10)
        res.raise_for_status()
        epgDetail = res.json().get("epgDetail", [])
        for channel_epg in epgDetail:
            channelId = str(channel_epg["channelId"])
            if channelId  == channel_id0:
                vimProgramIdList = [program["vimProgramId"] for program in channel_epg.get("programs", [])]
                break
        payload = {
            "lang": "zh",
            "programIdList": vimProgramIdList,
            "callerReferenceNo": f"Ad449480d{int(time.time() * 1000)}",
            "platform": "NPX",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("https://catalogapi.nowtv.now.com/CatalogEngine/getEPGProgramDetailList", json=payload, timeout=10)
        response.raise_for_status()
        epgProgramList = response.json()['epgProgramList']
        for epgProgram in epgProgramList:
            epg = {
                "channel_id": channel_id,
                "starttime": datetime.datetime.fromtimestamp(epgProgram["actualStartTime"] / 1000),
                "endtime": datetime.datetime.fromtimestamp(epgProgram["endTime"] / 1000),
                "title": epgProgram["progName"],
                "desc": epgProgram["synopsis"] if "synopsis" in epgProgram else ""
            }
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


async def get_channels_nowtv():
    channels = []
    payload = {
        "appId": "15",
        "lang": "zh",
        "callerReferenceNo": f"Ad449480d{int(time.time() * 1000)}",
        "platform": "NPX",
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://catalogapi.nowtv.now.com/CatalogEngine/getLiveChannelList", json=payload, timeout=10)
    res.raise_for_status()
    channelList = res.json()["channelList"]
    for channel in channelList:
        channelId = channel["channelId"]
        # print(cs[channel_id])
        name = channel["name"]
        channel = {
            "id": "nowtv_" + channelId,
            "name": name,
            "id0": channelId,
            "source": "nowtv",
        }
        print(channel)
        # print(f"#EXTINF:-1 tvg-id="nowtv_{channel_id}" tvg-name="{name}" tvg-logo="https://images.now-tv.com/shares/channelPreview/img/zh_tw/color/ch{channelId}_170_122" group-title="Now TV",{channelId} {name}")
        channels.append(channel)
    return channels


if __name__ == "__main__":
    channels = asyncio.run(get_channels_nowtv())
#     epgs = asyncio.run(get_epgs_nowtv({"id": "nowtv_331", "name": "Now直播台", "id0": "331", "source": "nowtv"}, get_days=(-1, 0, 1)))
#     print(epgs)
