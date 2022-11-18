from ppadb.client import Client as AdbClient

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)
device = client.device("07845371BS000116")  # Значение из adb devices
# while True:
#     print(list(map(lambda o:o.package,device.get_top_activities())))
# device.shell(device.shell(f'am start -n com.fast.ufovpn.proxy/.ui.SplashActivity'))
device.input_keyevent(123)
device.shell(f'input roll 0 -17') 885