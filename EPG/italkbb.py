import asyncio
import datetime
import os
import time
import uuid
from zoneinfo import ZoneInfo

import httpx


ITALKBB_API_BASE = "https://api.italkbbtv.com"
ITALKBB_AUTH_PATH = "/auth/v1/token"
ITALKBB_CHANNELS_PATH = "/classictv/live/v1/lives"
ITALKBB_EPG_PATH = "/classictv/live/v1/lives/{channel_id}/dvrs"
ITALKBB_ROOT_ID = "62ac4e2e4beefe535864769d"
ITALKBB_CATEGORY_ID = "62ac4e314beefe53586476c2"
ITALKBB_APP_VERSION = "305013"
ITALKBB_TIMEZONE = ZoneInfo("Asia/Shanghai")
ITALKBB_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
ITALKBB_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.italkbbtv.com/",
    "User-Agent": "Mozilla/5.0",
}

_DEVICE_ID = str(uuid.uuid4())
_TOKEN = None
_TOKEN_EXPIRES_AT = 0
_TOKEN_TASK = None
_EPG_CACHE = {}
_EPG_INFLIGHT_REQUESTS = {}


def _token_is_valid():
    return _TOKEN and time.time() * 1000 < _TOKEN_EXPIRES_AT - 60_000


async def _request_visitor_token():
    form = {
        "device_type": "web",
        "device_model": "Chrome",
        "app_version": ITALKBB_APP_VERSION,
        "device_id": _DEVICE_ID,
        "login_type": "password",
        "grant_type": "tv_login_in",
        "login_name": f"{_DEVICE_ID}@web.visitor.italkbb.com",
        "password": "visitor_secret",
    }
    async with httpx.AsyncClient(
        base_url=ITALKBB_API_BASE,
        timeout=ITALKBB_TIMEOUT,
    ) as client:
        response = await client.post(
            ITALKBB_AUTH_PATH,
            data=form,
            headers=ITALKBB_HEADERS,
        )
    response.raise_for_status()
    access = response.json().get("access") or {}
    token = access.get("token")
    expires_at = access.get("expire_time")
    if not token or not isinstance(expires_at, (int, float)):
        raise ValueError("iTalkBB visitor login returned no access token")
    return token, expires_at


async def _get_visitor_token():
    global _TOKEN, _TOKEN_EXPIRES_AT, _TOKEN_TASK

    if _token_is_valid():
        return _TOKEN
    if _TOKEN_TASK is None:
        _TOKEN_TASK = asyncio.create_task(_request_visitor_token())

    task = _TOKEN_TASK
    try:
        token, expires_at = await task
    finally:
        if _TOKEN_TASK is task:
            _TOKEN_TASK = None

    _TOKEN = token
    _TOKEN_EXPIRES_AT = expires_at
    return token


def _invalidate_token(token):
    global _TOKEN, _TOKEN_EXPIRES_AT

    if _TOKEN == token:
        _TOKEN = None
        _TOKEN_EXPIRES_AT = 0


async def _request_italkbb_json(path, params=None):
    for attempt in range(2):
        token = await _get_visitor_token()
        headers = {**ITALKBB_HEADERS, "Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(
            base_url=ITALKBB_API_BASE,
            timeout=ITALKBB_TIMEOUT,
        ) as client:
            response = await client.get(path, params=params, headers=headers)

        if response.status_code == 401 and attempt == 0:
            _invalidate_token(token)
            continue
        response.raise_for_status()
        return response.json()

    raise RuntimeError("iTalkBB request failed after token refresh")


async def _request_italkbb_epg(channel_id):
    payload = await _request_italkbb_json(
        ITALKBB_EPG_PATH.format(channel_id=channel_id),
        params={"sort": "start_at", "order": "desc", "hl": "zh_CN"},
    )
    programmes = payload.get("dvrs")
    if not isinstance(programmes, list):
        raise ValueError(f"iTalkBB EPG response has no dvrs list: {channel_id}")
    return programmes


