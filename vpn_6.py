import time
from threading import Thread
import math, operator
import functools
from PIL import ImageChops
from PIL import Image
from ppadb.client import Client as AdbClient

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)
device = client.device("07845371BS000116")  # Значение из adb devices


def screen(path):
    '''Функция для скринов'''
    with open(f"{path}", "wb") as fp:
        fp.write(device.screencap())


class App:
    def __init__(self, package):
        self.launch = package
        self.package = package.split('/')[0]
        self.activity = package.split('/')[1]
        self.time_0 = 0
        self.traffic_0 = 0
        self.uid = device.get_uid(package)

    def start(self):
        '''Запуск приложения'''
        res = device.shell(f'am start -n {self.package}/{self.activity}')
        self.time_0 = time.time()
        print(f'Запуск приложения {self.package}, со статусом {res}, время {time.time() - self.time_0} с')

    def stop(self):
        '''Останавливает работу всех процессов связанных с данным приложением'''
        res = device.shell(f'am force-stop {self.package}')
        print(f'Остановка процессов приложения {self.package}, со статусом {res}, время {time.time() - self.time_0}')

    def close(self):
        '''Выгрузка приложения из активных'''
        device.input_keyevent(187)
        while self.package in list(map(lambda o: o.package, device.get_top_activities())):
            activity_lst = list(map(lambda o: o.package, device.get_top_activities()))
            activity_lst.remove('com.transsion.itel.launcher')
            print(activity_lst)
            if len(activity_lst)==1:
                ind = 1
            elif len(activity_lst)==0:
                break
            elif len(activity_lst)==2:
                ind=activity_lst.index(self.package)+1
            else:
                ind=activity_lst.index(self.package)
            device.input_swipe([80, 350, 660][ind], 1200, [80, 350, 660][ind], 100, 500)  # Выгружаем VPN из трея


    def traffic(self):
        tr = device.shell('ifconfig tun0')
        if tr == 'ifconfig: tun0: No such device\n':
            tr = device.shell('ifconfig tun1')
        try:
            res = int(tr.split('\n')[-3].strip().split(':')[1].split()[0])
        except:
            res = 0
        return res

    def time(self):
        return time.time() - self.time_0

    def is_similar(self, path, t=10, k=10, box=(0, 0, 720, 1612)):
        t_0 = time.time()
        try:
            while time.time() - t_0 < t:
                with open("screen.png", "wb") as fp:
                    fp.write(device.screencap())
                im1 = Image.open(path).crop(box)
                im2 = Image.open('screen.png').crop(box)
                h = ImageChops.difference(im1, im2).histogram()
                rms = math.sqrt(functools.reduce(operator.add,
                                                 map(lambda h, i: h * (i ** 2), h, range(256))
                                                 ) / (float(im1.size[0]) * im1.size[1]))
                print(rms)
                if rms < k:
                    return True
        except:
            self.is_similar(path, t, k, box)
        return False

    def tap(self, x, y):
        device.shell(f'input tap {x} {y}')

    def roll(self, x, y):
        device.shell(f'input roll {x} {y}')

    def activ(self, commands_list):
        if len(commands_list)>0:
            for command in commands_list:
                print(command)
                exec(command)


class VPN(App):
    '''Класс для запуска и работы с VPN-ами'''

    def __init__(self, package):
        super().__init__(package)
        self.result = [False, False, False, False]
        self.is_work = False


    def work(self):
        def smart_input():
            if not input():
                self.is_work='0'
        th = Thread(target=smart_input, args=())
        th.start()
        while self.time() < 120:
            if self.traffic()>5000:
                self.is_work=True
                break
            elif self.is_work=='0':
                self.is_work=False
                break
            else:
                time.sleep(0.5)


class WEB(App):
    '''Класс для web-версий и работы с web-страницами'''

    def __init__(self, package):
        super().__init__(package)
        self.package = 'com.yandex.browser'

    def start(self):
        '''Запуск приложения'''
        res = device.shell(f'am start -a {self.launch}')
        self.time_0 = time.time()
        print(f'Запуск приложения {self.launch}, со статусом {res}, время {time.time() - self.time_0} с')

    def close_page(self):
        device.input_tap(500, 1560)  # Нажатие плюсика, открыть вкладки
        while True:
            time.sleep(0.2)
            device.input_swipe(100, 1400, 700, 1400, 200)  # Выгрузка страницы агрегатора
            if self.is_similar('page_web.png',t=1, box=(359,1400,361,1612)):
                break



