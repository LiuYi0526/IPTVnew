# -*- coding:utf-8 -*-
import asyncio
import datetime
import json
import os
import datetime
import re
import os
import datetime
import httpx

headers = {
    'Accept': 'application/json, text/javascript, */*',
    'Api-Language': 'zh_TW',
}


async def get_epgs_tdm(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    dt1 = dt + datetime.timedelta(days=1)
    url = 'https://www.tdm.com.mo/api/v1.0/program-list/%s?channelId=%s' % (str(dt), channel_id0)
    url1 = 'https://www.tdm.com.mo/api/v1.0/program-list/%s?channelId=%s' % (str(dt1), channel_id0)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url1, headers=headers, timeout=8)
        res.encoding = 'utf-8'
        j = json.loads(res.text)
        starttime = datetime.datetime.strptime(j['data'][0]['date'], '%Y-%m-%d %H:%M:%S')
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, timeout=8)
        res.encoding = 'utf-8'
        j = json.loads(res.text)
        data = j['data']
        for d in data[::-1]:
            title = d['title']
            endtime = starttime
            starttime = datetime.datetime.strptime(d['date'], '%Y-%m-%d %H:%M:%S')
            if d['slug']:
                async with httpx.AsyncClient() as client:
                    res = await client.get(f"https://www.tdm.com.mo/api/v1.0/program/{d['slug']}/details", headers=headers, timeout=8)
                res.encoding = 'utf-8'
                j = json.loads(res.text)
                data0 = j['data']
                desc = data0['content'] if data0['content'] else ''
            else:
                desc = ''
            epg = {'channel_id': channel_id,
                   'starttime': starttime,
                   'endtime': endtime,
                   'title': title,
                   'desc': desc,
                   }
            epgs.append(epg)
            # print(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs[::-1],
        'msg': msg,
        'ban': 0,
    }
    return ret


# if __name__ == '__main__':
#     epgs = await get_epgs_tdm({'id': 'tdm_1', 'name': '澳視澳門 Ch. 91', 'id0': '1', 'source': 'tdm'}, datetime.datetime.now().date())
