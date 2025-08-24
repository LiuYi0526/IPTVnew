import httpx
import datetime
import json
import os


async def get_epgs_xjtvs(channel, dt):
    epgs = []
    msg = ''
    success = 1
    need_date = dt.strftime('%Y-%m-%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = 'https://slstapi.xjtvs.com.cn/api/TVLiveV100/TVGuideList?tvChannelId=%s&date=%s+00:00:00&json=true' % (channel_id0, need_date)
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
        res.encoding = 'utf-8'
        programs = json.loads(res.text)
        prog_lists = programs['data']
        for prog_list in prog_lists:
            title = prog_list['Name']
            starttime = datetime.datetime.strptime(prog_list['TVDate'] + prog_list['StartTime'], '%Y-%m-%d%H:%M')
            endtime = datetime.datetime.strptime(prog_list['TVDate'] + prog_list['EndTime'], '%Y-%m-%d%H:%M')
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
        'ban': 0,
    }
    return ret


# await get_channels_cctv()
# await get_epgs_xjtvs({'id': 'XJTV-2', 'name': 'XJTV-2', 'id0': '3', 'source': 'xjtvs'}, datetime.datetime.now())
