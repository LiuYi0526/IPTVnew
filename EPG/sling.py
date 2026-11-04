import asyncio
import datetime
import os
import re
import sys
from collections import defaultdict

import httpx


# Adapted from CharmingEPG's Sling platform implementation.
SLING_CMS_BASE = "https://cbd46b77.cdn.cms.movetv.com"
SLING_SUMMARY_URL = (
    f"{SLING_CMS_BASE}/cms/publish3/domain/summary/ums/1.json"
)
SLING_SCHEDULE_URL = (
    f"{SLING_CMS_BASE}/cms/publish3/channel/schedule/24/"
    "{date}/1/{guid}.json"
)
SLING_CHANNEL_MAP_URL = (
    "https://raw.githubusercontent.com/CharmingCheung/CharmingEPG/"
    "main/app/epg_platform/data/sling_channels.json"
)
SLING_TIMEOUT = httpx.Timeout(60.0, connect=15.0)
SLING_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0",
}
SLING_REQUEST_ATTEMPTS = 3
SLING_TEST_NAME = re.compile(
    r"(?:pilot|signal-test|atomizertest|opstest|mctest|stb-test)",
    re.I,
)

_CATALOG = None
_CATALOG_TASK = None
_SCHEDULE_CACHE = {}
_SCHEDULE_INFLIGHT_REQUESTS = {}


def _normalized(value):
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _candidate_score(local, item):
    metadata = item.get("metadata") or {}
    wanted = _normalized(local.get("name"))
    call_sign = _normalized(metadata.get("call_sign"))
    title = _normalized(item.get("title"))
    raw = " ".join(
        str(value or "")
        for value in (metadata.get("call_sign"), item.get("title"))
    )
    return (
        wanted in {call_sign, title},
        not bool(SLING_TEST_NAME.search(raw)),
        bool(item.get("offered")),
        bool((item.get("visibility") or {}).get("visible", True)),
        item.get("primary_channel_guid") == item.get("channel_guid"),
    )


def _load_channel_map(payload):
    if not isinstance(payload, list):
        raise ValueError("Sling channel map is not a list")
    return [
        {"id": row[0], "name": row[1], "guid": row[2]}
        for row in payload
        if isinstance(row, list) and len(row) == 3
    ]


def _match_catalog(local_channels, payload):
    cms_channels = [
        item
        for item in payload.get("channels", [])
        if (item.get("metadata") or {}).get("is_linear_channel")
    ]
    by_id = defaultdict(list)
    by_callsign = defaultdict(list)
    for item in cms_channels:
        if item.get("dyna_source_id") is not None:
            by_id[str(item["dyna_source_id"])].append(item)
        metadata = item.get("metadata") or {}
        for value in (metadata.get("call_sign"), item.get("title")):
            normalized = _normalized(value)
            if normalized:
                by_callsign[normalized].append(item)

    catalog = []
    for local in local_channels:
        choices = by_id.get(str(local.get("id")), [])
        if not choices:
            choices = by_callsign.get(_normalized(local.get("name")), [])
        if not choices:
            continue
        item = max(
            choices,
            key=lambda candidate: _candidate_score(local, candidate),
        )
        cms_guid = str(item.get("channel_guid") or "").strip()
        if not cms_guid:
            continue
        metadata = item.get("metadata") or {}
        genres = metadata.get("genre") or []
        if isinstance(genres, str):
            genres = [genres]
        catalog.append({
            "id": str(local["guid"]),
            "name": str(
                metadata.get("channel_name") or local["name"]
            ).strip(),
            "cms_guid": cms_guid,
            "category": str(genres[0]).strip() if genres else "Sling",
        })
    return catalog


async def _request_json(url):
    last_error = None
    for attempt in range(SLING_REQUEST_ATTEMPTS):
        try:
            async with httpx.AsyncClient(timeout=SLING_TIMEOUT) as client:
                response = await client.get(url, headers=SLING_HEADERS)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, (dict, list)):
                raise ValueError("Sling CMS response is not JSON data")
            return payload
        except Exception as error:
            last_error = error
            if attempt + 1 < SLING_REQUEST_ATTEMPTS:
                await asyncio.sleep(2 ** attempt)
    raise RuntimeError(f"Sling CMS request failed: {last_error}") from last_error


async def _request_catalog():
    summary, channel_map = await asyncio.gather(
        _request_json(SLING_SUMMARY_URL),
        _request_json(SLING_CHANNEL_MAP_URL),
    )
    return _match_catalog(_load_channel_map(channel_map), summary)


