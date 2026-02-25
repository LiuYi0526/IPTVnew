import httpx
import datetime
import asyncio
import os
from bs4 import BeautifulSoup

async def get_epgs_fjtv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    dt_str = dt.strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = f'https://live.fjtv.net/m2o/program_switch.php?channel_id={channel_id0}&play_time=0&dates={dt_str}&shownums=7'
    headers = {
        'Referer': 'https://live.fjtv.net/'
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.find("div", id="liveSchedule").find_all('li')
        for li in items:
            start_time0 = li.find('span', class_="time").text.strip()
            start_time = datetime.datetime.strptime(f"{dt_str} {start_time0}", "%Y-%m-%d %H:%M:%S")
            for span in li.find_all("span"):
                span.extract()
            title = li.get_text().replace(start_time0, "").strip()
            epg = {
                'channel_id': channel_id,
                'starttime': start_time,
                'endtime': '',
                'title': title,
                'desc': ''
            }
            epgs.append(epg)
            # print(epg)
        for i in range(len(epgs) - 1):
            epgs[i]['endtime'] = epgs[i+1]['starttime']
        if epgs:
            epgs[-1]['endtime'] = datetime.datetime.strptime(f"{dt_str} 23:59:59", "%Y-%m-%d %H:%M:%S")
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
        'last_program_date': dt,
        'ban': 0
    }
    return ret


# asyncio.run(get_epgs_fjtv({'id': 'fjtv_665248990102917120', 'name': '福建综合频道', 'id0': '665248990102917120', 'source': 'fjtv'}, datetime.datetime.now()))
