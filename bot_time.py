import os
import time
import json
import random
import re
import requests
from config import TOKEN


URL = "https://api.telegram.org/bot{}/".format(TOKEN)
XBET = 'https://part.upnp.xyz/PartLive/GetAllFeedGames?sportid=103&periodid=1'


def get_url(url):
    """Auto transform content in utf8 via requests"""
    response = requests.get(url)
    content = response.content.decode("utf8")
    print(response, url)
    return content


def send_message(text, chat_id):
    """Sends message into telegram channel"""
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    return get_url(url)


def get_refferal():
    url = 'http://127.0.0.1:84/api.php'
    return requests.get(url).json()['work'] + 'L?tag=s_315357m_1107c_%26site=315357%26ad=1107'
###################################################################################################


def match_info(i):
    """Takes info about next game in MK10 and writes it into file"""
    game_id = str(data[i]['I'])
    session = requests.Session()
    global actual_link_to_xbet
    actual_link_to_xbet = data[i]['U'][12:18]
    rekv = session.get('https://one-' + actual_link_to_xbet + '.world/LiveFeed/GetGameZip?id=' + game_id + '&lng=ru')
    coef = rekv.json()

    if data[i]['A'] == "Ди'Вора":
        data[i]['A'] = "ДиВора"
    elif data[i]['A'] == "Саб-Зиро":
        data[i]['A'] = "СабЗиро"
    elif data[i]['H'] == "Ди'Вора":
        data[i]['H'] = "ДиВора"
    elif data[i]['H'] == "Саб-Зиро":
        data[i]['H'] = "СабЗиро"

    first_line = u'\U0001F432' + data[i]['H'] + ' vs ' + data[i]['A'] + u'\U0001F432'

    second_line = 'Прогноз - ' + str(round((coef['Value']['E'][10]['P'] - 100) * 100, 2))\
                  + random.choice(['Б', 'М'])

    result = '☠Результат - '

    fourth_line = ''

    if 1.7 < coef['Value']['E'][0]['C'] < 2.9 and 1.7 < coef['Value']['E'][1]['C'] < 2.9:
        if 'Б' in second_line:
            fourth_line = 'Коэффициент - ' + str(coef['Value']['E'][10]['C'])
        elif 'М' in second_line:
            fourth_line = 'Коэффициент - ' + str(coef['Value']['E'][11]['C'])
    else:
        return ''

    promo = 'Ставим тут ' + get_refferal() + '\nБонус до 9100р, промокод на бонус [MORTAL10]'

    with open('time' + game_id + '.txt', 'w', encoding='utf-8') as game_info:
        game_info.writelines('{}\n{}\n{}\n{}\n{}'.format(first_line, second_line,
                                                       result, fourth_line, promo))

    return '{}\n{}\n{}\n{}\n{}'.format(first_line, second_line,
                                     result, fourth_line, promo)


###################################################################################################

def results(game):
    """Sends result of ended matches into tg channel"""
    session = requests.Session()
    rekv = session.get('https://one-' + actual_link_to_xbet + '.world/LiveFeed/GetGameZip?id=' + str(game) + '&lng=ru')
    coef = rekv.json()
    text = (coef['Value']['SC']['S'][1]['Value']).strip('[]')
    regex = r':([a-zA-z0-9а-яА-я" ]+)'
    res_match = (re.findall(regex, text))
    ans = []
    for i in res_match:
        if i.isdigit():
            ans.append(int(i))
        else:
            ans.append(i[1:-1])
    ans_2 = []
    while len(ans) != 0:
        ans_2.append(ans[0:5])
        ans = ans[5:]
    print(ans_2)
    with open('time' + str(game) + '.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        round_duration = lines[1][14]
        if round_duration == 'Б':
            for i in range(len(ans_2)):
                if int(ans_2[i][3]) > float(lines[1][10:14]):
                    return str(ans_2[i][0]) + ' раунд  ✅ '
        else:
            for i in range(len(ans_2)):
                if int(ans_2[i][3]) < float(lines[1][10:14]):
                    return str(ans_2[i][0]) + ' раунд  ✅ '

    return ''


###################################################################################################


def edit_message(chat_id, message_id, text):
    """Send message into telegram channel"""
    url = URL + "editMessageText?chat_id={}&message_id={}&text={}".format(chat_id, message_id, text)
    return get_url(url)


def combo_results(game):
    """Function contains new text for edited message"""

    with open('time' + str(game) + '.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines[2] = '☠Результат - ' + results(game) + '\n'

    return ''.join(lines)


def match_checker(data):
    for i in range(len(data)):
        if 'Mortal Kombat X' in data[i]['C'] and \
                (round((int(data[i]['D'][6:-5]) - time.time()) / 60, 2) >= 4):
            return data
        continue
    return False


AWAITING_RESULTS = {}

while True:
    data = 0
    for i in range(10):
        req = requests.get(XBET)
        if req.status_code == 200:
            data = req.json()
            break
        time.sleep(1)

    while not match_checker(data):
        print('searching for a match...(bot_time.py)')
        time.sleep(4)
        for i in range(10):
            try:
                req = requests.get(XBET)
                if req.status_code == 200:
                    data = req.json()
                    break
                time.sleep(1)
            except BaseException:
                continue
    else:
        for i in range(len(data)):
            if 'Mortal Kombat X' in data[i]['C'] \
                    and (round((int(data[i]['D'][6:-5]) - time.time()) / 60, 2) >= 4):
                try:
                    x = send_message(match_info(i), '-1001349793498')
                    x = json.loads(x)
                    AWAITING_RESULTS[data[i]['I']] = x['result']['message_id']
                except BaseException:
                    print('some data is empty or 1.7 < coef < 2.9')
                print(AWAITING_RESULTS)
    for i in range(8):
        for i in list(AWAITING_RESULTS):
            try:
                rekv = requests.get('https://one-' + actual_link_to_xbet + '.world/LiveFeed/GetGameZip?id=' +
                                    str(i) + '&lng=ru')
                coef = rekv.json()
                if results(i) != '':
                    try:
                        print(edit_message('-1001349793498', AWAITING_RESULTS[i], combo_results(i)))
                    except KeyError as no_key:
                        print('Нет ключа')
                    except IndexError as wrong_index:
                        print('empty E in coef')
                    AWAITING_RESULTS.pop(i)
                    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                        'time' + str(i) + '.txt')
                    os.remove(path)
                    print(AWAITING_RESULTS)
                elif 'CPS' in coef['Value']['SC']:
                    if coef['Value']['SC']['CPS'] == 'Игра завершена':
                        print('\n!!!Игра завершена!!!\n')
                        try:
                            with open('time' + str(i) + '.txt', 'r', encoding='utf-8') as file:
                                lines = file.readlines()
                                lines[2] = 'Результат - X' + '\n'
                            print(edit_message('-1001349793498', AWAITING_RESULTS[i], ' '.join(lines)))
                        except KeyError as no_key:
                            print('Нет ключа')
                        except IndexError as wrong_index:
                            print('empty E in coef')
                        AWAITING_RESULTS.pop(i)
                        path = os.path.join(os.path.abspath(
                            os.path.dirname(__file__)), 'time' + str(i) + '.txt')
                        os.remove(path)
                        print(AWAITING_RESULTS)
                    else:
                        try:
                            print(edit_message('-1001349793498', AWAITING_RESULTS[i], combo_results(i)))
                        except KeyError as no_key:
                            print('Нет ключа')
                        except IndexError as wrong_index:
                            print('empty E in coef')
            except:
                print('Error in searching results')

        time.sleep(25)
    time.sleep(45)
