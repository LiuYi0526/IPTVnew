import httpx
import datetime
import os
from bs4 import BeautifulSoup

async def get_epgs_RTHK(channel, dt):
    epgs = []
    msg = ''
    success = 1
    channel_id = channel['id']
    channel_id0 = channel['id0']
    url = f'https://www.rthk.hk/timetable/{channel_id0}'
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        for i in soup.find_all('div', class_='slideBlock'):
            date_str = i.get('date')
            if date_str and date_str == dt.strftime("%Y%m%d"):
                # Parse date
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                # Find all programs for this date
                for program_block in i.find_all('div', class_='shdBlock'):
                    time_block = program_block.find('div', class_='shTimeBlock')
                    time_elements = time_block.find_all('p', class_='timeDis')
                    start_time_str = time_elements[0].text.strip()
                    end_time_str = time_elements[2].text.strip() if len(time_elements) > 2 else None
                    # Parse start time
                    start_hour, start_min = map(int, start_time_str.split(':'))
                    start_datetime = datetime.datetime(year, month, day, start_hour, start_min)
                    # Parse end time
                    end_hour, end_min = map(int, end_time_str.split(':'))
                    end_datetime = datetime.datetime(year, month, day, end_hour, end_min)
                    # Handle day crossing
                    if end_hour < start_hour or (end_hour == start_hour and end_min < start_min):
                        end_datetime += datetime.timedelta(days=1)

                    # Get program title
                    title_block = program_block.find('div', class_='shTitle')
                    title = title_block.find('a').text.strip()
                    if title_block.find('img', alt="重播節目"):
                        title += '[重播]'
                    if title_block.find('img', alt="英文節目"):
                        title += '[英]'
                    if title_block.find('img', alt="家長指引"):
                        title += '[PG]'
                    if title_block.find('img', alt="成年觀眾"):
                        title += '[M]'
                    # Get program description
                    sub_title_block = program_block.find('div', class_='shSubTitle')
                    description = ""
                    if sub_title_block and sub_title_block.find('a'):
                        description = sub_title_block.find('a').text.strip()
                    epg = {
                        'channel_id': channel_id,
                        'starttime': start_datetime,
                        'endtime': end_datetime,
                        'title': title,
                        'desc': description
                    }
                    epgs.append(epg)
                    # print(epg)
    except Exception as e:
        success = 0
        spidername = os.path.basename(__file__).split('.')[0]
        msg = 'spider-%s-%s' % (channel_id, e)
    ret = {
        'success': success,
        'epgs': epgs[::-1],
        'msg': msg,
        'last_program_date': dt,
        'ban': 0,
    }
    return ret

# await get_epgs_RTHK({'name': '港台電視 31', 'id': 'RTHK_tv31', 'id0': 'tv31', 'source': 'RTHK'}, dt=datetime.datetime.now())
