# -*- coding:utf-8 -*-
import asyncio
import datetime
import os
from zoneinfo import ZoneInfo

import httpx


ELTA_CHANNELS_URL = (
    'https://piceltaott-elta.cdn.hinet.net/production/json/'
    'channel/channel_list.json'
)
ELTA_PROGRAM_URL = (
    'https://piceltaott-elta.cdn.hinet.net/production/json/'
    'program_list/program_list_{date}.json'
)
ELTA_TIMEZONE = ZoneInfo('Asia/Taipei')
ELTA_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
ELTA_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0',
}
ELTA_REQUEST_RETRIES = 3

_program_cache = {}
_program_tasks = {}


async def _request_json(url):
    async with httpx.AsyncClient(
        timeout=ELTA_TIMEOUT,
        follow_redirects=True,
    ) as client:
        for attempt in range(1, ELTA_REQUEST_RETRIES + 1):
            try:
                response = await client.get(url, headers=ELTA_HEADERS)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError):
                if attempt == ELTA_REQUEST_RETRIES:
                    raise
                await asyncio.sleep(0.5 * attempt)


async def _download_programs(date_str):
    payload = await _request_json(
        ELTA_PROGRAM_URL.format(date=date_str)
    )
    if not isinstance(payload, dict):
        raise ValueError(f'ELTA program list is not an object: {date_str}')
    return payload


async def _get_programs(date_str):
    if date_str in _program_cache:
        return _program_cache[date_str]

    task = _program_tasks.get(date_str)
    if task is None:
        task = asyncio.create_task(_download_programs(date_str))
        _program_tasks[date_str] = task

    try:
        payload = await task
    except Exception:
        if _program_tasks.get(date_str) is task:
            _program_tasks.pop(date_str, None)
        raise

    _program_cache[date_str] = payload
    if _program_tasks.get(date_str) is task:
        _program_tasks.pop(date_str, None)
    return payload


async def get_epgs_elta(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = str(channel['id0'])
    date_str = dt.strftime('%Y-%m-%d')

    try:
        payload = await _get_programs(date_str)
        if channel_id0 not in payload:
            raise ValueError(
                f'ELTA channel {channel_id0} is missing on {date_str}'
            )

        seen = set()
        for programme in payload[channel_id0]:
            title = str(programme.get('program_desc') or '').strip()
            if not title:
                continue

            try:
                starttime = datetime.datetime.fromtimestamp(
                    int(programme['start_time']),
                    ELTA_TIMEZONE,
                )
                endtime = datetime.datetime.fromtimestamp(
                    int(programme['end_time']),
                    ELTA_TIMEZONE,
                )
            except (KeyError, TypeError, ValueError, OSError):
                continue

            if starttime.date() != dt or endtime <= starttime:
                continue

            programme_key = (
                str(programme.get('program_sn') or ''),
                starttime,
                endtime,
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


async def get_channels_elta():
    payload = await _request_json(ELTA_CHANNELS_URL)
    if not isinstance(payload, list):
        raise ValueError('ELTA channel list is not an array')

    channels = []
    active_channels = sorted(
        (
            item
            for item in payload
            if item.get('cl_status') == 1 and item.get('cl_display') == 1
        ),
        key=lambda item: (item.get('cl_order', 0), item.get('cl_num', 0)),
    )
    for item in active_channels:
        channel_number = str(item['cl_num'])
        channel = {
            'id': f'elta_{channel_number}',
            'name': str(item['cl_title']).strip(),
            'id0': channel_number,
            'source': 'elta',
        }
        print(channel)
        channels.append(channel)
    return channels


if __name__ == '__main__':
    asyncio.run(get_channels_elta())
    # asyncio.run(get_epgs_elta(
    #     {'id': 'elta_101', 'name': '體育 1 台', 'id0': '101', 'source': 'elta'},
    #     datetime.date.today(),
    # ))
