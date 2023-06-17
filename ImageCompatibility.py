import requests


def main_task(path):
    compatible_arch = []
    compatible_os = []
    url = "https://hub.docker.com/v2/repositories/"+path+"/tags/?page_size&page&name&ordering"
    url2 = "https://hub.docker.com/v2/repositories/library/"+path+"/tags/?page_size&page&name&ordering"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7,bn;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': 'docker-id=; OptanonAlertBoxClosed=2023-03-06T12:48:59.945Z; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Mar+06+2023+12%3A58%3A06+GMT%2B0000+(Hora+padr%C3%A3o+da+Europa+Ocidental)&version=202209.1.0&isIABGlobal=false&hosts=&consentId=14da2c77-1be1-429b-8c27-a59bac419a40&interactionCount=1&landingPath=NotLandingPage&groups=C0003%3A0%2CC0001%3A1%2CC0002%3A0%2CC0004%3A0&geolocation=PT%3B13&AwaitingReconsent=false',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    cookies = {
        'docker-id': ''
        }
    response = requests.get(url,cookies=cookies, headers=headers)
    response2 = requests.get(url2,cookies=cookies, headers=headers)
    var = 0
    try:
        if response.status_code == 200:
            print("Trying to proccess method %1")
            var = 1
            page_text = response.text
            #print(page_text)
            architectures = ["arm","amd","386","ppc64le","s390x"]
            os = ["linux","windows"]
            for i in architectures:
                num = page_text.find(i)
                if num > 0 : compatible_arch.append(i)
            for i in os:
                num = page_text.find(i)
                if num > 0 : compatible_os.append(i)
        elif var == 1:
            print('Error:', response.status_code)
    except:
        pass
    try:
        if response2.status_code == 200 and var == 0:
            print("Trying to proccess method %2, method%1 failed")
            page_text = response2.text
            #print(page_text)
            architectures = ["386","arm","amd","ppc64le","s390x"]
            os = ["linux","windows"]
            for i in architectures:
                num = page_text.find(i)
                if num > 0 : compatible_arch.append(i)
            for i in os:
                num = page_text.find(i)
                if num > 0 : compatible_os.append(i)
        elif var == 0:
            print('Error:', response.status_code)
    except:
        pass
    if "amd" in compatible_arch:
        return "amd"
    if "arm" in compatible_arch:
        return "amd"
    return compatible_arch
