# -*- coding:utf-8 -*-
import os
import httpx
import datetime
import asyncio
import hmac
import base64
import time
import hashlib
import json

HNTV_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class HntvProgramsUnavailableError(ValueError):
    pass


async def get_epgs_hntv(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    dt_ts = int(datetime.datetime.combine(dt, datetime.datetime.min.time()).timestamp())
    retryable = True
    try:
        ts = int(time.time())
        sign = hashlib.sha256(f'6ca114a836ac7d73{ts}'.encode()).hexdigest()
        headers = {
            'tenant_id': '1',
            'timestamp': str(ts),
            'sign': sign,
            'User-Agent': 'okhttp/3.12.0'
        }
        async with httpx.AsyncClient(timeout=HNTV_TIMEOUT) as client:
            res = await client.get(f'https://pubmod.hntv.tv/program/getAuth/vod/originStream/program/{channel_id0}/{dt_ts}', headers=headers)
        res.raise_for_status()
        payload = res.json()
        programs = payload.get('programs')
        if programs is None:
            raise HntvProgramsUnavailableError(
                f'channel {channel_id0} returned no programs; '
                f'keys={sorted(payload) if isinstance(payload, dict) else []}'
            )
        for program in programs:
            title = program['title']
            starttime = datetime.datetime.fromtimestamp(int(program['beginTime']))
            endtime = datetime.datetime.fromtimestamp(int(program['endTime']))
            epg = {
                'channel_id': channel_id,
                'starttime': starttime,
                'endtime': endtime,
                'title': title,
                'desc': '',
            }
            epgs.append(epg)
            # print(epg)
    except HntvProgramsUnavailableError as e:
        success = 0
        retryable = False
        msg = f'spider-{channel_id}-{type(e).__name__}-{e}'
    except httpx.HTTPStatusError as e:
        success = 0
        status_code = e.response.status_code
        retryable = status_code in (408, 429) or status_code >= 500
        msg = f'spider-{channel_id}-HTTPStatusError-{status_code}'
    except Exception as e:
        success = 0
        msg = 'spider-%s-%s-%s' % (
            channel_id,
            type(e).__name__,
            str(e) or repr(e),
        )
    ret = {
        'success': success,
        'epgs': epgs,
        'msg': msg,
        'retryable': retryable,
        'ban': 0,
    }
    return ret

# asyncio.run(get_epgs_hntv({'id': 'hntv_145', 'name': '河南卫视', 'id0': '145', 'source': 'hntv'}, datetime.datetime.now().date()))
