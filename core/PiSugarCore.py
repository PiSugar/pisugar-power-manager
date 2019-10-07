# -*-coding:utf-8-*-
# coding: utf-8

import time
import threading
import json
import os
import http.client
from smbus2 import SMBus


class PiSugarCore:

    TIME_HOST = "cdn.pisugar.com"

    IS_RTC_ALIVE = False
    IS_BAT_ALIVE = False
    IS_CHARGING = False
    BATTERY_LEVEL_RECORD = None

    BATTERY_LEVEL = -1
    BATTERY_I = 0
    BATTERY_V = 0
    BATTERY_MODEL = ""
    RTC_ADDRESS = 0x32
    BAT_ADDRESS = 0x75
    CTR1 = 0x0f
    CTR2 = 0x10
    CTR3 = 0x11
    IS_PRO = True

    UPDATE_INTERVAL = 1
    TIME_UPDATE_INTERVAL = 0.5
    GPIO_INTERVAL = 0.15
    RTC_TIME = None
    RTC_TIME_LIST = None

    AUTO_WAKE_TYPE = 0
    AUTO_WAKE_TIME = time.time()
    AUTO_WAKE_REPEAT = 0b0000000

    TAP_ARRAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    SINGLE_TAP_ENABLE = False
    SINGLE_TAP_SHELL = ""
    DOUBLE_TAP_ENABLE = False
    DOUBLE_TAP_SHELL = ""
    LONG_TAP_ENABLE = False
    LONG_TAP_SHELL = ""

    AUTO_SHUTDOWN_PERCENT = -1

    SERVER = None
    JSON_PATH = os.path.expanduser('~') + "/pisugar_data.json"

    def __init__(self, local=False):

        print("Initialing PiSugar Core ...")
        if local:
            from PiSugarServer import PiSugarServer
        else:
            from core.PiSugarServer import PiSugarServer

        self.SERVER = PiSugarServer(core=self)
        self.loadData()

        try:
            v = self.read_battery_v()
            if v == 0:
                self.IS_PRO = False
            v = self.read_battery_v_P()
            if v== 0:
                self.IS_PRO = True
        except OSError as e:
            print(e)

        if self.IS_PRO:
            try:
                self.battery_shutdown_threshold_set_P()
                self.battery_loop_P()
                self.charge_check_loop()
                self.IS_BAT_ALIVE = True
                self.BATTERY_MODEL = "PiSugar 2 Pro"
            except OSError as e:
                print("Battery i2c error...")
                print(e)
        else:
            try:
                self.battery_shutdown_threshold_set()
                self.battery_loop()
                self.gpio_loop()
                self.charge_check_loop()
                self.battery_gpio_set()
                self.IS_BAT_ALIVE = True
                self.BATTERY_MODEL = "PiSugar 2"
            except OSError as e:
                print("Battery i2c error...")
                print(e)

        try:
            self.clean_alarm_flag()
            self.rtc_loop()
            self.IS_RTC_ALIVE = True
        except OSError as e:
            print("rtc i2c error...")
            print(e)

        print(self.get_battery_percent())
        self.dump_data()

    def get_status(self):
        return self.IS_BAT_ALIVE, self.IS_RTC_ALIVE

    @staticmethod
    def __bcd2ten(bcd):
        return (bcd & 0x0F) + (((bcd & 0xF0) >> 4) * 10)

    @staticmethod
    def __ten2bcd(ten):
        return ten % 10 + (int(ten / 10) << 4)

    @staticmethod
    def __bcd2ten_list(bcd):
        ten = []
        for k in bcd:
            ten.append(PiSugarCore.__bcd2ten(k))
        return ten

    @staticmethod
    def __ten2bcd_list(ten):
        bcd = []
        for k in ten:
            bcd.append(PiSugarCore.__ten2bcd(k))
        return bcd

    @staticmethod
    def __time2ten(ttime):
        bcd = PiSugarCore.__time2bcd(ttime)
        ten = PiSugarCore.__bcd2ten_list(bcd)
        return ten

    @staticmethod
    def __ten2time(ten):
        bcd = PiSugarCore.__ten2bcd_list(ten)
        ttime = PiSugarCore.__bcd2time(bcd)
        return ttime

    @staticmethod
    def __bcd2time(bcd):

        # time模组处理str的时候，周数会自动减一。例如，数字3代表周三，但是time模组以周日为第一天，读取以后会自动减一。SD3078也是周日为第一天，此处手动加1解决匹配的问题
        # print(bcd)
        bcd[3] = (bcd[3] - 1) % 7

        # 先将BCD码转化为十进制的，空格间隔的字符串：43 35 11 3 18 7 19
        str1 = ' '.join([str(PiSugarCore.__bcd2ten(x)) for x in bcd])
        # print(str1)

        # 将字符串转化为time元组
        bcd_time = time.strptime(str1, "%S %M %H %w %d %m %y")

        # print(BCDtime)
        return bcd_time

    @staticmethod
    def __time2bcd(local_time):
        bcd = [
            PiSugarCore.__ten2bcd(local_time.tm_sec),
            PiSugarCore.__ten2bcd(local_time.tm_min),
            PiSugarCore.__ten2bcd(local_time.tm_hour),
            PiSugarCore.__ten2bcd((local_time.tm_wday + 1) % 7),
            PiSugarCore.__ten2bcd(local_time.tm_mday),
            PiSugarCore.__ten2bcd(local_time.tm_mon),
            PiSugarCore.__ten2bcd(local_time.tm_year % 100)
        ]
        return bcd

    def __disable_rtc_write_protect(self):
        with SMBus(1) as bus:
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            ct = ct | 0b10000000
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR2, ct)
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            ct = ct|0b10000100
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR1, ct)
        return

    def __enable_rtc_write_protect(self):
        with SMBus(1) as bus:
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            # print(ct)
            ct = ct & 0b01111011
            # print(ct)
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR1, ct)
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            # print(ct)
            ct = ct & 0b01111111
            # print(ct)
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR2, ct)
        return

    def read_alarm_flag(self):
        with SMBus(1) as bus:
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            print("Read clock flag:", ct)
            if ct & 0b00100000:
                print("clock flag triggered")
                return 1
            if ct & 0b00010000:
                print("clock flag triggered")
                return 1
            return 0

    def clean_alarm_flag(self):
        print("Clean clock flag.")
        if self.read_alarm_flag() == 1:
            with SMBus(1) as bus:
                # 关闭写保护，写入数据
                self.__disable_rtc_write_protect()
                ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
                # print(ct)
                ct = ct & 0b11001111
                # print(ct)
                bus.write_byte_data(self.RTC_ADDRESS, self.CTR1, ct)
                # 数据写入完毕，打开写保护
                self.__enable_rtc_write_protect()
        return

    def sync_time_pi2rtc(self):
        print("Syncing Pi time to RTC...")
        with SMBus(1) as bus:
            ticks = time.time()
            localtime = time.localtime(ticks)
            print(localtime)
            bcd = self.__time2bcd(localtime)
            # 设置为24小时制

            bcd[2] = bcd[2] | 0b10000000
            # 关闭写保护，写入数据
            self.__disable_rtc_write_protect()
            bus.write_i2c_block_data(self.RTC_ADDRESS, 0, bcd)

            # 数据写入完毕，打开写保护
            self.__enable_rtc_write_protect()
        return

    def sync_time_rtc2pi(self):
        print ("Syncing RTC time to Pi...")
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", self.RTC_TIME)
        os.system('sudo date -s "%s"' % time_string)
        print (time_string)

    def sync_time_web(self):
        print ("Syncing Web time to RTC & Pi...")
        try:
            conn = http.client.HTTPConnection(self.TIME_HOST)
            conn.request("GET", "/")
            r = conn.getresponse()
            ts = r.getheader('date')
            print (ts)
            ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
            ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", ttime)
            print (time_string)
            tm = "date -s \"%s\"" % time_string
            os.system(tm)
            print("Update system time successfully!")
            self.sync_time_pi2rtc()
            print("Sync time Pi => RTC successfully!")
        except EnvironmentError as e:
            print ("Sync web time except")
            print (e)
            return None


    def read_time(self):
        with SMBus(1) as bus:
            block = bus.read_i2c_block_data(self.RTC_ADDRESS, 0, 7)
            # print(block)
            # 屏蔽判断位
            block[2] = block[2] & 0b01111111
            time_ic = self.__bcd2ten_list(block)
            self.logger(str(time_ic))
            self.RTC_TIME = self.__bcd2time(block)
            # print("System time：", self.__time2ten(time.localtime(time.time())))
            # print("RTC time", time.strftime("%Y--%m--%d %H:%M:%S", time_ic))
            # time.sleep(1)
            self.RTC_TIME_LIST = time_ic
            return time_ic

    def get_rtc_time(self):
        return self.RTC_TIME

    '''
    set_rtc_alarm
    
    clock_time 
    [sec, min, hour, week, day, month, year]
    ep. [10, 1, 16, 4, 30, 12, 19] -> 16:01:10 Thu 2019-12-05
    
    week_day_repeat
    ep. 0b00000111 -> repeat alarm on Tue, Mon, Sun 
    '''

    def set_rtc_alarm(self, clock_time, week_repeat):
        print("预计开机时间：", clock_time)
        bcd = self.__ten2bcd_list(clock_time)
        bcd[3] = week_repeat
        print("经过转换后：", bcd)
        with SMBus(1) as bus:

            # 关闭写保护，写入数据
            self.__disable_rtc_write_protect()

            # 设置报警时间
            bus.write_i2c_block_data(self.RTC_ADDRESS, 0x07, bcd)

            # 打开报警中断同时设置INT输出选择报警中断和频率
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            # print(ct)
            ct = ct | 0b01010010
            ct = ct & 0b11011111
            print("预计写入的数据为：", bin(ct))
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR2, ct)

            # 设置报警允许位为小时分钟秒
            bus.write_byte_data(self.RTC_ADDRESS, 0X0E, 0b00000111)

            # 数据写入完毕，打开写保护
            self.__enable_rtc_write_protect()
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            # print("CTR1数据为：", bin(ct))
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            # print("CTR2数据为：", bin(ct))
            block = bus.read_i2c_block_data(self.RTC_ADDRESS, 0x07, 7)
            print(block)
        self.AUTO_WAKE_TYPE = 1
        self.AUTO_WAKE_TIME = time.mktime(self.__ten2time(clock_time))
        self.AUTO_WAKE_REPEAT = week_repeat
        self.dump_data()

    def disable_rtc_alarm(self):
        self.AUTO_WAKE_TYPE = 0
        with SMBus(1) as bus:

            # 关闭写保护，写入数据
            self.__disable_rtc_write_protect()

            # 打开报警中断同时设置INT输出选择报警中断和频率
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            # print(ct)
            ct = ct | 0b01010010
            ct = ct & 0b11011111
            print("预计写入的数据为：", bin(ct))
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR2, ct)

            # 设置报警允许位为小时分钟秒
            bus.write_byte_data(self.RTC_ADDRESS, 0X0E, 0b00000000)

            # 数据写入完毕，打开写保护
            self.__enable_rtc_write_protect()
        self.dump_data()


    #P版本读取SYS电流
    def read_battery_i_P(self):
        with SMBus(1) as bus:
            low = bus.read_byte_data(self.BAT_ADDRESS, 0x6a)
            high = bus.read_byte_data(self.BAT_ADDRESS, 0x6b)
            if high & 0x20:
                low = ~low & 0xff
                high = (~high) & 0x1f
                i = -(high * 256 + low + 1) * 0.6394
            else:
                i = ((high & 0x1f) * 256 + low + 1) * 0.6394
        # print("current %d mA" % i)
        self.BATTERY_I = i
        return i


    # P版本读取SYS电压
    def read_battery_v_P(self):
        with SMBus(1) as bus:
            low = bus.read_byte_data(self.BAT_ADDRESS, 0x64)
            high = bus.read_byte_data(self.BAT_ADDRESS, 0x65)
            if high & 0x20:
                low = ~low & 0xff
                high = (~high) & 0x1f
                v = -(high * 256 + low + 1) * 0.26855 + 2600
            else:
                v = ((high & 0x1f) * 256 + low + 1) * 0.26855 + 2600
        self.BATTERY_V = v
        # print("current %d mV" % v)
        self.logger(str(v/1000))
        return v


    #zero版本读取电池电流
    def read_battery_i(self):
        with SMBus(1) as bus:
            low = bus.read_byte_data(self.BAT_ADDRESS, 0xa4)
            high = bus.read_byte_data(self.BAT_ADDRESS, 0xa5)
            if high & 0x20:
                low = ~low & 0xff
                high = (~high) & 0x1f
                i = -(high * 256 + low + 1) * 0.745985
            else:
                i = ((high & 0x1f) * 256 + low + 1) * 0.745985
        self.BATTERY_I = i
        return i

    #zero版本读取电池电压
    def read_battery_v(self):
        with SMBus(1) as bus:
            low = bus.read_byte_data(self.BAT_ADDRESS, 0xa2)
            high = bus.read_byte_data(self.BAT_ADDRESS, 0xa3)
            if high & 0x20:
                low = ~low & 0xff
                high = (~high) & 0x1f
                v = -(high * 256 + low + 1) * 0.26855 + 2600
            else:
                v = ((high & 0x1f) * 256 + low + 1) * 0.26855 + 2600
        self.BATTERY_V = v
        return v

    #Zero版本设置关机阈值
    def battery_shutdown_threshold_set(self):
        with SMBus(1) as bus:

            # 设置阈值电流
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x0c)
            t = (t & 0b00000111)
            t = t | (12 << 3)
            bus.write_byte_data(self.BAT_ADDRESS, 0x0c, t)

            # 设置关机时间
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x04)
            t = t | 0b00000000
            t = t & 0b00111111
            bus.write_byte_data(self.BAT_ADDRESS, 0x04, t)

            # 确保使能打开
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x02)
            t = t | 0b00000011
            bus.write_byte_data(self.BAT_ADDRESS, 0x02, t)


    #P版本关机轻载阈值设定，SYSI总电流，不会随电池电压降低而增加
    def battery_shutdown_threshold_set_P(self):
        with SMBus(1) as bus:

            # 设置阈值电流和打开使能
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x84)
            t = (t & 0b00000111)
            t = t | (12 << 3)
            t = 0xFF
            bus.write_byte_data(self.BAT_ADDRESS, 0x84, t)

            # 设置关机时间
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x07)
            t = t | 0b01000000
            t = t & 0b01111111
            bus.write_byte_data(self.BAT_ADDRESS, 0x07, t)


    #P版本强制关机，主要用于解决树莓派关机后轻载电流依然过大的问题
    def battery_force_shutdown_P(self):
        with SMBus(1) as bus:
            # 开启强制关机开关
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x5B)
            t = t | 0b00010010
            bus.write_byte_data(self.BAT_ADDRESS, 0x5B, t)

            # 强制关机
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x5B)
            t = t & 0b11101111
            bus.write_byte_data(self.BAT_ADDRESS, 0x5B, t)


    def battery_gpio_set(self):
        with SMBus(1) as bus:
            # 将VSET更改为内部设置
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x26)
            t = t | 0b00000000
            t = t & 0b10111111
            bus.write_byte_data(self.BAT_ADDRESS, 0x26, t)

            # 将VSET引脚更改为GPIO模式
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x52)
            t = t | 0b00000100
            t = t & 0b11110111
            bus.write_byte_data(self.BAT_ADDRESS, 0x52, t)
            # 将VSET的GPIO设置为输入
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x53)
            t = t | 0b00010000
            t = t & 0b11111111
            bus.write_byte_data(self.BAT_ADDRESS, 0x53, t)

    def read_battery_gpio(self):
        with SMBus(1) as bus:
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x55)
            self.gpio_tap_detect(t)
            return t

    #Zero版本检测按下
    def gpio_tap_detect(self, tap):
        if tap > 0:
            tap = 1
        del self.TAP_ARRAY[0]
        self.TAP_ARRAY.append(tap)
        string = "".join([str(x) for x in self.TAP_ARRAY])
        should_refresh = False
        current_tap_type = ""
        if string.find("111111110") >= 0:
            print("long tap event")
            current_tap_type = "long"
            should_refresh = True
        if string.find("1010") >= 0 \
                or string.find("10010") >= 0 \
                or string.find("10110") >= 0\
                or string.find("100110") >= 0\
                or string.find("101110") >= 0\
                or string.find("1001110") >= 0:
            print("double tap event")
            current_tap_type = "double"
            should_refresh = True
        if string.find("1000") >= 0:
            print("single tap event")
            current_tap_type = "single"
            should_refresh = True
        if current_tap_type != "":
            self.SERVER.ws_broadcast(current_tap_type)
        if current_tap_type == "single" and self.SINGLE_TAP_ENABLE:
            self.execute_shell_async(self.SINGLE_TAP_SHELL)
        if current_tap_type == "double" and self.DOUBLE_TAP_ENABLE:
            self.execute_shell_async(self.DOUBLE_TAP_SHELL)
        if current_tap_type == "long" and self.LONG_TAP_ENABLE:
            self.execute_shell_async(self.LONG_TAP_SHELL)
        if should_refresh:
            self.TAP_ARRAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # print(self.TAP_ARRAY)

    def battery_loop(self):
        self.BATTERY_I = self.read_battery_i()
        self.BATTERY_V = self.read_battery_v()
        self.BATTERY_LEVEL = self.get_battery_percent()
        self.battery_shutdown_threshold_set()
        if self.BATTERY_LEVEL < self.AUTO_SHUTDOWN_PERCENT:
            self.execute_shell_async("sudo shutdown now")
        threading.Timer(self.UPDATE_INTERVAL, self.battery_loop).start()

    def battery_loop_P(self):
        self.BATTERY_I = self.read_battery_i_P()
        self.BATTERY_V = self.read_battery_v_P()
        self.BATTERY_LEVEL = self.get_battery_percent()
        self.battery_shutdown_threshold_set()
        if self.BATTERY_LEVEL < self.AUTO_SHUTDOWN_PERCENT:
            self.execute_shell_async("sudo shutdown now")
        threading.Timer(self.UPDATE_INTERVAL, self.battery_loop_P).start()

    def rtc_loop(self):
        try:
            self.read_time()
        except ValueError as error:
            print(error)
            self.logger('rtc time error')
        threading.Timer(self.TIME_UPDATE_INTERVAL, self.rtc_loop).start()

    def gpio_loop(self):
        current = self.read_battery_gpio()
        if current == 0:
            threading.Timer(self.GPIO_INTERVAL, self.gpio_loop).start()
        else:
            threading.Timer(self.GPIO_INTERVAL / 3, self.gpio_loop).start()

    def charge_check_loop(self):
        # print("check charging")
        if self.BATTERY_LEVEL == -1:
            threading.Timer(self.UPDATE_INTERVAL, self.charge_check_loop).start()
            return
        if self.BATTERY_LEVEL_RECORD is None:
            lv = self.BATTERY_LEVEL
            self.BATTERY_LEVEL_RECORD = [lv, lv, lv, lv, lv, lv, lv, lv, lv, lv]
        else:
            del self.BATTERY_LEVEL_RECORD[0]
            self.BATTERY_LEVEL_RECORD.append(self.BATTERY_LEVEL)
        max_lv = max(self.BATTERY_LEVEL_RECORD)
        max_index = self.BATTERY_LEVEL_RECORD.index(max_lv)
        min_lv = min(self.BATTERY_LEVEL_RECORD)
        min_index = self.BATTERY_LEVEL_RECORD.index(min_lv)
        result = None
        if max_lv - min_lv > 0.8:
            if max_index > min_index:
                result = True
            else:
                result = False
        elif max_lv - min_lv < 0.2:
            result = False
        if result is not None:
            # print("charing?", result)
            if not result:
                start_index = 1
                acc = 0
                while start_index < 10:
                    acc += self.BATTERY_LEVEL_RECORD[start_index] - self.BATTERY_LEVEL_RECORD[start_index - 1]
                    start_index += 1
                if acc > 0.2:
                    result = True
                # print(acc)
            self.IS_CHARGING = result
        threading.Timer(self.UPDATE_INTERVAL, self.charge_check_loop).start()

    def get_battery_votage(self):
        return int(self.BATTERY_V / 10) / 100

    def get_battery_current(self):
        return int(self.BATTERY_I / 10) / 100

    def get_battery_charging_status(self):
        return self.IS_CHARGING

    def get_battery_percent(self):
        batter_curve = [
            [4.16, 5.5, 100, 100],
            [4.05, 4.16, 87.5, 100],
            [4.00, 4.05, 75, 87.5],
            [3.92, 4.00, 62.5, 75],
            [3.86, 3.92, 50, 62.5],
            [3.79, 3.86, 37.5, 50],
            [3.66, 3.79, 25, 37.5],
            [3.52, 3.66, 12.5, 25],
            [3.49, 3.52, 6.2, 12.5],
            [3.1, 3.49, 0, 6.2],
            [0, 3.1, 0, 0],
        ]
        batter_level = 0
        for range in batter_curve:
            if range[0] < self.BATTERY_V / 1000 <= range[1]:
                batter_level = ((self.BATTERY_V / 1000 - range[0]) / (range[1] - range[0])) * (range[3] - range[2]) + range[2]
        self.BATTERY_LEVEL = batter_level
        return batter_level

    #检测硬件版本
    def get_model(self):
        return self.BATTERY_MODEL

    def set_test_wake(self):
        print("wakeup after 1min30sec")
        self.sync_time_pi2rtc()
        current_time = self.read_time()
        current_time[0] = current_time[0] + 5
        current_time[1] = current_time[1] + 0
        if current_time[0] >= 60:
            current_time[1] = current_time[1] + 1
            current_time[0] = current_time[0] - 60

        if current_time[1] >= 60:
            current_time[1] = current_time[1] - 60
            current_time[2] = current_time[2] + 1
        self.set_rtc_alarm(current_time, 0b0111111)

    def dump_data(self):
        # save data to local file
        data_to_save = {
            'autoWakeType': self.AUTO_WAKE_TYPE,
            'autoWakeTime': self.AUTO_WAKE_TIME,
            'autoWakeRepeat': self.AUTO_WAKE_REPEAT,
            'singleTapEnable': self.SINGLE_TAP_ENABLE,
            'singleTapShell': self.SINGLE_TAP_SHELL,
            'doubleTapEnable': self.DOUBLE_TAP_ENABLE,
            'doubleTapShell': self.DOUBLE_TAP_SHELL,
            'longTapEnable': self.LONG_TAP_ENABLE,
            'longTapShell': self.LONG_TAP_SHELL,
            'autoShutdownPercent': self.AUTO_SHUTDOWN_PERCENT
        }
        print(data_to_save)
        f = open(self.JSON_PATH, 'w')
        new = json.dumps(data_to_save, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(new)
        f.flush()
        f.close()

    def loadData(self):
        if not os.path.exists(self.JSON_PATH):
            return
        f = open(self.JSON_PATH, "r")
        print(f)
        try:
            data = json.load(f)
            self.AUTO_WAKE_TYPE = data['autoWakeType']
            self.AUTO_WAKE_TIME = data['autoWakeTime']
            self.AUTO_WAKE_REPEAT = data['autoWakeRepeat']
            self.SINGLE_TAP_ENABLE = data['singleTapEnable']
            self.SINGLE_TAP_SHELL = data['singleTapShell']
            self.DOUBLE_TAP_ENABLE = data['doubleTapEnable']
            self.DOUBLE_TAP_SHELL = data['doubleTapShell']
            self.LONG_TAP_ENABLE = data['longTapEnable']
            self.LONG_TAP_SHELL = data['longTapShell']
            self.AUTO_SHUTDOWN_PERCENT = data['autoShutdownPercent']
        except Exception as e:
            print(e)

    def get_button_enable(self, button_type):
        if button_type == "single":
            return self.SINGLE_TAP_ENABLE
        if button_type == "double":
            return self.DOUBLE_TAP_ENABLE
        if button_type == "long":
            return self.LONG_TAP_ENABLE

    def set_button_enable(self, button_type, is_enable):
        if button_type == "single":
            self.SINGLE_TAP_ENABLE = is_enable
        if button_type == "double":
            self.DOUBLE_TAP_ENABLE = is_enable
        if button_type == "long":
            self.LONG_TAP_ENABLE = is_enable
        self.dump_data()

    def get_button_shell(self, button_type):
        if button_type == "single":
            return self.SINGLE_TAP_SHELL
        if button_type == "double":
            return self.DOUBLE_TAP_SHELL
        if button_type == "long":
            return self.LONG_TAP_SHELL

    def set_button_shell(self, button_type, shell):
        if button_type == "single":
            self.SINGLE_TAP_SHELL = shell
        if button_type == "double":
            self.DOUBLE_TAP_SHELL = shell
        if button_type == "long":
            self.LONG_TAP_SHELL = shell
        self.dump_data()

    def set_safe_shutdown_level(self, percent):
        self.AUTO_SHUTDOWN_PERCENT = percent
        self.dump_data()

    def get_safe_shutdown_level(self):
        return self.AUTO_SHUTDOWN_PERCENT

    def get_alarm_type(self):
        return self.AUTO_WAKE_TYPE

    def get_alarm_time(self):
        return self.AUTO_WAKE_TIME

    def get_alarm_repeat(self):
        return self.AUTO_WAKE_REPEAT

    def execute_shell_async(self, shell):
        threading.Thread(name="execute_shell", target=self.execute_shell, args=(shell,)).start()

    def execute_shell(self, shell):
        if shell != '':
            print('Execute shell : ' + shell)
            os.system(shell)
        else:
            print('Empty shell!')

    def logger(self, log):
        localtime = time.asctime(time.localtime(time.time()))
        f = open('/home/pi/pisugar_log.txt', 'a+')
        new = str(localtime) + " : " + log + "\n"
        # print(new)
        f.write(new)
        f.flush()
        f.close()


if __name__ == "__main__":

    core = PiSugarCore(local=True)
    # wake up after 1 min 30 sec
    #core.set_test_wake()
    #core.battery_force_shutdown_P()
