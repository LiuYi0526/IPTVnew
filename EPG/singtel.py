import asyncio
import datetime
import os
from zoneinfo import ZoneInfo

import httpx


SINGTEL_EPG_URL = "https://api.liuyi0526.com/singtelcast/v1/channels/epg/"
SINGTEL_CHANNELS_URL = "https://api.v3.singtelcast.com/v1/channels/"
SINGTEL_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
SINGTEL_TIMEZONE = ZoneInfo("Asia/Singapore")
SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")
UTC = datetime.timezone.utc
SINGTEL_SLOT_HOURS = 6

_SINGTEL_EPG_CACHE = {}
_SINGTEL_INFLIGHT_REQUESTS = {}

SINGTEL_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "origin": "https://watchcast.singtel.com",
    "pragma": "no-cache",
    "referer": "https://watchcast.singtel.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
    "x-api-key": "weLnqiyqPWw6zQuVf9tXbpssrL2VVDTbzHiVbSnw",
}


def _format_utc_datetime(value, milliseconds):
    return value.strftime("%Y-%m-%dT%H:%M:%S") + f".{milliseconds}Z"


def _iter_singtel_time_slots(dt):
    local_start = datetime.datetime.combine(dt, datetime.time.min).replace(
        tzinfo=SINGTEL_TIMEZONE
    )
    utc_start = local_start.astimezone(UTC)
    for hour_offset in range(0, 24, SINGTEL_SLOT_HOURS):
        start = utc_start + datetime.timedelta(hours=hour_offset)
        end = start + datetime.timedelta(
            hours=SINGTEL_SLOT_HOURS,
            milliseconds=-1,
        )
        yield (
            _format_utc_datetime(start, "000"),
            _format_utc_datetime(end, "999"),
        )


def _parse_singtel_datetime(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


async def _request_singtel_epg(start, end):
    params = {
        "offset": "0",
        "limit": "10000",
        "startdate": start,
        "enddate": end,
    }
    async with httpx.AsyncClient(timeout=SINGTEL_TIMEOUT) as client:
        res = await client.get(
            SINGTEL_EPG_URL,
            params=params,
            headers=SINGTEL_HEADERS,
        )
    res.raise_for_status()
    data = res.json()
    items = data.get("data")
    if not isinstance(items, list):
        raise ValueError("Singtel EPG response has no data list")
    return items


async def _fetch_singtel_epg(start, end):
    cache_key = (start, end)
    cached_items = _SINGTEL_EPG_CACHE.get(cache_key)
    if cached_items is not None:
        return cached_items

    task = _SINGTEL_INFLIGHT_REQUESTS.get(cache_key)
    if task is None:
        task = asyncio.create_task(_request_singtel_epg(start, end))
        _SINGTEL_INFLIGHT_REQUESTS[cache_key] = task

    try:
        items = await task
    except Exception:
        if _SINGTEL_INFLIGHT_REQUESTS.get(cache_key) is task:
            _SINGTEL_INFLIGHT_REQUESTS.pop(cache_key, None)
        raise

    _SINGTEL_EPG_CACHE[cache_key] = items
    if _SINGTEL_INFLIGHT_REQUESTS.get(cache_key) is task:
        _SINGTEL_INFLIGHT_REQUESTS.pop(cache_key, None)
    return items


async def get_epgs_singtel(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = str(channel['id0'])
    try:
        slot_items = await asyncio.gather(*(
            _fetch_singtel_epg(start, end)
            for start, end in _iter_singtel_time_slots(dt)
        ))
        for items in slot_items:
            for item in items:
                epg_channel_id = str(item.get('epgChannelId', ''))
                if not epg_channel_id:
                    continue
                if epg_channel_id == channel_id0:
                    title = item.get('title', '') or ''
                    subtitle = item.get('subtitle', '') or ''
                    description = item.get('description', '') or ''
                    if subtitle:
                        title = f"{title} {subtitle}".strip()
                    start_str = item.get('startDate')
                    duration = item.get('duration')
                    if not start_str or duration is None:
                        continue
                    start_utc = _parse_singtel_datetime(start_str)
                    end_utc = start_utc + datetime.timedelta(seconds=int(duration))
                    start_time = start_utc.astimezone(SHANGHAI_TIMEZONE)
                    end_time = end_utc.astimezone(SHANGHAI_TIMEZONE)
                    epg = {
                        'channel_id': channel_id,
                        'starttime': start_time,
                        'endtime': end_time,
                        'title': title,
                        'desc': description,
                    }
                    # print(epg)
                    epgs.append(epg)
        epgs.sort(key=lambda item: item['starttime'])
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s-%s' % (spidername, type(e).__name__, e)
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'ban': 0
    }
    return ret


async def get_channels_singtel():
    channels = []
    params = {"offset": "0", "limit": "200"}

    async with httpx.AsyncClient(timeout=SINGTEL_TIMEOUT) as client:
        res = await client.get(
            SINGTEL_CHANNELS_URL,
            params=params,
            headers=SINGTEL_HEADERS,
        )
    res.raise_for_status()
    data = res.json()
    items = data.get('data')
    if not isinstance(items, list):
        raise ValueError("Singtel channels response has no data list")
    for item in items:
        epg_channel_id = str(item.get('epgChannelId') or '')
        title = item.get('title')
        if not epg_channel_id or not title:
            continue
        channel = {
            'id': 'singtel_' + epg_channel_id,
            'name': title,
            'id0': epg_channel_id,
            'source': 'singtel',
        }
        print(channel)
        channels.append(channel)
    return channels


if __name__ == '__main__':
    asyncio.run(get_channels_singtel())
    # asyncio.run(get_epgs_singtel({'id': 'singtel_5585', 'name': 'Celestial Movies(HD)', 'id0': '5585', 'source': 'singtel'}, dt=datetime.datetime.now()))