async def _fetch_catalog():
    global _CATALOG, _CATALOG_TASK

    if _CATALOG is not None:
        return _CATALOG
    if _CATALOG_TASK is None:
        _CATALOG_TASK = asyncio.create_task(_request_catalog())

    task = _CATALOG_TASK
    try:
        catalog = await task
    finally:
        if _CATALOG_TASK is task:
            _CATALOG_TASK = None
    _CATALOG = catalog
    return catalog


async def _request_schedule(cms_guid, date):
    url = SLING_SCHEDULE_URL.format(date=date, guid=cms_guid)
    payload = await _request_json(url)
    rows = ((payload.get("schedule") or {}).get("scheduleList") or [])
    if not isinstance(rows, list):
        raise ValueError(f"Sling schedule has no scheduleList: {cms_guid}")
    return rows


async def _fetch_schedule(cms_guid, date):
    cache_key = (cms_guid, date)
    cached = _SCHEDULE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    task = _SCHEDULE_INFLIGHT_REQUESTS.get(cache_key)
    if task is None:
        task = asyncio.create_task(_request_schedule(cms_guid, date))
        _SCHEDULE_INFLIGHT_REQUESTS[cache_key] = task

    try:
        rows = await task
    except Exception:
        if _SCHEDULE_INFLIGHT_REQUESTS.get(cache_key) is task:
            _SCHEDULE_INFLIGHT_REQUESTS.pop(cache_key, None)
        raise

    _SCHEDULE_CACHE[cache_key] = rows
    if _SCHEDULE_INFLIGHT_REQUESTS.get(cache_key) is task:
        _SCHEDULE_INFLIGHT_REQUESTS.pop(cache_key, None)
    return rows


def _parse_program(channel_id, row):
    title = str(row.get("title") or row.get("grid_title") or "").strip()
    try:
        start_timestamp = int(row["schedule_start"])
        stop_value = row.get("schedule_stop")
        if stop_value is None:
            stop_value = start_timestamp + int(row["duration"])
        end_timestamp = int(stop_value)
        starttime = datetime.datetime.fromtimestamp(
            start_timestamp,
            datetime.timezone.utc,
        )
        endtime = datetime.datetime.fromtimestamp(
            end_timestamp,
            datetime.timezone.utc,
        )
    except (KeyError, TypeError, ValueError, OSError):
        return None
    if not title or endtime <= starttime:
        return None

    metadata = row.get("metadata") or {}
    program_data = row.get("program") or {}
    subtitle = str(
        metadata.get("episode_title") or program_data.get("name") or ""
    ).strip()
    if subtitle and subtitle != title:
        title = f"{title} : {subtitle}"
    description = str(
        metadata.get("short_description")
        or metadata.get("description")
        or program_data.get("short_description")
        or ""
    )
    return {
        "channel_id": channel_id,
        "starttime": starttime,
        "endtime": endtime,
        "title": title,
        "desc": description,
    }


def _is_retryable(error):
    cause = error.__cause__ if isinstance(error, RuntimeError) else error
    if not isinstance(cause, httpx.HTTPStatusError):
        return True
    status_code = cause.response.status_code
    return status_code in (408, 429) or status_code >= 500


async def get_epgs_sling(channel, dt):
    channel_id = channel["id"]
    cms_guid = str(channel["id0"])

    try:
        date = dt.strftime("%Y%m%d")
        rows = await _fetch_schedule(cms_guid, date)

        epgs_by_key = {}
        for row in rows:
            epg = _parse_program(channel_id, row)
            if epg is None:
                continue
            key = (
                row.get("schedule_guid"),
                epg["starttime"],
                epg["title"],
            )
            epgs_by_key[key] = epg
        epgs = sorted(
            epgs_by_key.values(),
            key=lambda item: item["starttime"],
        )
        if not epgs:
            raise ValueError(f"Sling EPG has no valid programmes: {cms_guid}")
    except Exception as error:
        spidername = os.path.splitext(os.path.basename(__file__))[0]
        return {
            "success": 0,
            "epgs": [],
            "msg": f"spider-{spidername}-{type(error).__name__}-{error}",
            "ban": 0,
            "retryable": _is_retryable(error),
        }

    return {
        "success": 1,
        "epgs": epgs,
        "msg": "",
        "ban": 0,
    }


async def get_channels_sling():
    catalog = await _fetch_catalog()
    channels = []
    for item in catalog:
        channels.append({
            "id": f"sling_{item['id']}",
            "name": item["name"],
            "id0": item["cms_guid"],
            "source": "sling",
        })
    return channels


if __name__ == "__main__":
    name_filter = " ".join(sys.argv[1:]).strip().casefold()
    for channel in asyncio.run(get_channels_sling()):
        if not name_filter or name_filter in channel["name"].casefold():
            print(channel)
