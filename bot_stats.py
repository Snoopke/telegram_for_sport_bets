import os
import time
import json
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


def get_referral():
    """Generates referral link from php script"""
    url = 'http://127.0.0.1:84/api.php'
    return requests.get(url).json()['work'] + 'L?tag=s_315357m_1107c_%26site=315357%26ad=1107'


def match_info(i):
    """Sends announcement about next game in MK10"""
    game_id = str(data[i]['I'])
    global actual_link_for_results
    actual_link_for_results = data[i]['U'][12:18]
    rekv = requests.get('https://one-' + actual_link_for_results +
                        '.world/LiveFeed/GetGameZip?id=' + game_id + '&lng=ru')
    coef = rekv.json()
    game = 'Mortal Kombat X'
    starting_time = str(time.strftime("%Y.%m.%d %H:%M", time.localtime(int(data[i]['D'][6:-5]))))
    if data[i]['A'] == "Ди'Вора":
        data[i]['A'] = "ДиВора"
    elif data[i]['A'] == "Саб-Зиро":
        data[i]['A'] = "СабЗиро"
    elif data[i]['H'] == "Ди'Вора":
        data[i]['H'] = "ДиВора"
    elif data[i]['H'] == "Саб-Зиро":
        data[i]['H'] = "СабЗиро"

    hashtag_first_line = '%20%23' + str('_'.join(data[i]['H'].split())) + \
                         ' ' + '%20%23' + str('_'.join(data[i]['A'].split()))

    hashtag_second_line = '%20%23' + ''.join(data[i]['H'].split()) + \
                          '_' + ''.join(data[i]['A'].split())

    main_coefs = 'П1' + '(' + (str(coef['Value']['E'][0]['C'])) + ') - ' + \
                 'П2(' + (str(coef['Value']['E'][1]['C'])) + ')'

    if coef['Value']['E'][2]['C'] < 11:
        fbr_coefs = 'F(' + (str(coef['Value']['E'][2]['C'])) + ') B(' + \
                    (str(coef['Value']['E'][5]['C'])) + ') R(' + \
                    (str(coef['Value']['E'][6]['C'])) + ')'
    else:
        fbr_coefs = 'F(' + (str(coef['Value']['E'][3]['C'])) + ') B(' + \
                    (str(coef['Value']['E'][6]['C'])) + ') R(' + \
                    (str(coef['Value']['E'][7]['C'])) + ')'

    time_stamps = str(round((coef['Value']['E'][8]['P'] - 100) * 100, 2)) + '/' + \
                  str(round((coef['Value']['E'][10]['P'] - 100) * 100, 2)) + '/' + \
                  str(round((coef['Value']['E'][12]['P'] - 100) * 100, 2))

    promo = 'Ставим тут ' + get_referral() + '\nБонус до 9100р, промокод на бонус [MORTAL10]'

    with open(game_id + '.txt', 'w', encoding='utf-8') as file:
        file.writelines('{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(game, starting_time, hashtag_first_line,
                                                                hashtag_second_line, main_coefs, fbr_coefs, time_stamps,
                                                                promo))

    return '{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}'.format(game, starting_time, hashtag_first_line,
                                                   hashtag_second_line, main_coefs, fbr_coefs, time_stamps, promo)


########################################################################################################################


def results(game):
    """Sends result of ended matches into tg channel"""

    rekv = requests.get('https://one-' + actual_link_for_results +
                        '.world/LiveFeed/GetGameZip?id=' + str(game) + '&lng=ru')
    coef = rekv.json()

    player_1 = coef['Value']['O1']
    player_2 = coef['Value']['O2']
    if len(coef['Value']['SC']['FS']) == 2:
        total_score = str(coef['Value']['SC']['FS']['S1']) + ':' + str(coef['Value']['SC']['FS']['S2'])
    else:
        if 'S1' in coef['Value']['SC']['FS']:
            total_score = str(coef['Value']['SC']['FS']['S1']) + ':0'
        else:
            total_score = '0:' + str(coef['Value']['SC']['FS']['S2'])
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
    res_fbr = ''
    score_first_player = 0
    score_second_player = 0
    first_part_result = ''
    counter = 1
    for i in range(len(ans_2)):
        if ans_2[i][1] in player_1:
            first_part_result += str(counter) + '. ' + 'П1' + '-' + ans_2[i][2][0] + '-' + str(ans_2[i][3]) + '\n'
            counter += 1
        else:
            first_part_result += str(counter) + '. ' + 'П2' + '-' + ans_2[i][2][0] + '-' + str(ans_2[i][3]) + '\n'
            counter += 1
    for i in range(len(ans_2)):
        if ans_2[i][1] in player_1:
            score_first_player += 1
        elif ans_2[i][1] in player_2:
            score_second_player += 1
        res_fbr += str(score_first_player) + ':' + str(score_second_player) + ' ' + ans_2[i][2][0] + '; '
    return '\n' + first_part_result + '\n' + total_score + ' (' + res_fbr + ')' + '\n\n'


#######################################################################################################################


def edit_message(chat_id, message_id, text):
    """Send message into telegram channel"""
    url = URL + "editMessageText?chat_id={}&message_id={}&text={}".format(chat_id, message_id, text)
    return get_url(url)


def combo_results(game):
    """Function contains new text for edited message"""

    with open(str(game) + '.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines.insert(7, results(i))

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
        print('searching for a match...(bot_stats.py)')
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
                    x = send_message(match_info(i), '-1001291060910')
                    x = json.loads(x)
                    awaiting_results[data[i]['I']] = x['result']['message_id']
                except:
                    print('some data is empty')
                print(awaiting_results)
    for i in range(4):
        for i in list(awaiting_results):
            try:
                rekv = requests.get('https://one-' + actual_link_for_results +
                                    '.world/LiveFeed/GetGameZip?id=' + str(i) + '&lng=ru')
                coef = rekv.json()
                if 'CPS' in coef['Value']['SC']:
                    if coef['Value']['SC']['CPS'] == 'Игра завершена':
                        print('\n!!!Игра завершена!!!\n')
                        print(results(i))
                        try:
                            print(edit_message('-1001291060910', awaiting_results[i], combo_results(i)))
                        except KeyError as e:
                            print('Нет ключа')
                        except IndexError as j:
                            print('empty E in coef')
                        awaiting_results.pop(i)
                        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), str(i) + '.txt')
                        os.remove(path)
                        print(awaiting_results)
                    else:
                        try:
                            print(edit_message('-1001291060910', awaiting_results[i], combo_results(i)))
                        except KeyError as e:
                            print('Нет ключа')
                        except IndexError as j:
                            print('empty E in coef')
            except:
                print('Error in searching results')

        time.sleep(50)
    time.sleep(58)
