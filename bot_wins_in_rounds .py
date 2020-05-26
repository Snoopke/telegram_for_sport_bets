import os
import time
import json
import random
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


def get_referral():
    """Generates referral link from php script"""
    url = 'http://127.0.0.1:84/api.php'
    return requests.get(url).json()['work'] + 'L?tag=s_315357m_1107c_%26site=315357%26ad=1107'


def match_info(i):
    """Sends announcement about next game in MK10"""
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
    second_line = 'Прогноз - ' + random.choice(['П1 в раунде', 'П2 в раунде'])
    result = '☠Результат - '
    fourth_line = ''

    if 'П1' in second_line:
        if 1.7 < coef['Value']['E'][0]['C'] < 2.9 and 1.7 < coef['Value']['E'][1]['C'] < 2.9:
            fourth_line = 'Коэффициент - ' + str(coef['Value']['E'][0]['C'])
        else:
            return ''
    elif 'П2' in second_line:
        if 1.7 < coef['Value']['E'][0]['C'] < 2.9 and 1.7 < coef['Value']['E'][1]['C'] < 2.9:
            fourth_line = 'Коэффициент - ' + str(coef['Value']['E'][1]['C'])
        else:
            return ''

    promo = 'Ставим тут ' + get_referral() + '\nБонус до 9100р, промокод на бонус [MORTAL10]'

    with open('wins' + game_id + '.txt', 'w', encoding='utf-8') as file:
        file.writelines('{}\n{}\n{}\n{}\n{}'.format(first_line, second_line, result, fourth_line, promo))

    return '{}\n{}\n{}\n{}\n{}'.format(first_line, second_line, result, fourth_line, promo)


def results(game):
    """Sends result of ended matches into tg channel"""
    rekv = requests.get('https://one-' + actual_link_to_xbet + '.world/LiveFeed/GetGameZip?id=' + str(game) + '&lng=ru')
    coef = rekv.json()

    with open('wins' + str(game) + '.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        winner = lines[1][11]
        if winner == '1':
            if 'S1' in coef['Value']['SC']['FS'] and 'S2' not in coef['Value']['SC']['FS']:
                return '1 раунд' + ' ✅ '
            elif 'S1' in coef['Value']['SC']['FS'] and 'S2' in coef['Value']['SC']['FS']:
                return str(coef['Value']['SC']['FS']['S1'] + coef['Value']['SC']['FS']['S2']) + ' раунд' + ' ✅ '
        else:
            if 'S2' in coef['Value']['SC']['FS'] and 'S1' not in coef['Value']['SC']['FS']:
                return '1 раунд' + ' ✅ '
            elif 'S2' in coef['Value']['SC']['FS'] and 'S1' in coef['Value']['SC']['FS']:
                return str(coef['Value']['SC']['FS']['S1'] + coef['Value']['SC']['FS']['S2']) + ' раунд' + ' ✅ '

    return ''


def edit_message(chat_id, message_id, text):
    """Send message into telegram channel"""
    url = URL + "editMessageText?chat_id={}&message_id={}&text={}".format(chat_id, message_id, text)
    return get_url(url)


def combo_results(game):
    """Function contains new text for edited message"""

    with open('wins' + str(game) + '.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines[2] = '☠Результат - ' + results(game) + '\n'

    return ''.join(lines)


def match_checker(data):
    for i in range(len(data)):
        if 'Mortal Kombat X' in data[i]['C'] and (round((int(data[i]['D'][6:-5]) - time.time()) / 60, 2) >= 4):
            return data
        else:
            continue
    return False


awaiting_results = {}

while True:
    global data
    for i in range(10):
        req = requests.get(XBET)
        if req.status_code == 200:
            data = req.json()
            break
        else:
            time.sleep(1)

    while not match_checker(data):
        print('searching for a match...(bot_wins.py)')
        time.sleep(4)
        for i in range(10):
            try:
                req = requests.get(XBET)
                if req.status_code == 200:
                    data = req.json()
                    break
                else:
                    time.sleep(1)
            except:
                continue
    else:
        for i in range(len(data)):
            if 'Mortal Kombat X' in data[i]['C'] and (round((int(data[i]['D'][6:-5]) - time.time()) / 60, 2) >= 4):
                try:
                    x = send_message(str(match_info(i)), '-1001305018894')
                    x = json.loads(x)
                    awaiting_results[data[i]['I']] = x['result']['message_id']
                except KeyError:
                    print('some data is empty')
                except json.JSONDecodeError:
                    print('empty json')
                print(awaiting_results)
    for i in range(8):
        for i in list(awaiting_results):
            try:
                rekv = requests.get('https://one-' + actual_link_to_xbet +
                                    '.world/LiveFeed/GetGameZip?id=' + str(i) + '&lng=ru')
                coef = rekv.json()
                if results(i) != '':
                    try:
                        print(edit_message('-1001305018894', awaiting_results[i], combo_results(i)))
                    except KeyError as e:
                        print('Нет ключа')
                    except IndexError as j:
                        print('empty E in coef')
                    awaiting_results.pop(i)
                    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'wins' + str(i) + '.txt')
                    os.remove(path)
                    print(awaiting_results)
                elif 'CPS' in coef['Value']['SC']:
                    if coef['Value']['SC']['CPS'] == 'Игра завершена':
                        print('\n!!!Игра завершена!!!\n')
                        try:
                            with open('wins' + str(i) + '.txt', 'r', encoding='utf-8') as file:
                                lines = file.readlines()
                                lines[2] = 'Результат - X' + '\n'
                            print(edit_message('-1001305018894', awaiting_results[i], ''.join(lines)))
                        except KeyError as e:
                            print('Нет ключа')
                        except IndexError as j:
                            print('empty E in coef')
                        awaiting_results.pop(i)
                        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'wins' + str(i) + '.txt')
                        os.remove(path)
                        print(awaiting_results)
                    else:
                        try:
                            print(edit_message('-1001305018894', awaiting_results[i], combo_results(i)))
                        except KeyError as e:
                            print('Нет ключа')
                        except IndexError as j:
                            print('empty E in coef')
            except:
                print('Error in searching results')

        time.sleep(25)
    time.sleep(45)
