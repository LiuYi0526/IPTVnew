import httpx
import datetime
import os

async def get_epgs_hami(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    need_date = dt.strftime('%Y-%m-%d')
    reqUrl = "https://hamivideo.hinet.net/channel/epg.do"
    payload = f"contentPk={channel_id0}&date={need_date}"
    headersList = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" 
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(reqUrl, data=payload, headers=headersList)
        response = res.json()
        for prog_list in response:
            title = prog_list['programName']
            starttime = datetime.datetime.fromtimestamp(int(prog_list['startTime']))
            endtime = datetime.datetime.fromtimestamp(int(prog_list['endTime']))
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

# await get_epgs_hami({'id': 'OTT_LIVE_0000001853', 'name': '愛爾達體育MAX1台', 'id0': 'OTT_LIVE_0000001853', 'source': 'hami'}, datetime.datetime.now())