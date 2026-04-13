# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import asyncio

async def get_epgs_gehua(channel, dt):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    date_str = dt.strftime("%Y-%m-%d")
    try:
        # url = f"https://yfsxcx.yun.gehua.net.cn/ghyx-api/api/v1/epg/liveEpg.json?date={date_str}&channelId={channel_id0}&type=&pageNo=1&pageSize=100&scope=1&openId="
        url = f"https://api.liuyi0526.com/yfsxcx?date={date_str}&channelId={channel_id0}"
        headers = {
            "charset": "utf-8",
            "User-Agent": "Mozilla/5.0 (Linux) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.173 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br"
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res.encoding = "utf-8"
        # print(res.text)
        res_list = res.json()["response"]["responseBody"]["list"]
        for item in res_list:
            title = item["title"]
            starttime = datetime.datetime.strptime(item["date"] + item["startTime"], "%Y-%m-%d%H:%M")
            endtime = datetime.datetime.strptime(item["date"] + item["endTime"], "%Y-%m-%d%H:%M")
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


async def get_channels_gehua():
    date_str = datetime.datetime.now().date().strftime("%Y-%m-%d")
    url = f"https://yfsxcx.yun.gehua.net.cn/ghyx-api/api/v2/epg/liveEpg.json?date={date_str}&channelId=&type=ALL&pageNo=1&pageSize=100&scope=0&openId="
    headers = {
        "charset": "utf-8",
        "User-Agent": "Mozilla/5.0 (Linux) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.173 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br"
    }
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
    res_list = res.json()["response"]["responseBody"]["list"]
    channels = []
    for li in res_list:
        name = li["channelName"]
        id = li["channelId"]
        channel = {
            "id": f"guhua_{id}",
            "name": name,
            "id0": id,
            "source": "gehua",
        }
        print(channel)
        channels.append(channel)
    return channels


# asyncio.run(get_channels_gehua())
# asyncio.run(get_epgs_gehua({"id": "guhua_613", "name": "CCTV-13高清", "id0": "613", "source": "gehua"}, datetime.datetime.now().date()))
