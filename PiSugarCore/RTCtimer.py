
import time
#载入总线模块
from smbus2 import SMBusWrapper
#RTC时钟地址为0x32
RTCaddress = 0x32
BATaddress = 0x75
CTR1= 0x0f
CTR2= 0x10
CTR3= 0x11

#单个BCD转十进制
def BCDtoTEN(BCD):
    return ((BCD&0x0F) + (((BCD&0xF0) >> 4) * 10))

#单个十进制转BCD
def TENtoBCD(TEN):
    return (TEN%10+(int(TEN/10)<<4))

#listBCD转十进制
def BCDtoTENl(BCD):
    TEN=[]
    for k in BCD:
        TEN.append(BCDtoTEN(k))
    return TEN

#list十进制转BCD
def TENtoBCDl(TEN):
    BCD= []
    for k in TEN:
#        print("原本的%d转化为%d" %(k,TENtoBCD(k)))
        BCD.append(TENtoBCD(k))
    return BCD


#BCD转换为time模组
def BCDtotime(BCD):
    #time模组处理str的时候，周数会自动减一。例如，数字3代表周三，但是time模组以周日为第一天，读取以后会自动减一。SD3078也是周日为第一天，此处手动加1解决匹配的问题
    BCD[3]=BCD[3]+1
    #先将BCD码转化为十进制的，空格间隔的字符串：43 35 11 3 18 7 19
    str1 = ' '.join([str(BCDtoTEN(x)) for x in BCD])
    print(str1)
    #将字符串转化为time元组
    BCDtime=time.strptime(str1,"%S %M %H %w %d %m %y")
#    print(BCDtime)
    return BCDtime
#时间戳转换为寄存器BCD码（24小时制）
def timetoBCD(localtime):

    BCD=[
        TENtoBCD(localtime.tm_sec),
        TENtoBCD(localtime.tm_min),
        TENtoBCD(localtime.tm_hour),
        TENtoBCD(localtime.tm_wday),
        TENtoBCD(localtime.tm_mday),
        TENtoBCD(localtime.tm_mon),
        TENtoBCD(localtime.tm_year%100)
    ]
    return BCD

def timetoTEN(ttime):
    BCD=timetoBCD(ttime)
    TEN = BCDtoTENl(BCD)
    return TEN

#十进制转BCD
def TENtotime(TEN):
    BCD=TENtoBCDl(TEN)
    ttime=BCDtotime(BCD)
    return time


#关闭写保护
def DSWRTPROTECT():
    with SMBusWrapper(1) as bus:
        ct = bus.read_byte_data(RTCaddress, CTR2)
        #print(ct)
        ct = ct | 0b10000000
        #print(ct)
        bus.write_byte_data(RTCaddress, CTR2, ct)
        ct = bus.read_byte_data(RTCaddress, CTR1)
        #print(ct)
        ct = ct|0b10000100
        #print(ct)
        bus.write_byte_data(RTCaddress, CTR1,ct)
    return

#打开写保护
def ENWRTPROTECT():
    with SMBusWrapper(1) as bus:
        ct = bus.read_byte_data(RTCaddress, CTR1)
        #print(ct)
        ct = ct&0b01111011
        #print(ct)
        bus.write_byte_data(RTCaddress, CTR1,ct)
        ct = bus.read_byte_data(RTCaddress, CTR2)
        #print(ct)
        ct = ct & 0b01111111
        #print(ct)
        bus.write_byte_data(RTCaddress, CTR2, ct)

    return

def readclockflag():
    with SMBusWrapper(1) as bus:
        ct = bus.read_byte_data(RTCaddress, CTR1)
        if ct&0b00100000 :
            print("报警中断已触发")
            return 1
        if ct&0b00010000 :
            print("循环中断已触发")
            return 1

def cleanclockflag():
    if readclockflag()==1:
        with SMBusWrapper(1) as bus:
            DSWRTPROTECT()  # 关闭写保护，写入数据
            ct = bus.read_byte_data(RTCaddress, CTR1)
            # print(ct)
            ct = ct & 0b11001111
            # print(ct)
            bus.write_byte_data(RTCaddress, CTR1, ct)
            ENWRTPROTECT()  # 数据写入完毕，打开写保护
    return

def uploadtime():
    with SMBusWrapper(1) as bus:
        ticks = time.time()
        localtime= time.localtime(ticks)
        BCD=timetoBCD(localtime)
        #设置为24小时制
        BCD[2]=BCD[2]|0b10000000
        DSWRTPROTECT()#关闭写保护，写入数据
        bus.write_i2c_block_data(RTCaddress, 0,BCD )
        ENWRTPROTECT()#数据写入完毕，打开写保护
    return

