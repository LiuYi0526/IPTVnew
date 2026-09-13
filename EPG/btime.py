# -*- coding:utf-8 -*-
import asyncio
import datetime
import json
import os
import re
from zoneinfo import ZoneInfo

import httpx


BTIME_EPG_URL = 'https://app.api.btime.com/btv/menuList'
BTIME_CHANNELS_URL = 'https://app.api.btime.com/news/list'
BTIME_CHANNEL_CID = '89c77e29681377ac932434f78870b9b0'
BTIME_TIMEZONE = ZoneInfo('Asia/Shanghai')
BTIME_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
BTIME_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0',
}


def _parse_duration(value):
    parts = str(value).strip().split(':')
    if len(parts) != 3:
        raise ValueError(f'Invalid BTime duration: {value}')
    hours, minutes, seconds = (int(part) for part in parts)
    return datetime.timedelta(
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )


def _channel_sort_key(channel):
    mark = channel.get('btv_mark', '')
    match = re.search(r'(\d+)$', mark)
    if match:
        return 0, int(match.group(1)), channel['name']
    return 1, mark, channel['name']


async def get_epgs_btime(channel):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    gid = str(channel['id0'])

    try:
        async with httpx.AsyncClient(timeout=BTIME_TIMEOUT) as client:
            response = await client.get(
                BTIME_EPG_URL,
                params={'gid': gid},
                headers=BTIME_HEADERS,
            )
        response.raise_for_status()
        payload = response.json()
        if payload.get('errno') != 0:
            raise ValueError(
                payload.get('message')
                or payload.get('errmsg')
                or f"BTime EPG errno: {payload.get('errno')}"
            )

        days = payload.get('data', {}).get('data')
        if not isinstance(days, list) or not days:
            raise ValueError(f'BTime EPG has no days: {gid}')

        seen = set()
        for day in days:
            programmes = day.get('data')
            if not isinstance(programmes, list):
                continue
            for programme in programmes:
                title = str(programme.get('name') or '').strip()
                start_text = programme.get('fdate')
                duration_text = programme.get('length')
                if not title or not start_text or not duration_text:
                    continue

                try:
                    starttime = datetime.datetime.strptime(
                        start_text,
                        '%Y-%m-%d %H:%M:%S',
                    ).replace(tzinfo=BTIME_TIMEZONE)
                    endtime = starttime + _parse_duration(duration_text)
                except (TypeError, ValueError):
                    continue
                if endtime <= starttime:
                    continue

                programme_key = (
                    str(programme.get('id') or ''),
                    starttime,
                    title,
                )
                if programme_key in seen:
                    continue
                seen.add(programme_key)
                epg = {
                    'channel_id': channel_id,
                    'starttime': starttime,
                    'endtime': endtime,
                    'title': title,
                    'desc': '',
                }
                # print(epg)
                epgs.append(epg)

        if not epgs:
            raise ValueError(f'BTime EPG has no valid programmes: {gid}')
        epgs.sort(key=lambda item: item['starttime'])
    except Exception as error:
        success = 0
        spidername = os.path.splitext(os.path.basename(__file__))[0]
        msg = 'spider-%s-%s-%s' % (
            spidername,
            type(error).__name__,
            error,
        )

    return {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0,
    }


async def get_channels_btime():
    params = {
        'protocol': '3',
        'cid': BTIME_CHANNEL_CID,
        'cname': '看电视',
        'is_paging': '1',
        'offset': '0',
        'refresh_type': '1',
        'refresh_count': '1',
        'last': '',
        'gid': '',
        'refresh_total': '1',
    }
    async with httpx.AsyncClient(timeout=BTIME_TIMEOUT) as client:
        response = await client.get(
            BTIME_CHANNELS_URL,
            params=params,
            headers=BTIME_HEADERS,
        )
    response.raise_for_status()
    payload = response.json()
    if payload.get('errno') != 0:
        raise ValueError(
            payload.get('message')
            or payload.get('errmsg')
            or f"BTime channels errno: {payload.get('errno')}"
        )

    cards = payload.get('data', {}).get('data')
    if not isinstance(cards, list):
        raise ValueError('BTime channels response has no data list')

    channels_by_gid = {}
    for card in cards:
        news_items = (card.get('data') or {}).get('news')
        if not isinstance(news_items, list):
            continue
        for item in news_items:
            if item.get('type') != 6:
                continue
            item_data = item.get('data') or {}
            gid = str(item.get('gid') or '').strip()
            name = str(item_data.get('title') or '').strip()
            if not gid or not name:
                continue

            try:
                meta = json.loads(item_data.get('meta') or '{}')
            except (TypeError, json.JSONDecodeError):
                meta = {}
            btv_mark = str(meta.get('btv_mark') or '').strip()
            suffix = btv_mark.lower() if btv_mark else gid
            channels_by_gid[gid] = {
                'id': f'btime_{suffix}',
                'name': name,
                'id0': gid,
                'source': 'btime',
                'btv_mark': btv_mark,
            }

    channels = sorted(channels_by_gid.values(), key=_channel_sort_key)
    for channel in channels:
        channel.pop('btv_mark', None)
        print(channel)
    return channels


if __name__ == '__main__':
    asyncio.run(get_channels_btime())
    # asyncio.run(get_epgs_btime({'id': 'btime_btv_12', 'name': '北京卫视', 'id0': '573ib1kp5nk92irinpumbo9krlb', 'source': 'btime'}))