async def _fetch_italkbb_epg(channel_id):
    cached = _EPG_CACHE.get(channel_id)
    if cached is not None:
        return cached

    task = _EPG_INFLIGHT_REQUESTS.get(channel_id)
    if task is None:
        task = asyncio.create_task(_request_italkbb_epg(channel_id))
        _EPG_INFLIGHT_REQUESTS[channel_id] = task

    try:
        programmes = await task
    except Exception:
        if _EPG_INFLIGHT_REQUESTS.get(channel_id) is task:
            _EPG_INFLIGHT_REQUESTS.pop(channel_id, None)
        raise

    _EPG_CACHE[channel_id] = programmes
    if _EPG_INFLIGHT_REQUESTS.get(channel_id) is task:
        _EPG_INFLIGHT_REQUESTS.pop(channel_id, None)
    return programmes


def _is_retryable(error):
    if not isinstance(error, httpx.HTTPStatusError):
        return True
    status_code = error.response.status_code
    return status_code in (408, 429) or status_code >= 500


async def get_epgs_italkbb(channel):
    epgs = []
    channel_id = channel["id"]
    channel_id0 = str(channel["id0"])

    try:
        programmes = await _fetch_italkbb_epg(channel_id0)
        seen = set()
        for programme in programmes:
            title = str(programme.get("name") or "").strip()
            start_at = programme.get("start_at")
            end_at = programme.get("end_at")
            if not title or not isinstance(start_at, (int, float)):
                continue
            if not isinstance(end_at, (int, float)):
                duration = programme.get("duration")
                if not isinstance(duration, (int, float)):
                    continue
                end_at = start_at + duration
            if end_at <= start_at:
                continue

            starttime = datetime.datetime.fromtimestamp(
                start_at,
                tz=ITALKBB_TIMEZONE,
            )
            endtime = datetime.datetime.fromtimestamp(
                end_at,
                tz=ITALKBB_TIMEZONE,
            )
            programme_key = (
                str(programme.get("id") or ""),
                starttime,
                title,
            )
            if programme_key in seen:
                continue
            seen.add(programme_key)
            epgs.append({
                "channel_id": channel_id,
                "starttime": starttime,
                "endtime": endtime,
                "title": title,
                "desc": "",
            })

        if not epgs:
            raise ValueError(f"iTalkBB EPG has no valid programmes: {channel_id0}")
        epgs.sort(key=lambda item: item["starttime"])
    except Exception as error:
        spidername = os.path.splitext(os.path.basename(__file__))[0]
        return {
            "success": 0,
            "epgs": [],
            "msg": (
                f"spider-{spidername}-{type(error).__name__}-{error}"
            ),
            "ban": 0,
            "retryable": _is_retryable(error),
        }

    return {
        "success": 1,
        "epgs": epgs,
        "msg": "",
        "ban": 0,
    }


async def get_channels_italkbb():
    payload = await _request_italkbb_json(
        ITALKBB_CHANNELS_PATH,
        params={
            "root_id": ITALKBB_ROOT_ID,
            "category_id": ITALKBB_CATEGORY_ID,
            "data_version": "",
            "page": 1,
            "size": 100,
            "hl": "zh_CN",
        },
    )
    items = payload.get("lives")
    if not isinstance(items, list):
        raise ValueError("iTalkBB channels response has no lives list")

    channels = []
    for item in items:
        channel_id = str(item.get("id") or "").strip()
        name = str(item.get("name") or "").strip()
        if not channel_id or not name or not item.get("show_dvr"):
            continue
        channels.append({
            "id": f"italkbb_{channel_id}",
            "name": name,
            "id0": channel_id,
            "source": "italkbb",
        })
    return channels


if __name__ == "__main__":
    for channel in asyncio.run(get_channels_italkbb()):
        print(channel)
