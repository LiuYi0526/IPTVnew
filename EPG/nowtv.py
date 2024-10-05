# -*- coding:utf-8 -*-
import asyncio
import re
import datetime
import json
import os
import datetime
import re
import os
import datetime
import httpx

# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://nowtv.now.com/epg/',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'application/json, text/javascript, */*',
    'Pragma': 'no-cache',
    'Accept-Encoding': 'gzip, deflate',
    'Proxy-Connection': 'keep-alive',
}


async def get_epg_nowtv(channelepg, channel_id):
    starttime = datetime.datetime.fromtimestamp(channelepg['start'] / 1000)
    endtime = datetime.datetime.fromtimestamp(channelepg['end'] / 1000)
    title = channelepg['name']
    vimProgramId = channelepg['vimProgramId']
    async with httpx.AsyncClient() as client:
        response = await client.get(url=f'https://nowplayer.now.com/tvguide/epgprogramdetail?programId={vimProgramId}', headers=headers, timeout=8)
    res2 = json.loads(response.text)
    desc = res2['chiSynopsis'] if 'chiSynopsis' in res2 else ''
    epg = {'channel_id': channel_id,
           'starttime': starttime,
           'endtime': endtime,
           'title': title,
           'desc': desc,
           'program_date': starttime.date(),
           }
    return epg


async def get_epgs_nowtv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'https://now-tv.now.com/gw-epg/epg/zh_tw/%s/prf136/resp-ch/ch_%s.json' % (dt.strftime('%Y%m%d'), channel_id0)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        j = json.loads(res.text)
        chs = j['data']['chProgram']  # 很多频道的这一天的节目表
        for ch in chs:
            tasks = [get_epg_nowtv(channelepg, channel_id) for channelepg in chs[ch] if ch == channel_id0]
            epgs_ch = await asyncio.gather(*tasks)
            for i in epgs_ch:
                epgs.append(i)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0,
    }
    return ret


async def get_channels_nowtv():
    url = 'https://now-tv.now.com/gw-epg/epg/channelMapping.zh-TW.js'
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers, timeout=10)
    res.encoding = 'utf-8'
    reinfo = re.search('.+?var ChannelMapping=(.*)var GenreToChanne', res.text, re.DOTALL)
    cs = reinfo.group(1)[:-2]
    cs = json.loads(cs)
    channels = []
    for channel_id in cs:
        if 'name' not in cs[channel_id]:
            continue
        # id1 = cs[channel_id]['genreKeys'][0]
        # print(cs[channel_id])
        name = cs[channel_id]['name']
        channel = {
            'id': 'nowtv_' + channel_id,
            'name': name,
            'id0': channel_id,
            'source': 'nowtv',
        }
        print(channel)
        channels.append(channel)
    return channels


# if __name__ == '__main__':
#     channels = asyncio.run(get_channels_nowtv())
#     epgs = asyncio.run(get_epgs_nowtv({'id': 'nowtv_331', 'name': 'Now直播台', 'id0': '331', 'source': 'nowtv'}, datetime.datetime.now().date()))
#     print(epgs)
