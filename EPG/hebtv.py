import httpx
import datetime
import asyncio
import os


async def get_epgs_hebtv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    dt_str = (dt + datetime.timedelta(days=-5)).strftime('%Y-%m-%d')
    dt_end = (dt + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'https://api.cmc.hebtv.com/spidercrms/api/live/liveShowSet/findNoPage'
    headers = {'Content-Type': 'application/json', 'tenantId': '0d91d6cfb98f5b206ac1e752757fc5a9'}
    payload = {"sourceId": channel_id0, "tenantId": "0d91d6cfb98f5b206ac1e752757fc5a9", "day": dt_str, "dayEnd": dt_end}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload)
        res.encoding = 'utf-8'
        print(res.text)
        data = res.json()['data']
        for day in data:
            for i in data[day]:
                title = i['name']
                starttime = datetime.datetime.strptime(i['startDateTime'], "%Y-%m-%d %H:%M:%S")
                endtime = datetime.datetime.strptime(i['endDateTime'], "%Y-%m-%d %H:%M:%S")
                if starttime > endtime:
                    endtime = endtime + datetime.timedelta(days=1)
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': endtime,
                    'title': title,
                    'desc': ''
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
        'last_program_date': dt,
        'ban': 0
    }
    return ret


# asyncio.run(get_epgs_hebtv({'id': 'hebtv_462', 'name': "河北卫视", 'id0': '462', 'source': 'hebtv'}, datetime.datetime.now()))
