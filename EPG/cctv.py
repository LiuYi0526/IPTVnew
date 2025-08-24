import httpx
import re
import datetime
import json
from bs4 import BeautifulSoup


async def get_epgs_cctv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y%m%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'http://api.cntv.cn/epg/getEpgInfoByChannelNew?c=%s&serviceId=tvcctv&d=%s&t=jsonp&cb=set' % (channel_id0, need_date)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
        res.encoding = 'utf-8'
        programs = json.loads(res.text[4:-2])
        prog_lists = programs['data'][channel_id0]['list']
        for prog_list in prog_lists:
            title = prog_list['title']
            starttime = datetime.datetime.fromtimestamp(prog_list['startTime'])
            endtime = datetime.datetime.fromtimestamp(prog_list['endTime'])
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
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret


async def get_channels_cctv():
    channels = []
    async with httpx.AsyncClient() as client:
        res = await client.get('https://tv.cctv.com/epg/index.shtml')
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    lis = soup.select('div.channel_con > div > ul > li')
    need_date = datetime.datetime.now().strftime('%Y%m%d')
    for li in lis:
        id = li.select('img')[0].attrs['title'].strip()
        # logo = 'http://' + li.select('img')[0].attrs['src'].strip()
        url_info = 'http://api.cntv.cn/epg/getEpgInfoByChannelNew?c=%s&serviceId=tvcctv&d=%s&t=jsonp&cb=set' % (id, need_date)
        async with httpx.AsyncClient() as client:
            res = await client.get(url_info, timeout=5)
        res.encoding = 'utf-8'
        research = re.search('"channelName":"(.+?)".+?"lvUrl":"(.+?)"', res.text)
        name = research.group(1)
        # url = research.group(2)
        channel = {
            'id': 'cctv_' + id,
            'name': name,
            'id0': id,
            'source': 'cctv'
        }
        channels.append(channel)
        print(channel)
    return channels


# await get_channels_cctv()
# get_epgs_cctv({'id': 'cctv_cctv1', 'name': 'CCTV-1 综合', 'id0': 'cctv1', 'source': 'cctv'}, datetime.datetime.now())
