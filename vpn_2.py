import time
import random
from PIL import ImageChops
from PIL import Image
import math, operator
import functools
from ppadb.client import Client as AdbClient

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)
device = client.device("07845371BS000116")  # Значение из adb devices


# result = device.screencap()
# with open("problem_1.png", "wb") as fp:
#     fp.write(result)

def screen(path):
    '''Скриншот экрана и сохраняет по имени'''
    result = device.screencap()
    with open(f"{path}", "wb") as fp:
        fp.write(result)


def rmsdiff(path_one, path_two, box=(0, 0, 720, 1612)):
    "Calculate the root-mean-square difference between two images"
    im1 = Image.open(path_one).crop(box)
    try:
        im2 = Image.open(path_two).crop(box)
    except:
        time.sleep(1)
        screen(path_two)
        im2 = Image.open(path_two).crop(box)
    h = ImageChops.difference(im1, im2).histogram()
    # calculate rms
    return math.sqrt(functools.reduce(operator.add,
                                      map(lambda h, i: h * (i ** 2), h, range(256))
                                      ) / (float(im1.size[0]) * im1.size[1]))


def traffic():
    tr = device.shell('ifconfig tun0')
    if tr == 'ifconfig: tun0: No such device\n':
        tr = device.shell('ifconfig tun1')
    try:
        res = int(tr.split('\n')[-3].strip().split(':')[1].split()[0])
    except:
        res = 0
    return res


def face_web():
    '''Функция для отработки web-версии Facebook'''
    t_0 = time.time()
    tr_0 = traffic()
    device.shell(
        'am start -a android.intent.action.VIEW http:/m.facebook.com')  # открытие страницы Facebook в Яндекс браузере
    print('Открытие Facebook web-версия')
    while (time.time() - t_0) < 60:
        screen('screen.png')
        if (recog := rmsdiff('face_web.png', 'screen.png', (0, 70, 720, 230))) > 30 and (time.time() - t_0) < 30:
            print(f"Facebook-web время: {time.time() - t_0}, трафик: {traffic() - tr_0}, распознование: {recog}")
            continue
        elif (traffic() - tr_0) > 400000:
            result[0] = True
            print('Facebook web-версия успешно загруженно')
            break
        elif (time.time() - t_0) > 30 and (traffic() - tr_0) < 200000:
            print('Facebook web-версия не загруженно')
            break
    device.input_keyevent(4)
    print(f'Закрытие вкладки Facebook: трафик {traffic() - tr_0} за время {time.time() - t_0}')
    time.sleep(0.5)


def insta_web():
    '''Функция для отработки web-версии Instagram'''
    t_0 = time.time()
    tr_0 = traffic()
    device.shell(
        'am start -a android.intent.action.VIEW http:/instagram.com')  # открытие страницы Instagram в Яндекс браузере
    print('Открытие Instagram web-версия')
    while (time.time() - t_0) < 60:
        screen('screen.png')
        if (recog := rmsdiff('insta_web.png', 'screen.png', box=(0, 1310, 720, 1525))) > 30 and (
                time.time() - t_0) < 30:
            print(f"Instagram-web время: {time.time() - t_0}, трафик: {traffic() - tr_0}, распознование: {recog}")
            continue
        elif (traffic() - tr_0) > 600000:
            result[1] = True
            print('Instagram web-версия успешно загруженно')
            time.sleep(2)
            break
        elif (time.time() - t_0) > 30 and (traffic() - tr_0) < 200000:
            print('Instagram web-версия не загруженно')
            break
    device.input_keyevent(4)
    print(f'Закрытие вкладки Instagram: трафик {traffic() - tr_0} за время {time.time() - t_0}')
    time.sleep(0.5)


def face_app():
    '''Функция для отработки приложения Facebook'''
    t_0 = time.time()
    tr_0 = traffic()
    device.shell('am start -n com.facebook.katana/.LoginActivity')  # открытие приложения Facebook
    print('Открытие Facebook приложения')
    time.sleep(3)
    device.input_tap(660, 225)
    while True:
        screen('screen.png')
        if (recog := rmsdiff('face_app_1.png', 'screen.png')) < 40:
            break
        print(
            f"Facebook-app время: {time.time() - t_0}, трафик: {traffic() - tr_0}, распознование первого элемента: {recog}")
    device.input_tap(565, 222)
    while (time.time() - t_0) < 30:
        screen('screen.png')
        if (recog := rmsdiff('face_app_2.png', 'screen.png')) < 40:
            result[2] = True
            print('Приложение успешно загруженно')
            time.sleep(1)
            break
        print(
            f"Facebook-app время: {time.time() - t_0}, трафик: {traffic() - tr_0}, распознование второго элемента: {recog}")
    device.input_keyevent(187)
    device.input_swipe(660, 1200, 660, 100, 500)
    print(f'Закрытие приложения Facebook: трафик {traffic() - tr_0} за время {time.time() - t_0}')
    time.sleep(0.5)


