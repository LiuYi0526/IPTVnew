import httpx
import datetime
import asyncio
import os
import datetime

async def get_epgs_fengshows(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    date_str = dt.strftime("%Y%m%d")
    url = f'https://api.fengshows.cn/live/{channel_id0}/resources?dir=asc&date={date_str}&page=1&page_size=99'
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
        res.encoding = 'utf-8'
        returnData = res.json()
        for i in returnData:
            epg = {
                'channel_id': channel_id,
                'starttime': datetime.datetime.fromisoformat(i["event_time"]).astimezone(datetime.timezone(datetime.timedelta(hours=8))),
                'endtime': '',
                'title': i['title'],
                'desc': ''
            }
            epgs.append(epg)
            # print(epg)
        for i in range(len(epgs) - 1):
            epgs[i]['endtime'] = epgs[i+1]['starttime']
        if epgs:
            epgs[-1]['endtime'] = (datetime.datetime.strptime(f"{date_str} 00:00:00", "%Y%m%d %H:%M:%S") + datetime.timedelta(days=1)).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        # for i in epgs:
        #     print(i)
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


# asyncio.run(get_epgs_fengshows({'id': 'fengshows_1', 'name': '資訊台', 'id0': "7c96b084-60e1-40a9-89c5-682b994fb680", 'source': 'fengshows'}, dt=datetime.datetime.now()))
