# -*-coding:utf-8-*-
# coding: utf-8

import time
import threading
from smbus2 import SMBusWrapper
import socket
import sys
import os


class PiSugarCore:

    IS_RTC_ALIVE = False
    IS_BAT_ALIVE = False
    IS_CHARGING = False
    BATTERY_LEVEL_RECORD = None

    BATTERY_LEVEL = -1
    BATTERY_I = 0
    BATTERY_V = 0
    RTC_ADDRESS = 0x32
    BAT_ADDRESS = 0x75
    CTR1 = 0x0f
    CTR2 = 0x10
    CTR3 = 0x11

    UPDATE_INTERVAL = 1
    TIME_UPDATE_INTERVAL = 0.5
    RTC_TIME = None
    RTC_TIME_LIST = None

    SERVER_ADDRESS = '/tmp/pisugar.sock'
    SERVER_ADDRESS_UI = '/tmp/pisugar_ui.sock'

    def __init__(self):

        # 初始化实例，检查i2c总线里各个芯片是否存在
        IS_RTC_ALIVE = True
        IS_BAT_ALIVE = True

        print("Initialing PiSugar Core ...")
        self.start_socket_server()
        try:
            self.clean_clock_flag()
            self.battery_shutdown_threshold_set()
            self.battery_loop()
            self.rtc_loop()
            self.gpio_loop()
            self.charge_check_loop()
            self.battery_gpio_set()
        except OSError as e:
            print(e)

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

    # BCD转换为time模组
    @staticmethod
    def __bcd2time(bcd):

        # time模组处理str的时候，周数会自动减一。例如，数字3代表周三，但是time模组以周日为第一天，读取以后会自动减一。SD3078也是周日为第一天，此处手动加1解决匹配的问题
        bcd[3] = (bcd[3] - 1) % 7

        # 先将BCD码转化为十进制的，空格间隔的字符串：43 35 11 3 18 7 19
        str1 = ' '.join([str(PiSugarCore.__bcd2ten(x)) for x in bcd])
        # print(str1)

        # 将字符串转化为time元组
        bcd_time = time.strptime(str1, "%S %M %H %w %d %m %y")

        # print(BCDtime)
        return bcd_time

    # 时间戳转换为寄存器BCD码（24小时制）
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

    # 关闭写保护
    def __disable_rtc_write_protect(self):
        with SMBusWrapper(1) as bus:
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            ct = ct | 0b10000000
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR2, ct)
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            ct = ct|0b10000100
            bus.write_byte_data(self.RTC_ADDRESS, self.CTR1, ct)
        return

    # 打开写保护
    def __enable_rtc_write_protect(self):
        with SMBusWrapper(1) as bus:
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

    def read_clock_flag(self):
        with SMBusWrapper(1) as bus:
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            print("Read clock flag:", ct)
            if ct & 0b00100000:
                print("clock flag triggered")
                return 1
            if ct & 0b00010000:
                print("clock flag triggered")
                return 1
            return 0

    def clean_clock_flag(self):
        print("Clean clock flag.")
        if self.read_clock_flag() == 1:
            with SMBusWrapper(1) as bus:
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
        with SMBusWrapper(1) as bus:
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

    def read_time(self):
        with SMBusWrapper(1) as bus:
            block = bus.read_i2c_block_data(self.RTC_ADDRESS, 0, 7)
            # print(block)
            # 屏蔽判断位
            block[2] = block[2] & 0b01111111
            time_ic = self.__bcd2ten_list(block)
            self.RTC_TIME = self.__bcd2time(block)
            # print("System time：", self.__time2ten(time.localtime(time.time())))
            # print("RTC time", time.strftime("%Y--%m--%d %H:%M:%S", time_ic))
            # time.sleep(1)
            self.RTC_TIME_LIST = time_ic
            return time_ic

    def get_rtc_time(self):
        return self.RTC_TIME

    '''
    clock_time_set
    
    clock_time 
    [sec, min, hour, week, day, month, year]
    ep. [10, 1, 16, 4, 30, 12, 19] -> 16:01:10 Thu 2019-12-05
    
    week_day_repeat
    ep. 0b00000111 -> repeat alarm on Tue, Mon, Sun 
    '''

    def clock_time_set(self, clock_time, week_repeat):
        print("预计开机时间：", clock_time)
        bcd = self.__ten2bcd_list(clock_time)
        bcd[3] = week_repeat
        print("经过转换后：", bcd)
        with SMBusWrapper(1) as bus:

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

    def read_battery_i(self):
        with SMBusWrapper(1) as bus:
            low = bus.read_byte_data(self.BAT_ADDRESS, 0xa4)
            high = bus.read_byte_data(self.BAT_ADDRESS, 0xa5)
            # print(bin(high))
            # print(bin(low))
            if high & 0x20:
                low = ~low & 0xff
                high = (~high) & 0x1f
                # print(bin(high))
                # print(bin(low))
                i = -(high * 256 + low + 1) * 0.745985
            else:
                i = ((high & 0x1f) * 256 + low + 1) * 0.745985
        # print("current %d mA" % i)
        self.BATTERY_I = i
        return i

    def read_battery_v(self):
        with SMBusWrapper(1) as bus:
            low = bus.read_byte_data(self.BAT_ADDRESS, 0xa2)
            high = bus.read_byte_data(self.BAT_ADDRESS, 0xa3)
            # print(bin(high))
            # print(bin(low))
            if high & 0x20:
                low = ~low & 0xff
                high = (~high) & 0x1f
            # print(bin(high))
            # print(bin(low))
                v = -(high * 256 + low + 1) * 0.26855 + 2600
            else:
                v = ((high & 0x1f) * 256 + low + 1) * 0.26855 + 2600
        # print("votage %d mV" % v)
        self.BATTERY_V = v
        return v

    def battery_shutdown_threshold_set(self):
        with SMBusWrapper(1) as bus:

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

    # set PMIC GPIO
    def battery_gpio_set(self):
        with SMBusWrapper(1) as bus:
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

    # 读取电源芯片GPIO
    def read_battery_gpio(self):
        with SMBusWrapper(1) as bus:
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x55)
            return t

    def battery_loop(self):
        self.BATTERY_I = self.read_battery_i()
        self.BATTERY_V = self.read_battery_v()
        self.BATTERY_LEVEL = self.get_battery_percent()
        self.battery_shutdown_threshold_set()
        # print("system power: %d mW" % (self.BATTERY_I * self.BATTERY_V / 1000))
        # print("Battery level: %d%%" % self.BATTERY_LEVEL)
        threading.Timer(self.UPDATE_INTERVAL, self.battery_loop).start()

    def rtc_loop(self):
        self.read_time()
        threading.Timer(self.TIME_UPDATE_INTERVAL, self.rtc_loop).start()

    def gpio_loop(self):
        self.read_battery_gpio()
        threading.Timer(0.15, self.read_battery_gpio).start()

    def charge_check_loop(self):
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
        if max_lv - min_lv > 1:
            if max_index > min_index:
                result = True
            else:
                result = False
        elif max_lv - min_lv < 0.15:
            result = False
        if result is not None:
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

    def get_model(self):
        return "PiSugar 2"

    def set_test_wake(self):
        print("wakeup after 1min30sec")
        self.sync_time_pi2rtc()
        current_time = self.read_time()
        current_time[0] = current_time[0] + 30
        current_time[1] = current_time[1] + 1
        if current_time[0] >= 60:
            current_time[1] = current_time[1] + 1
            current_time[0] = current_time[0] - 60

        if current_time[1] >= 60:
            current_time[1] = current_time[1] - 60
            current_time[2] = current_time[2] + 1
        self.clock_time_set(current_time, 0b0111111)

    def socket_server(self):
        try:
            os.unlink(self.SERVER_ADDRESS)
        except OSError:
            if os.path.exists(self.SERVER_ADDRESS):
                raise
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the port
        print(sys.stderr, 'starting up on %s' % self.SERVER_ADDRESS)
        sock.bind(self.SERVER_ADDRESS)

        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            try:
                while True:
                    data = connection.recv(64)
                    if data:
                        # print(sys.stderr, 'sending data back to the client')
                        response = self.socket_handler(data)
                        connection.sendall(response)
                        connection.close()
                        break
                    else:
                        print(sys.stderr, 'no more data from', client_address)
                        connection.close()
                        break
            finally:
                # Clean up the connection
                connection.close()

    def socket_server4ui(self):
        try:
            os.unlink(self.SERVER_ADDRESS_UI)
        except OSError:
            if os.path.exists(self.SERVER_ADDRESS_UI):
                raise
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the port
        print(sys.stderr, 'starting up on %s' % self.SERVER_ADDRESS_UI)
        sock.bind(self.SERVER_ADDRESS_UI)

        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Wait for a connection
            connection, client_address = sock.accept()
            try:
                while True:
                    data = connection.recv(64)
                    if data:
                        # print(sys.stderr, 'sending data back to the client')
                        response = self.socket_handler(data)
                        connection.sendall(response)
                        break
                    else:
                        print(sys.stderr, 'no more data from', client_address)
                        break
            finally:
                # Clean up the connection
                connection.close()

    def socket_handler(self, data):
        req_str = str(data.decode(encoding="utf-8")).replace("\n", "")
        req_arr = req_str.split(" ")
        res_str = ""
        try:
            if req_arr[0] == "get":
                if req_arr[1] == "model":
                    res_str = self.get_model()
                if req_arr[1] == "battery":
                    res_str = str(self.BATTERY_LEVEL)
                if req_arr[1] == "battery_v":
                    res_str = str(self.BATTERY_V)
                if req_arr[1] == "battery_i":
                    res_str = str(self.BATTERY_I)
                if req_arr[1] == "battery_charging":
                    res_str = str(self.IS_CHARGING)
                if req_arr[1] == "rtc_time":
                    res_str = time.strftime("%w %b %d %H:%M:%S %Y", self.RTC_TIME)
                if req_arr[1] == "rtc_time_list":
                    print(self.RTC_TIME_LIST)
                    res_str = str(self.RTC_TIME_LIST)
                if req_arr[1] == "rtc_clock_flag":
                    res_str = str(self.read_clock_flag())
            if req_arr[0] == "rtc_clean_flag":
                self.clean_clock_flag()
                res_str = "done"
            if req_arr[0] == "rtc_pi2rtc":
                self.sync_time_pi2rtc()
                res_str = "done"
            if req_arr[0] == "rtc_clock_set":
                argv1 = req_arr[1]
                argv2 = req_arr[2]
                try:
                    time_arr = list(map(int, argv1.split(",")))
                    week_repeat = int(argv2, 2)
                    self.clock_time_set([time_arr[0], time_arr[1], time_arr[2], time_arr[3], time_arr[4], time_arr[5], time_arr[6]], week_repeat)
                    self.clean_clock_flag()
                    res_str = "done"
                except Exception as e:
                    print(e)
                    return bytes('Invalid arguments.' + "\n", encoding='utf-8')
            if req_arr[0] == "rtc_test_wake":
                self.set_test_wake()
                res_str = "wakeup after 1 min 30 sec"
        except Exception as e:
            print(e)
            return bytes('Invalid arguments.' + "\n", encoding='utf-8')
        return bytes(res_str + "\n", encoding='utf-8')

    def start_socket_server(self):
        threading.Thread(name="server_thread", target=self.socket_server).start()

    def start_socket_server4ui(self):
        threading.Thread(name="server_thread", target=self.socket_server4ui).start()


if __name__ == "__main__":

    core = PiSugarCore()

    # core.battery_GPIO_set()
    # wake up after 1 min 30 sec
    # core.set_test_wake()
    # while 1:
    #     time.sleep(0.15)
    #     print(core.read_battery_GPIO())
    # print("Hello PiSugar 2")
