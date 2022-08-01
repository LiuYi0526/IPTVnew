import requests
i = 1
j = 1
str = "#EXTM3U"
while i <= 20:
    url = f'https://live-play.cctvnews.cctv.com/cctv/merge{i}.m3u8'
    html = requests.get(url).text
    if str in html:
        with open(f'cctvnewslivemerge{j}.m3u8', "w") as file:
            file.write("#EXTM3U\n")
            file.write("#EXT-X-VERSION:3\n")
            file.write("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2560000\n")
            file.write(url)
        j =j + 1
    i = i + 1
i = 1
j = 1
while i <= 20:
    url = f'https://live-play.cctvnews.cctv.com/cctv/newslive_{i}.m3u8'
    html = requests.get(url).text
    if str in html:
        with open(f'cctvnewslive{j}.m3u8', "w") as file:
            file.write("#EXTM3U\n")
            file.write("#EXT-X-VERSION:3\n")
            file.write("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2560000\n")
            file.write(url)
        j =j + 1
    i = i + 1
