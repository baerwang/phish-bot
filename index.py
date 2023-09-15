# -*- coding: utf-8 -*-

import datetime
import requests
import json
import os
import random
from zhdate import ZhDate as lunar_date

WEBHOOK = os.environ.get('WECHATWORK_WEBHOOK')

card_images = ['https://i.loli.net/2021/05/31/nPFamUTbi3KNovZ.png', 'https://i.loli.net/2020/11/18/3zogEraBFtOm5nI.jpg',
               'https://i.loli.net/2021/07/10/1hx68db4muqfWaB.png']


def get_week_day(date):
    week_day_dict = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    day = date.weekday()
    return week_day_dict[day]


def time_parse(today):
    # 距离大年
    distance_big_year = calculate_distance(today=today, m=1, d=1, lunar=True)
    # 距离元宵
    distance_1_15 = calculate_distance(today=today, m=1, d=15, lunar=True)
    # 距离端午
    distance_5_5 = calculate_distance(today=today, m=5, d=5, lunar=True)
    # 距离中元
    distance_7_15 = calculate_distance(today=today, m=7, d=15, lunar=True)
    # 距离中秋
    distance_8_15 = calculate_distance(today=today, m=8, d=15, lunar=True)
    # 距离重阳
    distance_9_9 = calculate_distance(today=today, m=9, d=9, lunar=True)

    # 距离元旦
    distance_year = calculate_distance(today=today, m='01', d='01')
    # 距离妇女
    distance_3_8 = calculate_distance(today=today, m='03', d='08')
    # 距离清明
    distance_4_5 = calculate_distance(today=today, m='04', d='05')
    # 距离劳动节
    distance_5_1 = calculate_distance(today=today, m='05', d='01')
    # 距离儿童节
    distance_6_1 = calculate_distance(today=today, m='06', d='01')
    # 距离国庆节
    distance_10_1 = calculate_distance(today=today, m='10', d='01')
    # 距离圣诞节
    distance_12_25 = calculate_distance(today=today, m='12', d='25')

    time_ = [
        {
            "v": distance_year,
            "emoji": "🎉",
            "title": "元旦节"
        },
        {
            "v": distance_big_year,
            "emoji": "🧧",
            "title": "过春节"
        },
        {
            "v": distance_1_15,
            "emoji": "🥟",
            "title": "元宵节"
        },
        {
            "v": distance_3_8,
            "emoji": "💰",
            "title": "富女节"
        },
        {
            "v": distance_4_5,
            "emoji": "😔",
            "title": "清明节"
        },
        {
            "v": distance_5_1,
            "emoji": "🧑‍💻",
            "title": "劳动节"
        },
        {
            "v": distance_5_5,
            "emoji": "🐲🛶",
            "title": "端午节"
        },
        {
            "v": distance_6_1,
            "emoji": "🍭",
            "title": "巨婴节"
        },
        {
            "v": distance_7_15,
            "emoji": "👻",
            "title": "中元节"
        },
        {
            "v": distance_8_15,
            "emoji": "🎑",
            "title": "中秋节"
        },
        {
            "v": distance_9_9,
            "emoji": "☀️",
            "title": "重阳节"
        },
        {
            "v": distance_10_1,
            "emoji": "🇨🇳",
            "title": "国庆节"
        },
        {
            "v": distance_12_25,
            "emoji": "🎅🏼",
            "title": "圣诞节"
        },
    ]

    # 企业微信卡片只支持显示6个，所以移除距离较远的多余节日
    time_ = sorted(time_, key=lambda x: x['v'], reverse=False)
    while len(time_) > 5:
        time_.pop()
    return time_


def calculate_distance(today, m, d, lunar=False):
    if lunar:
        distance = (lunar_date(today.year, m, d).to_datetime().date() -
                    today).days
        distance = distance if distance > 0 else (
                lunar_date(today.year + 1, m, d).to_datetime().date() - today).days
    else:
        distance = (datetime.datetime.strptime("{}-{}-{}".format(today.year, m, d), "%Y-%m-%d").date() - today).days
        distance = distance if distance > 0 else (
                datetime.datetime.strptime("{}-{}-{}".format(today.year + 1, m, d), "%Y-%m-%d").date() - today).days
    return distance


