# -*- coding:utf-8 -*-
import datetime
import os
import httpx
import asyncio

SCHEDULE_URL = "https://iptv.jxntv.cn/contentservice/channel/getChannelScheduleListByChannelCode"
SCHEDULE_HEADERS = {
    "clientType": "1",
    "isp": "CTC",
    "projectCode": "GANTV",
    "spid": "12",
}
_schedule_cache = {}


async def _get_schedules(client, channel_code, date_str):
    cache_key = (channel_code, date_str)
    if cache_key in _schedule_cache:
        return _schedule_cache[cache_key]

    response = await client.get(
        SCHEDULE_URL,
        headers=SCHEDULE_HEADERS,
        params={
            "channelCode": channel_code,
            "date": date_str,
            "pageNumber": "1",
            "pageSize": "100",
        },
    )
    response.raise_for_status()
    result = response.json()["data"]["schedules"]["result"]
    _schedule_cache[cache_key] = result
    return result


async def get_epgs_jxntv(channel, dt):
    epgs = []
    msg = ""
    success = 1
    channel_id = channel["id"]
    channel_id0 = channel["id0"]
    date_str = dt.strftime("%Y%m%d")
    next_date_str = (dt + datetime.timedelta(days=1)).strftime("%Y%m%d")
    try:
        async with httpx.AsyncClient() as client:
            result = await _get_schedules(client, channel_id0, date_str)
            try:
                next_result = await _get_schedules(
                    client,
                    channel_id0,
                    next_date_str,
                )
            except Exception:
                next_result = []
        next_starttimes = sorted(
            datetime.datetime.strptime(
                item["startDate"] + item["startTime"],
                "%Y%m%d%H:%M",
            )
            for item in next_result
        )
        for item in result:
            name = item["name"]
            starttime = datetime.datetime.strptime(item["startDate"] + item["startTime"], "%Y%m%d%H:%M")
            epg = {
                "channel_id": channel_id,
                "starttime": starttime,
                "endtime": "",
                "title": name,
                "desc": ""
            }
            epgs.append(epg)
        epgs.sort(key=lambda epg: epg["starttime"])
        for index, epg in enumerate(epgs):
            if index + 1 < len(epgs):
                endtime = epgs[index + 1]["starttime"]
            else:
                endtime = next(
                    (
                        next_starttime
                        for next_starttime in next_starttimes
                        if next_starttime > epg["starttime"]
                    ),
                    epg["starttime"] + datetime.timedelta(minutes=30),
                )
            epg["endtime"] = endtime
            # print(epg)
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


async def get_channels_jxntv():
    url = "https://iptv.jxntv.cn/contentservice/channel/getChannelListByCategoryCode"
    headers = {
        "clientType": "1",
        "isp": "CTC",
        "projectCode": "GANTV",
        "spid": "12"
    }
    querystring = {"categoryCode":"f5b8e163836e4f1fbb104368daf4570c","pageNumber":"1","pageSize":"1000","isWithExtInfo":"2"}
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers, params=querystring)
    result = res.json()["data"]["result"]
    channels = []
    for i in result:
        name = i["name"]
        code = i["code"]
        channelNumber = i["channelNumber"]
        channel = {
            "id": f"jxntv_{channelNumber}",
            "name": name,
            "id0": code,
            "source": "jxntv",
        }
        print(channel)
        channels.append(channel)
    return channels


if __name__ == "__main__":
    asyncio.run(get_channels_jxntv())
    # asyncio.run(get_epgs_jxntv({'id': 'jxntv_19', 'name': '江西卫视-高清', 'id0': 'Umai:CHAN/2097383@BESTV.STA.SMG', 'source': 'jxntv'}, datetime.datetime.now().date()))
