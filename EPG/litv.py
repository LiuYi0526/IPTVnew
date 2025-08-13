import sqlite3
import datetime
import os
import asyncio
import httpx
import zipfile
import io
import logging
import json


async def download_litv_epgs():
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ABR-AL80 Build/4860264.0)",
        "Host": "proxy.svc.litv.tv",
        "Connection": "Keep-Alive" 
    }
    data = json.dumps({"jsonrpc":"2.0","id":9527,"method":"ConfigService.GetConfigNoAuth","params":{"device_id":"0","swver":"LTAGP0231140LTV20250623101220","services":["epg"]}})
    async with httpx.AsyncClient() as client:
        response = await client.post("https://proxy.svc.litv.tv/cdi/v2/rpc", headers=headers, data=data)
    epg_sqlite_url = response.json()["result"]["epg_sqlite"][0]
    async with httpx.AsyncClient() as client:
        response = await client.get(epg_sqlite_url)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall("")
        logging.info("epg.db下载成功")


async def get_epgs_litv(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    try:
        conn = sqlite3.connect('epg.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            if channel_id0 == table_name:
                for row in rows:
                    id, channelname, title, starttime, endtime, ep, subtitle, desc = row
                    # print(row)
                    epg = {
                        'channel_id': channel_id,
                        'starttime': datetime.datetime.fromtimestamp(starttime / 1000),
                        'endtime': datetime.datetime.fromtimestamp(endtime / 1000),
                        'title': f'{title} - {subtitle}' if subtitle and subtitle != '' else title,
                        'desc': desc
                    }
                    # print(epg)
                    epgs.append(epg)
                conn.close()
                break
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
        print(msg)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0,

    }
    return ret


async def get_channels_litv():
    channels = []
    conn = sqlite3.connect('epg.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_name = tables[0][0]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    for row in rows:
        q, id0, w, name, logotv, logomobile, e, r, id, t, y, u = row
        print(row)
        channel = {
            'id': 'litv_' + id,
            'name': name,
            'id0': 'ch' + str(id0),
            'source': 'litv',
        }
        print(channel)
        channels.append(channel)


# asyncio.run(download_litv_epgs())
# asyncio.run(get_channels_litv())
# asyncio.run(get_epgs_litv({'id': 'litv_4gtv-4gtv009', 'name': '中天新聞台', 'id0': 'ch52', 'source': 'litv'}))
