import httpx
import datetime
import asyncio
import os


async def get_epgs_btzx(channel, dt):
    epgs = []
    msg = ''
    success = 1
    dt_str = dt.strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("https://api.btzx.com.cn/mobileinf/rest/cctv/videolivelist/dayWeb", params={"json": {'id': channel_id0, 'day': dt_str}, "cb": ""})
        res.encoding = 'utf-8'
        # print(res.text)
        videolivelist = res.json()['videolivelist']
        for videolive in videolivelist:
            title = videolive['title']
            starttime = datetime.datetime.strptime(videolive['startdate'], "%Y-%m-%d %H:%M:%S")
            endtime = datetime.datetime.strptime(videolive['enddate'], "%Y-%m-%d %H:%M:%S")
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

# asyncio.run(get_epgs_btzx({'id': 'btzx', 'name': "兵团卫视", 'id0': 'TvCh1540979167111228', 'source': 'bztx'}, datetime.datetime.now()))
