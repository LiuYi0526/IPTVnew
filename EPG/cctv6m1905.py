import httpx
import datetime
import os
from bs4 import BeautifulSoup


async def get_epgs_1905(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = f'https://m.1905.com/m/{channel_id0}/list/'
    starttime = datetime.datetime(dt.year, dt.month, dt.day, 0, 0) + datetime.timedelta(days=1)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser').find("div", class_="hasCons")
        for i in soup.find_all("li")[::-1]:
            title = i.find('em').text
            endtime = starttime
            starttime = datetime.datetime.fromtimestamp(int(i['data-id']))
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
        'epgs': epgs[::-1],
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


# await get_channels_cctv()
# await get_epgs_1905({'id': '1905_xl', 'name': '初秋·电影放映厅', 'id0': 'xl', 'source': '1905'}, datetime.datetime.now())
