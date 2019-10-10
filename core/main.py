import PiSugarCore
import time

core = PiSugarCore.PiSugarCore(local=True)
while 1:
    try:
        core.read_time()
        core.read_battery_v_P()
    except OSError as e:
        print("rtc i2c error...")
        print(e)

    time.sleep(1)