class Group:
    def __init__(self, group=1):
        self.group = group
        with open(f'group_{group}.txt', 'r') as file:
            self.vpn_list = file.readlines()
        with open('iter.txt', 'r') as file:
            self.i = int(file.read().strip()) - 2

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < len(self.vpn_list) - 1:
            self.i += 1
            return self.vpn_list[self.i].strip()
        raise StopIteration

    def save(self):
        with open('iter.txt', 'w') as file:
            file.write(str(self.i + 2))

    def commands(self):
        with open(f'command_{self.group}.txt', 'r') as file:
            commands_all=file.readlines()
            if len(commands_all)>self.i:
                command_line=commands_all[self.i].strip()
                return command_line.split('->')
            return []


# input()
vpn_list = Group(1)
for vpn_name in vpn_list:
    vpn = VPN(vpn_name)
    vpn.start()
    vpn.activ(vpn_list.commands())
    vpn.work()
    if vpn.is_work:
        # FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK
        face = App('com.facebook.katana/.LoginActivity')
        face.start()
        if face.is_similar('face_app_1.png', box=(635, 200, 685, 245)):
            face.tap(660, 225)
            if face.is_similar('face_app_2.png', box=(530, 180, 610, 260)):
                face.tap(570, 222)
                if face.is_similar('face_app_3.png', box=(545, 680, 645, 775)):
                    vpn.result[2] = True
                    print('Приложение Facebook запустилось')
                else:
                    print('Приложение Facebook НЕ запустилось')
        face.close()
        # FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK FACEBOOK

        # INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM
        insta = App('com.instagram.android/com.instagram.mainactivity.MainActivity')
        insta.start()
        if insta.is_similar('insta_app_1.png', box=(330, 1540, 386, 1590)):
            insta.tap(360, 1568)
            while insta.time() < 20:
                if not insta.is_similar('insta_app_2.png', k=20, t=1):
                    print('Приложение Instagram запустилось')
                    vpn.result[3] = True
                    break
            else:
                print('Приложение Instagram не запустилось')
        insta.close()
        # INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM INSTAGRAM

        # FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB
        face_web = WEB('android.intent.action.VIEW http:/m.facebook.com')
        face_web.start()
        if face_web.is_similar('face_web.png', t=30, box=(15, 250, 105, 340)):
            print('Страница Facebook загрузилась')
            vpn.result[0] = True
        else:
            print('Страница Facebook НЕ загрузилась')
        face_web.close_page()
        # FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB FACE_WEB

        # INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB
        insta_web = WEB('android.intent.action.VIEW http:/instagram.com')
        insta_web.start()
        if insta_web.is_similar('insta_web.png', t=30, box=(20, 180, 165, 350)):
            print('Страница Instagram загрузилась')
            vpn.result[1] = True
        else:
            print('Страница Instagram НЕ загрузилась')
        insta_web.close_page()
        # INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB INSTA_WEB

    # CLOSE VPN & SAVE
    vpn.close()
    vpn.stop()
    vpn_list.save()
    # CLOSE VPN & SAVE

    # RESULT
    testing = WEB(
        f"android.intent.action.VIEW {['http:/testing-niir.ru/testing/work-1', 'http:/testing-niir.ru/testing/work-2', 'http:/testing-niir.ru/testing/work-3', 'http:/testing-niir.ru/testing/problem-1'][vpn_list.group - 1]}")
    testing.start()
    if testing.is_similar('work_1.png', t=120, box=(210, 100, 505, 305)):
        testing.tap(600, 200)
        testing.roll(0,22)
        if not testing.is_similar('result_page.png', t=1, box=(100,1290,250,1350)):
            device.input_keyevent(123)
            device.input_swipe(350, 100, 350, 1080, 500)
        y = 930
        for res in vpn.result:
            if res:
                testing.tap(115, y)  # Простановка галочек в выборе работоспособности
            y += 100
        testing.tap(180, y)  # Нажатие кнопки отправить результат
    if testing.is_similar('work_2.png', t=120, box=(165, 635, 555, 710)):
        testing.close_page()
        testing.close()
        device.shell('service call statusbar 1')  # Открытие-закрытие шторки
        time.sleep(0.5)
        device.shell('service call statusbar 2')
        device.input_keyevent(187)
        device.input_keyevent(187)
