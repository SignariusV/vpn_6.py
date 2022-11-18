import time
from ppadb.client import Client as AdbClient
# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)
device = client.device("07845371BS000116") # Значение из adb devices



def traffic():
    tr=device.shell('ifconfig tun0')
    return int(tr.split('\n')[-3].strip().split(':')[1].split()[0])

def face_web():
    '''Функция для отработки web-версии Facebook'''
    tr_0=traffic()
    device.shell('am start -a android.intent.action.VIEW http:/m.facebook.com')  # открытие страницы Facebook в Яндекс браузере
    print('Открытие Facebook web-версия')
    input('Если приложение загрузилось нажмите ENTER:') # Ожидание загрузки
    device.input_keyevent(4)
    tr_end=traffic()
    print(f'Закрытие вкладки Facebook: трафик {tr_end-tr_0}')
    result[0]=True


def insta_web():
    '''Функция для отработки web-версии Instagram'''
    device.shell('am start -a android.intent.action.VIEW http:/instagram.com')  # открытие страницы Instagram в Яндекс браузере
    print('Открытие Instagram web-версия')
    input('Если приложение загрузилось нажмите ENTER:') # Ожидание загрузки
    device.input_keyevent(4)
    print('Закрытие вкладки Instagram')
    result[1] = True


def face_app():
    '''Функция для отработки приложения Facebook'''
    time.sleep(0.5)
    device.shell('am start -n com.facebook.katana/.LoginActivity')  # открытие приложения Facebook
    print('Открытие Facebook приложения')
    input('Если приложение загрузилось нажмите ENTER:') # Ожидание загрузки
    device.input_keyevent(187)
    print('Закрытие приложения Facebook')
    device.input_swipe(660,1200,660,100,500)
    time.sleep(0.5)
    result[2] = True


def insta_app():
    '''Функция для отработки приложения Instagram'''
    time.sleep(0.5)
    device.shell('am start -n com.instagram.android/com.instagram.mainactivity.MainActivity')  # открытие приложения Instagram
    print('Открытие Instagram приложения')
    input('Если приложение загрузилось нажмите ENTER:') # Ожидание загрузки
    device.input_keyevent(187)
    print('Закрытие приложения Instagram')
    device.input_swipe(660,1200,660,100,500)
    time.sleep(0.5)
    result[3] = True


def close_vpn():
    '''Функция закрытия и выгрузки VPN'''
    device.input_tap(350,700) # Тапаем, чтобы он появился в списке последних
    time.sleep(1)
    device.input_keyevent(187)
    time.sleep(1)
    device.input_swipe([350,660][is_work], 1200, [350,660][is_work], 100, 500) # Выгружаем  VPN из трея
    time.sleep(1)
    device.shell('am start -n com.android.settings/.Settings') # Открываем настройки
    time.sleep(2)
    device.input_tap(350,600) # Нажимаем кнопку Приложения и уведомления
    time.sleep(4)
    device.input_tap(350,420) # Нажимаем на работающее приложение VPN
    time.sleep(3)
    device.input_tap(595,520) # Выбираем остановить
    time.sleep(0.5)
    device.input_tap(580,945) # Подтверждение OK
    time.sleep(0.5)
    device.input_keyevent(187)
    time.sleep(0.5)
    device.input_swipe([350,660][is_work], 1200, [350,660][is_work], 100, 500) # Выгружаем меню настроек
    time.sleep(0.5)
    print('VPN приложение остановленно и выгруженно')


def open_testing():
    device.shell('am start -a android.intent.action.VIEW http:/testing-niir.ru')
    time.sleep(5) # Ожидание загрузки агрегатора
    device.input_tap(450,345) # Тестирование
    print('Открытие вкладки агрегатора результатов тестирования')
    time.sleep(3)
    if grup:
        device.input_tap([105,325,545][grup],675)
        time.sleep(2)
    device.input_swipe(700,1300,700,150,1000)
    time.sleep(0.5)

def input_result():
    y=1100
    for res in result:
        if res:
            device.input_tap(115,y)
        y+=100
    input('Подтвердите результат:')
    device.input_tap(180,1500)
    # Закрытие страницы и выгрузка браузера
    time.sleep(3)
    device.input_tap(500,1560)
    time.sleep(1)
    device.input_swipe(100,1400,700,1400,500)
    device.input_keyevent(187)
    device.input_swipe(350, 1200, 350, 100, 500)




is_work=False
grup=0
result=[False,False,False,False]
if not input('VPN работает?'):
    is_work=True
    face_web()
    insta_web()
    face_app()
    insta_app()
close_vpn()
open_testing()
input_result()
