def get_one_text():
    # 文档 https://gushi.ci/ 和 https://www.jinrishici.com/

    send_url = "https://v1.jinrishici.com/all.json"
    headers = {"Content-Type": "text/plain"}
    res = requests.post(url=send_url, headers=headers)

    return json.loads(res.text).get('content')


def get_weather():
    send_url = "http://aider.meizu.com/app/weather/listWeather?cityIds=101020100"
    res = requests.post(url=send_url)
    context = json.loads(res.text).get('value')[0]
    weather = context.get('indexes')
    return {"recommend": random_weather(weather), "realtime": context.get('realtime'),
            "weathers": context.get("weathers")}


def random_weather(weather):
    w = weather[random.randint(0, len(weather) - 1)]
    content = w.get('content')
    if content == "":
        return random_weather(weather)
    return w


def get_wages(today):
    month = today.month + 1
    if today.day == 15:
        return 0
    elif not today.day > 15:
        month = today.month
    return calculate_distance(today=datetime.date.today(), m=month, d='15')


def get_work():
    current_time = datetime.datetime.now()
    closing_time = current_time.replace(hour=18, minute=30, second=0, microsecond=0)
    time_difference = closing_time - current_time
    hours_until_closing = time_difference.seconds // 3600
    minutes_until_closing = (time_difference.seconds % 3600) // 60
    seconds_until_closing = time_difference.seconds % 60
    return "{}小时{}分钟{}秒".format(hours_until_closing, minutes_until_closing, seconds_until_closing)


def work_expire(realtime, w):
    title = "🚇距离下班时间还有:"
    desc = "{} \n🌡️当前气温 {} ℃\n☁️当前气候 {}\n\n{}".format(get_work(), realtime.get('temp'),
                                                              realtime.get('weather'),
                                                              w.get('recommend').get(
                                                                  'content'))

    if not 14 <= datetime.datetime.now().hour < 19:
        title = "年年今日，灯明如昼；原火不灭，愿人依旧。"
        desc = "{}\n🌡️当前气温 {} ℃\n☁️当前气候 {}\n\n{}".format(get_one_text(), realtime.get('temp'),
                                                                 realtime.get('weather'),
                                                                 w.get('recommend').get('content'))

    return {'title': title, 'desc': desc}


def morning_or_Afternoon(weathers):
    desc = "☀️早上好！\n🍁今天是{} {}\n🌟温度 {}℃ ~ {}℃ {}".format(weathers.get('date'),
                                                                weathers.get('week'),
                                                                weathers.get('temp_night_c'),
                                                                weathers.get('temp_day_c'),
                                                                weathers.get('weather'))

    if 14 <= datetime.datetime.now().hour < 19:
        desc = "☀️下午好!\n🍁今天是{} {}".format(weathers.get('date'), weathers.get('week'))

    return desc


def send_msg():
    today = datetime.date.today()
    time_data = time_parse(today)
    one_text = get_one_text()
    w = get_weather()

    weathers = w.get('weathers')[0]
    expire = work_expire(w.get('realtime'), w)

    wages = get_wages(today)
    states = []

    if wages == 0:
        states.append({"keyname": "💰发工资了💰", "value": "🤑💵"})
    else:
        states.append({"keyname": "💰距离发工资", "value": "还有{}天".format(wages)})

    for item in time_data:
        keyname = "{}距离{}".format(item['emoji'], item['title'])
        value = "还有{}天".format(item['v'])
        states.append({"keyname": keyname, "value": value})

    headers = {"Content-Type": "text/plain"}
    send_url = WEBHOOK

    send_data = {
        "msgtype": "template_card",
        "template_card": {
            "card_type":
                "news_notice",
            "main_title": {
                "title": "浮世三千",
                "desc": morning_or_Afternoon(weathers)
                ,
            },
            "card_image": {
                "url": card_images[random.randint(0, len(card_images) - 1)],
            },
            "vertical_content_list": [{
                "title": expire.get("title"),
                "desc": "\n" + expire.get("desc") + "\n"
            }],
            "horizontal_content_list":
                states,
            "card_action": {
                "type": 1,
                "url": "https://so.gushiwen.cn/search.aspx?value=" + one_text + "&valuej=" + one_text[0],
                "appid": "APPID",
                "pagepath": "PAGEPATH"
            }
        }
    }

    res = requests.post(url=send_url, headers=headers, json=send_data)
    print(res.text)


def main_handler():
    send_msg()


main_handler()
