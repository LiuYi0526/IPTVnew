import httpx
import datetime
import asyncio
import os
import ssl
import secrets

async def get_epgs_wisetv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    dt_str = dt.strftime('%Y%m%d')
    channel_id = channel['id']
    channel_id0 = channel['id0']
    android_id = secrets.token_hex(8)
    try:
        async with httpx.AsyncClient() as client:
            # res = await client.get(f"https://api.wisetv.com.cn:8684/6/program/{channel_id0}/{dt_str}", headers=headers,follow_redirects=True)
            res = await client.get(f"https://program.wisetv.com.cn/{channel_id0}-1100000041-{dt_str}.json")
        data = res.json()["data"][0]["data"]
        for i in data:
            epg = {
                'channel_id': channel_id,
                'starttime': datetime.datetime.strptime(i["starttime"], "%Y-%m-%d %H:%M:%S"),
                'endtime': datetime.datetime.strptime(i["endtime"], "%Y-%m-%d %H:%M:%S"),
                'title': i["text"],
                'desc': ''
            }
            epgs.append(epg)
            # print(epg)
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


async def get_channels_wisetv():
    channels = []
    android_id = secrets.token_hex(8)
    headers = {
        "x-bindcp": "",
        "x-appcode": "503",
        "x-bindarea": "",
        "User-Agent": "WiseTVAndroid/VersionName:7.4.5(VersionCode:503; SystemInt:32) okhttp3(3.12.12)",
        "ak": "HyQuy347BBv9En+0VZ8ToA==",
        "x-rec": "on",
        "x-sysver": "12",
        "x-userid": "",
        "x-phonever": "M2011K2C",
        "x-phoneno": "",
        "authorization": "",
        "x-bindid": "",
        "x-deviceid": android_id,
        "sk": "CQNRW8hsdrKKwHr1ofFgdw==",
        "iemi": android_id,
        "x-platform": "Android",
        "x-devicetoken": "",
        "x-appversion": "7.4.5",
    }
    context = ssl.create_default_context()
    context.set_ciphers('DEFAULT@SECLEVEL=0')
    context.load_cert_chain(certfile='wisetv.crt', keyfile='wisetv.key')
    async with httpx.AsyncClient(verify=context) as client:
        res = await client.get("https://api.wisetv.com.cn:8684/6/channelvalid", headers=headers)
    contents = res.json()["data"]["data"][0]["contents"]
    for i in contents:
        id = i['id']
        channel = {
            'id': f'wisetv_{id}',
            'name': i["channelName"],
            'id0': id,
            'source': 'wisetv'
        }
        channels.append(channel)
        print(channel)
    return channels

# asyncio.run(get_channels_wisetv())
# asyncio.run(get_epgs_wisetv({'id': 'jstv_30001110000000000000000000000698', 'name': '天津卫视', 'id0': '30001110000000000000000000000698', 'source': 'wisetvtv'}, datetime.datetime.now()))