def insta_app():
    '''Функция для отработки приложения Instagram'''
    t_0 = time.time()
    tr_0 = traffic()
    device.shell(
        'am start -n com.instagram.android/com.instagram.mainactivity.MainActivity')  # открытие приложения Instagram
    print('Открытие Instagram приложения')
    time.sleep(4)
    device.input_tap(370, 1560)
    print('Открытие REELS')
    while (time.time() - t_0) < 30:
        screen('screen.png')
        if (recog := rmsdiff('insta_app_2.png', 'screen.png')) > 40:
            result[3] = True
            time.sleep(2)
            break
        print(f"Instagram-app время: {time.time() - t_0}, трафик: {traffic() - tr_0}, распознование: {recog}")
    device.input_keyevent(187)
    print(f'Закрытие приложения Instagram: трафик {traffic() - tr_0} за время {time.time() - t_0}')
    device.input_swipe(660, 1200, 660, 100, 500)


def close_vpn():
    '''Функция закрытия и выгрузки VPN'''
    list_activs = list(map(lambda o: o.package, device.get_top_activities()))
    if 'com.transsion.itel.launcher' in list_activs and len(list_activs) == 2:
        device.input_keyevent(187)
        time.sleep(0.5)
    ind = list_activs.index(vpn.package)
    device.input_swipe([80, 350, 660][ind], 1200, [80, 350, 660][ind], 100, 500)  # Выгружаем VPN из трея
    device.shell(f'am force-stop {vpn.package}')
    print(f'{vpn.package} приложение остановленно и выгруженно')


def open_testing():
    groups = ['http:/testing-niir.ru/testing/work-1',
              'http:/testing-niir.ru/testing/work-2',
              'http:/testing-niir.ru/testing/work-3',
              'http:/testing-niir.ru/testing/problem-1']
    device.shell(f'am start -a android.intent.action.VIEW {groups[group]}')
    while True:
        screen('screen.png')
        if (recog := rmsdiff(['work_1.png', 'work_2.png', 'work_3.png', 'problem_1.png'][group], 'screen.png')) < 12:
            break
        print(f"Распознование страницы агрегатора результатов: {recog}")  # Ожидание загрузки агрегатора
    device.input_tap(600, 200)
    device.shell('input roll 0 22')


def input_result():
    y = 930
    for res in result:
        if res:
            device.input_tap(115, y)  # Простановка галочек в выборе работоспособности
        y += 100
    input('Подтвердите результат:')
    device.input_tap(180, y)  # Нажатие кнопки отправить результат
    # Закрытие страницы и выгрузка браузера
    time.sleep(3)
    device.input_tap(500, 1560)  # Нажатие плюсика, открыть вкладки
    time.sleep(0.5)
    device.input_swipe(100, 1400, 700, 1400, 500)  # Выгрузка страницы агрегатора
    device.input_keyevent(187)
    time.sleep(0.5)
    device.input_swipe(350, 1200, 350, 100, 500)  # Выгрузка Яндекс браузера
    time.sleep(0.5)
    device.shell('service call statusbar 1')  # Открытие-закрытие шторки
    time.sleep(0.5)
    device.shell('service call statusbar 2')
    device.input_keyevent(187)
    device.input_keyevent(187)


def save_vpn(vpn):
    with open(f'group_{group + 1}_slave.txt', mode='a+', encoding='utf-8') as slave:
        print(f'{vpn.package}/{vpn.activity}', file=slave)


def start_vpn():
    with open(f'group_{group + 1}_master.txt') as master, open(f'group_{group + 1}_slave.txt', 'r',
                                                               encoding='utf-8') as slave:
        slave_lst=slave.readlines()
        for vpn in master.readlines():
            print(vpn.strip())
            if vpn not in slave_lst:
                return print(device.shell(f'am start -n {vpn}'))




# while True:
#     if len(device.get_top_activities())==2:
#         print(device.get_top_activities()[1])
#         break
while True:
    group = 3  # Номер группы тестирования VPN-ов +1
    # start_vpn()
    result = [False, False, False, False]  # результат тестирования по каждому Face_web, Insta_web, Face_app, Insta_app
    if not input('VPN работает?'):
        vpn = device.get_top_activities()[-1]
        face_web()
        insta_web()
        face_app()
        insta_app()
    else:
        vpn = device.get_top_activities()[-1]
    close_vpn()
    open_testing()
    input_result()
    save_vpn(vpn)
