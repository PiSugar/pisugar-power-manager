
import time
from smbus2 import SMBusWrapper


class PiSugarCore:

    IS_RTC_ALIVE = False
    IS_BAT_ALIVE = False
    RTC_ADDRESS = 0x32
    BAT_ADDRESS = 0x75
    CTR1 = 0x0f
    CTR2 = 0x10
    CTR3 = 0x11

    def __init__(self):

        # 初始化实例，检查i2c总线里各个芯片是否存在
        IS_RTC_ALIVE = True
        IS_BAT_ALIVE = True

        # 清除rtc报警flag
        self.clean_clock_flag()
        self.battery_shutdown_set()

    def get_model(self):
        return "PiSugar 2"

    def get_status(self):
        return self.IS_BAT_ALIVE, self.IS_RTC_ALIVE

    # 单个BCD转十进制
    @staticmethod
    def __bcd2ten(bcd):
        return (bcd & 0x0F) + (((bcd & 0xF0) >> 4) * 10)

    # 单个十进制转BCD
    @staticmethod
    def __ten2bcd(ten):
        return ten % 10 + (int(ten / 10) << 4)

    # listBCD转十进制
    @staticmethod
    def __bcd2tenl(bcd):
        ten = []
        for k in bcd:
            ten.append(PiSugarCore.__bcd2ten(k))
        return ten

    # list十进制转BCD
    @staticmethod
    def __ten2bcdl(ten):
        bcd = []
        for k in ten:
            # print("原本的%d转化为%d" %(k,TEN2BCD(k)))
            bcd.append(PiSugarCore.__ten2bcd(k))
        return bcd

    @staticmethod
    def __time2ten(ttime):
        bcd = PiSugarCore.__time2bcd(ttime)
        ten = PiSugarCore.__bcd2tenl(bcd)
        return ten

    @staticmethod
    def __ten2time(ten):
        bcd = PiSugarCore.__ten2bcdl(ten)
        ttime = PiSugarCore.__bcd2time(bcd)
        return ttime

    # BCD转换为time模组
    @staticmethod
    def __bcd2time(bcd):
        # time模组处理str的时候，周数会自动减一。例如，数字3代表周三，但是time模组以周日为第一天，读取以后会自动减一。SD3078也是周日为第一天，此处手动加1解决匹配的问题
        bcd[3] = bcd[3]+1
        # 先将BCD码转化为十进制的，空格间隔的字符串：43 35 11 3 18 7 19
        str1 = ' '.join([str(PiSugarCore.__bcd2ten(x)) for x in bcd])
        print(str1)
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
            PiSugarCore.__ten2bcd(local_time.tm_wday),
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
            if ct & 0b00100000:
                print("报警中断已触发")
                return 1
            if ct & 0b00010000:
                print("循环中断已触发")
                return 1

    def clean_clock_flag(self):
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
        with SMBusWrapper(1) as bus:
            ticks = time.time()
            localtime = time.localtime(ticks)
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
            time_ic = self.__bcd2tenl(block)
            print("RTC时间为：", time_ic)
            print("系统时间为：", self.__time2ten(time.localtime(time.time())))
            # time.sleep(1)
            return time_ic

    def clock_time_set(self, clock_time, week):
        print("预计开机时间：", clock_time)
        bcd = self.__ten2bcdl(clock_time)
        bcd[3] = week
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

            # 设置报警允许位为周小时分钟秒
            bus.write_byte_data(self.RTC_ADDRESS, 0X0E, 0b00001111)

            # 数据写入完毕，打开写保护
            self.__enable_rtc_write_protect()
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR1)
            print("CTR1数据为：", bin(ct))
            ct = bus.read_byte_data(self.RTC_ADDRESS, self.CTR2)
            print("CTR2数据为：", bin(ct))
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
        print("电流为 %d mA" % i)
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
        print("电压为 %d mV" % v)
        return v

    def battery_shutdown_set(self):
        with SMBusWrapper(1) as bus:

            # 设置阈值电流
            t = bus.read_byte_data(self.BAT_ADDRESS, 0x0c)
            print(bin(t))
            t = (t & 0b00000111)
            t = t | (12 << 3)
            print(bin(t))
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


if __name__ == "__main__":
    core = PiSugarCore()
    core.sync_time_pi2rtc()
    # read_time()
    core.battery_shutdown_set()
    current_time = core.read_time()
    current_time[0] = current_time[0] + 30
    current_time[1] = current_time[1] + 1
    if current_time[0] >= 60:
        current_time[1] = current_time[1] + 1
        current_time[0] = current_time[0] - 60

    if current_time[1] >= 60:
        current_time[1] = current_time[1] - 60
        current_time[2] = current_time[2] + 1
    core.clock_time_set(current_time, 0b0111111)
    t1 = 0
    while 1:
        print("系统功率为 %d mW" % (core.read_battery_i() * core.read_battery_v() / 1000))
        core.read_clock_flag()
        core.read_time()
        # clean_clock_flag()
        if core.read_clock_flag():
            current_time = core.read_time()
            current_time[0] = current_time[0] + 3
            if current_time[0] >= 60:
                current_time[1] = current_time[1] + 1
                current_time[0] = current_time[0] - 60
            if current_time[1] >= 60:
                current_time[1] = current_time[1] - 60
            core.clock_time_set(current_time, 0b0111101)
        time.sleep(1)