def readtime():
    with SMBusWrapper(1) as bus:
        block = bus.read_i2c_block_data(RTCaddress, 0, 7)
#        print(block)
        #屏蔽判断位
        block[2]=block[2]&0b01111111
        timeIC=BCDtoTENl(block)
        print("RTC时间为：",timeIC)
        print("系统时间为：",timetoTEN(time.localtime(time.time())))
        #time.sleep(1)
        return timeIC
    
    
def readBATI():
    with SMBusWrapper(1) as bus:
        low = bus.read_byte_data(BATaddress, 0xa4)
        high = bus.read_byte_data(BATaddress, 0xa5)
#        print(bin(high))
#        print(bin(low))
        if high&0x20:
            low = ~low&0xff
            high = (~high)&0x1f
#            print(bin(high))
#            print(bin(low))
            i=-(high*256+low+1)*0.745985
        else:
            i = ((high&0x1f) * 256 + low + 1) * 0.745985
    print("电流为 %d mA" % (i))
    return i

def readBATV():
    with SMBusWrapper(1) as bus:
        low = bus.read_byte_data(BATaddress, 0xa2)
        high = bus.read_byte_data(BATaddress, 0xa3)
#        print(bin(high))
#        print(bin(low))
        if high&0x20:
            low = ~low&0xff
            high = (~high)&0x1f
#            print(bin(high))
#            print(bin(low))
            v=-(high*256+low+1)*0.26855+2600
        else:
            v = ((high&0x1f) * 256 + low + 1)*0.26855+2600
    print("电压为 %d mV" % (v))
    return v

def BATshutdownset():
    with SMBusWrapper(1) as bus:
        #设置阈值电流
        t = bus.read_byte_data(BATaddress, 0x0c)
        print(bin(t))
        t=(t&0b00000111)
        t = t|(12<<3)
        print(bin(t))
        bus.write_byte_data(BATaddress, 0x0c,t)
        #设置关机时间
        t = bus.read_byte_data(BATaddress, 0x04)
        t = t|0b00000000
        t=t&0b00111111
        bus.write_byte_data(BATaddress, 0x04,t)
        #确保使能打开
        t = bus.read_byte_data(BATaddress, 0x02)
        t = t|0b00000011
        bus.write_byte_data(BATaddress, 0x02,t)




def clocktimeset(clocktime,week):
    print("预计开机时间：",clocktime)
    BCD=TENtoBCDl(clocktime)
    BCD[3]=week
    print("经过转换后：",BCD)
    with SMBusWrapper(1) as bus:
        DSWRTPROTECT()#关闭写保护，写入数据
        #设置报警时间
        bus.write_i2c_block_data(RTCaddress, 0x07, BCD)
        #打开报警中断同时设置INT输出选择报警中断和频率
        ct = bus.read_byte_data(RTCaddress, CTR2)
        # print(ct)
        ct = ct | 0b01010010
        ct = ct & 0b11011111
        print("预计写入的数据为：",bin(ct))
        bus.write_byte_data(RTCaddress, CTR2, ct)
        #设置报警允许位为周小时分钟秒
        bus.write_byte_data(RTCaddress, 0X0E, 0b00001111)
        ENWRTPROTECT()  # 数据写入完毕，打开写保护
        ct = bus.read_byte_data(RTCaddress, CTR1)
        print("CTR1数据为：" ,bin(ct))
        ct = bus.read_byte_data(RTCaddress, CTR2)
        print("CTR2数据为：" ,bin(ct))
        block = bus.read_i2c_block_data(RTCaddress, 0x07, 7)
        print(block)



uploadtime()
#readtime()
BATshutdownset()
clocktime = readtime()
clocktime[0] = clocktime[0] + 30
clocktime[1] = clocktime[1] + 1
if clocktime[0] >= 60:
    clocktime[1] = clocktime[1] + 1
    clocktime[0] = clocktime[0] - 60

if clocktime[1] >= 60:
    clocktime[1] = clocktime[1] - 60
    clocktime[2] = clocktime[2] +1
clocktimeset(clocktime, 0b0111111)
t1=0
while 1:
    print("系统功率为 %d mW"%(readBATI()*readBATV()/1000))
    readclockflag()
    readtime()
#cleanclockflag()
    if readclockflag():
        clocktime = readtime()
        clocktime[0] = clocktime[0] + 3
        if clocktime[0] >= 60:
            clocktime[1] = clocktime[1] + 1
            clocktime[0] = clocktime[0] - 60

        if clocktime[1] >= 60:
            clocktime[1] = clocktime[1] - 60
        clocktimeset(clocktime, 0b0111101)
    time.sleep(1)
