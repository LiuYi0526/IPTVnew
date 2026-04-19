import httpx
import datetime
import asyncio
import os
import datetime
import time
import pytz
import urllib

async def astro_get_access_token():
    params = {
        "client_id": "browser",
        "state": "guestUserLogin",
        "response_type": "token",
        "redirect_uri": "https://astrogo.astro.com.my",
        "scope": "urn:synamedia:vcs:ovp:guest-user",
        "prompt": "none",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
        "Referer": "https://astrogo.astro.com.my/",
    }
    async with httpx.AsyncClient() as client:
        res = await client.get("https://sg-sg-sg.astro.com.my:9443/oauth2/authorize", headers=headers, params=params, follow_redirects=False)
    location = res.headers.get("Location")
    parsed = urllib.parse.urlparse(location)
    fragment = parsed.fragment
    params = {}
    for item in fragment.split("&"):
        if "=" in item:
            key, value = item.split("=", 1)
            params[key] = value
    access_token = params.get("access_token")
    return access_token


async def get_epgs_astro(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    starttime = datetime.datetime.combine(dt, datetime.time.min).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8))).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    access_token = await astro_get_access_token()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
        "Referer": "https://astrogo.astro.com.my/",
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "zh"
    }
    params = {
        "startDateTime": starttime,
        "channelId": channel_id0,
        "limit": 1,
        "genreId": "",
        "isPlayable": "true",
        "duration": "24",
        "clientToken": "v:1!r:80800!ur:GUEST_REGION!community:Malaysia%20Live!t:k!dt:PC!f:Astro_unmanaged!pd:CHROME-FF!pt:Adults"
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get("https://sg-sg-sg.astro.com.my:9443/ctap/r1.6.0/shared/grid", headers=headers, params=params)
        res.encoding = 'utf-8'
        data = res.json()
        for channel in data.get("channels"):
            schedules = channel.get("schedule", [])
            for schedule in schedules:
                title = schedule.get('title', '')
                description = schedule.get('synopsis', '')
                episode_number = schedule.get("episodeNumber")
                if episode_number:
                    title += f" Ep{episode_number}"
                parentalRating = schedule.get("parentalRating", {}).get("name")
                if parentalRating:
                    title += f"[{parentalRating}]"
                start_time = datetime.datetime.fromisoformat(schedule.get('startDateTime').replace('Z', '+00:00')).astimezone(pytz.timezone('Asia/Shanghai'))
                end_time = start_time + datetime.timedelta(seconds=schedule.get("duration"))
                epg = {
                    'channel_id': channel_id,
                    'starttime': start_time,
                    'endtime': end_time,
                    'title': title,
                    'desc': description
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
        'ban': 0
    }
    return ret


async def get_channels_astro():
    channels = []
    access_token = await astro_get_access_token()
    params = {
        "clientToken": "v:1!r:80800!ur:GUEST_REGION!community:Malaysia%20Live!t:k!dt:PC!f:Astro_unmanaged!pd:CHROME-FF!pt:Adults"
    }
    headers = {
        "Referer": "https://astrogo.astro.com.my/",
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "zh"
    }
    async with httpx.AsyncClient() as client:
            res = await client.get("https://sg-sg-sg.astro.com.my:9443/ctap/r1.6.0/shared/channels", params=params, headers=headers)
    res.encoding = 'utf-8'
    data = res.json()
    for channel in data.get("channels", []):
        logicalChannelNumber = channel.get("logicalChannelNumber", "")
        name = channel.get("name", "").strip()
        id = str(channel.get("id", ""))
        channel = {
            'id': f'astro_{logicalChannelNumber}',
            'name': name,
            'id0': id,
            'source': 'astro'
        }
        channels.append(channel)
        print(channel)
    return channels

# asyncio.run(get_channels_astro())
# asyncio.run(get_epgs_astro({'id': 'astro_393', 'name': 'ONE HD', 'id0': '2702', 'source': 'astro'}, dt=datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=1)))
