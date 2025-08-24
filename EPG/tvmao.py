# -*- coding:utf-8 -*-
import httpx
import datetime


async def get_epgs_tvmao(channel, dt):
    epgs = []
    desc = ''
    msg = ''
    success = 1
    ban = 0  # 标识是否被BAN掉了,此接口不确定是否有反爬机制
    channel_id = channel['id']
    channel_id0 = channel['id0']
    now_date = datetime.datetime.now().date()
    delta = dt - now_date
    now_weekday = now_date.weekday()
    need_weekday = now_weekday + delta.days + 1
    id_split = channel_id0.split('-')
    if len(id_split) == 2:
        id = id_split[1]
    elif len(id_split) == 3:
        id = '-'.join(id_split[1:3])
    else:
        id = channel_id0
    url = f"https://lighttv.tvmao.com/qa/qachannelschedule?epgCode={id}&op=getProgramByChnid&epgName=&isNew=on&day={need_weekday}"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res_j = res.json()
        datas = res_j[2]['pro']
        endtime = datetime.datetime.combine(dt, datetime.time(23, 59))
        for data in datas[::-1]:
            title = data['name']
            starttime_str = data['time']
            starttime = datetime.datetime.combine(dt, datetime.time(int(starttime_str[:2]), int(starttime_str[-2:])))
            epg = {
                'channel_id': channel_id,
                'starttime': starttime,
                'endtime': endtime,
                'title': title,
                'desc': ''
            }
            epgs.append(epg)
            # print(epg)
            endtime = starttime
    except Exception as e:
        success = 0
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs[::-1],
        'msg': msg,
        'ban': 0
    }
    return ret


# await get_epgs_tvmao({'id': 'tvmao_NANCHANG-NANCHANG1', 'name': '南昌电视台新闻综合频道', 'id0': 'NANCHANG-NANCHANG1', 'source': 'tvmao'}, datetime.datetime.now().date())
