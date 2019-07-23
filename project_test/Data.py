import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from threading import Thread
import serial
import struct
import datetime
import random
import time     # 以上为导入的库
import pymongo
from bson.objectid import ObjectId
from multiprocessing.pool import ThreadPool


class Get_Data_4_20MA():
    def __init__(self, port, addr):
        self.addr = addr
        # 类的实例化
        logger = modbus_tk.utils.create_logger("console")
        # 建立连接过程 端口设置，波特率设置
        self.master = modbus_rtu.RtuMaster(serial.Serial(port, baudrate=9600))
        self.master.set_timeout(1.8)
        logger.info("connected")
        print('串口连接建立成功.....')
        #self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 20, output_value=1)   # 线圈输出地址 20/21/22/23，  通讯建立正常输出指示灯
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.connection = client['data1']
        self.db = self.connection['items1']

    def data_parse_4_20MA(self, t_id, ph_id, ox_id):
        try:  # 做异常处理/ 温度读取 4-20mA电流信号..
            num = self.master.execute(self.addr, cst.READ_HOLDING_REGISTERS, 4, 2)  # 读寄存器，起始地址为0，长度为2，即 0，1  类型为int
            #self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 15, output_value=1)

            a = num[0]  # 数据处理， 转成浮点数
            b = num[1]
            sum = a * 65536 + b
            byte_4 = struct.pack('l', sum)
            float_num, = struct.unpack('f', byte_4)

            temperature = (float_num - 4) / 16 * (35 - 0) + 0  # 线性转化，将浮点数转化成传感器的标准值

            condition = {'_id': t_id}
            temp = self.db.find_one(condition)
            if temp:
                #temp['value'] = ('%.2f' % temperature)
                t = ('%.2f' % temperature)
                print('t', t)
                self.db.update(condition, {'value': str(t)})  # *random.randint(1, 4))

        except:
            print('当前温度值读取失败..数据保持上一次数值..不进行数据库更新..')

        try:  # 做异常处理/ PH读取 4-20mA电流信号..
            num = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 0, 2)  # 读寄存器，起始地址为2，长度为2，即 2，3 类型为int

            a = num[0]  # 数据处理， 转成浮点数
            b = num[1]
            sum = a * 65536 + b
            byte_4 = struct.pack('l', sum)
            float_num, = struct.unpack('f', byte_4)

            PH = (float_num - 4) / 16 * (14 - 0) + 0  # 线性转化，将浮点数转化成传感器的标准值

            condition = {'_id': ph_id}
            temp = self.db.find_one(condition)
            if temp:
                #temp['value'] = ('%.2f' % PH)
                p = ('%.2f' % PH)
                print('p', p)
                self.db.update(condition, {'value': str(p)})
                if (p < 0 or p > 14.5) and self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 21, output_value=0)
                    self.temp_num = 0
                elif (0 <= p <= 14.5) and not self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 21, output_value=1)
                    self.temp_num = 1

        except:
            print('当前PH读取失败..数据保持上一次数值..不进行数据库更新..')

        try:  # 做异常处理/ 溶氧读取 4-20mA电流信号..

            num = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 2, 2)  # 读寄存器，起始地址为4，长度为2，即 4，5  类型为int

            a = num[0]  # 数据处理， 转成浮点数
            b = num[1]

            sum = a * 65536 + b
            byte_4 = struct.pack('l', sum)
            float_num, = struct.unpack('f', byte_4)

            oxygen = (float_num - 4) / 16 * (20 - 0) + 0  # 线性转化，将浮点数转化成传感器的标准值

            condition = {'_id': ox_id}
            temp = self.db.find_one(condition)
            if temp:
                #temp['value'] = ('%.2f' % oxygen)
                o = ('%.2f' % oxygen)
                print('o', o)
                self.db.update(condition, {'value': str(o)})
                if (p < 0 or p > 14.5) and self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 22, output_value=0)
                    self.temp_num = 0
                elif (0 <= p <= 14.5) and not self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 22, output_value=1)
                    self.temp_num = 1

        except:
            print('当前溶解氧值读取失败..数据保持上一次数值..不进行数据库更新..')

        try:
            #self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 13, output_value=0)

            y_bytes = struct.pack('!f', oxygen)
            y_hex = ''.join(['%02x' % i for i in y_bytes])
            n, m = y_hex[:-4], y_hex[-4:]
            n, m = int(n, 16), int(m, 16)
            print(n, m)

            t_bytes = struct.pack('!f', temperature)

            t_hex = ''.join(['%02x' % i for i in t_bytes])
            x, y = t_hex[:-4], t_hex[-4:]
            x, y = int(x, 16), int(y, 16)
            print(x, y)

            p_bytes = struct.pack('!f', PH)

            p_hex = ''.join(['%02x' % i for i in p_bytes])
            a, b = p_hex[:-4], p_hex[-4:]
            a, b = int(a, 16), int(b, 16)
            print(a, b)

            num1 = self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 316, output_value=[a, b])
            num2 = self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 516, output_value=[n, m])
            num3 = self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 716, output_value=[x, y])

        except:
            print('写入显示屏失败....')


class Get_Data_485():
    def __init__(self, port, addr, baud):
        self.addr = addr
        self.baud = baud
        self.PH_temp_num = 1
        self.OX_temp_num = 1
        # 类的实例化
        logger = modbus_tk.utils.create_logger("console")
        # 建立连接过程 端口设置，波特率设置
        self.master = modbus_rtu.RtuMaster(serial.Serial(port, baudrate=self.baud, bytesize=8, stopbits=1))
        self.master.set_timeout(1.8)
        logger.info("connected")
        print('串口连接建立成功.....')
        #self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 20, output_value=1)   # 线圈输出地址 20/21/22/23，  通讯建立正常输出指示灯
        #self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 21, output_value=1)   #PH 指示灯
        #self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 22, output_value=1)   #溶氧 指示灯
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.connection = client['data1']
        self.db = self.connection['items1']

    def data_parse_485(self, t_id, ph_id, ox_id):
        try:  # 做异常处理/ PH读取 4-20mA电流信号..
            num = self.master.execute(self.addr, cst.READ_HOLDING_REGISTERS, 0, 2)  # 读寄存器，起始地址为2，长度为2，即 2，3 类型为int
            a = num[0]  # 数据处理， 转成浮点数
            b = num[1]
            sum = a * 65536 + b
            byte_4 = struct.pack('l', sum)
            float_num, = struct.unpack('f', byte_4)

            PH = (float_num - 4) / 16 * (14 - 0) + 0  # 线性转化，将浮点数转化成传感器的标准值

            condition = {'_id': ph_id}
            temp = self.db.find_one(condition)
            if temp:
                p = ('%.2f' % PH)
                print('PH:', p)
                self.db.update(condition, {'value': str(p)})
                if (p < 0 or p > 14.5) and self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 21, output_value=0)
                    self.temp_num = 0
                elif (0 <= p <= 14.5) and not self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 21, output_value=1)
                    self.temp_num = 1
        except:
            # print('当前PH读取失败..数据保持上一次数值..不进行数据库更新..')
                pass

        try: # 做异常处理/ 温度/溶氧数据读取 485信号..
            OX = self.master.execute(168, cst.READ_HOLDING_REGISTERS, 0, 12)
            oxygen = float(OX[0]/100)
            temperature = float(OX[2]/10)
            print('oxygen:', oxygen)
            print('temperature:', temperature)

            condition = {'_id': t_id}
            temp = self.db.find_one(condition)
            if temp:
                t = ('%.2f' % temperature)
                self.db.update(condition, {'value': str(t)})

            condition = {'_id': ox_id}
            temp = self.db.find_one(condition)
            if temp:
                o = ('%.2f' % oxygen)
                self.db.update(condition, {'value': str(o)})
                if (o < 0 or o > 22) and self.OX_temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 22, output_value=0)
                    self.OX_temp_num = 0
                elif (0 >= o <= 22) and not self.temp_num:
                    self.master.execute(self.addr, cst.WRITE_SINGLE_COIL, 22, output_value=1)
                    self.OX_temp_num = 1

            bit = int(temp['bit'])
            bit_2 = int(temp['bit2'])
            print(condition, bit_2)
            if bit_2 == 1:
                print('{}将修改的盐度值{}写入485终端...'.format(condition, bit))
                try:
                    self.master.execute(247, cst.WRITE_SINGLE_REGISTER, 8, 2)
                    temp['bit2'] = '0'
                    self.db.update(condition, temp)

                except:
                    print('485设备离线......')

                finally:
                    temp['bit2'] = '0'
                    self.db.update(condition, temp)

        except:
            # print('当前溶氧/温度485读取失败..数据保持上一次数值..不进行数据库更新..')
            pass

        try:
            y_bytes = struct.pack('!f', oxygen)
            y_hex = ''.join(['%02x' % i for i in y_bytes])
            n, m = y_hex[:-4], y_hex[-4:]
            n, m = int(n, 16), int(m, 16)
            #print(n, m)

            t_bytes = struct.pack('!f', temperature)

            t_hex = ''.join(['%02x' % i for i in t_bytes])
            x, y = t_hex[:-4], t_hex[-4:]
            x, y = int(x, 16), int(y, 16)
            #print(x, y)

            p_bytes = struct.pack('!f', PH)

            p_hex = ''.join(['%02x' % i for i in p_bytes])
            a, b = p_hex[:-4], p_hex[-4:]
            a, b = int(a, 16), int(b, 16)

            self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 316, output_value=[a, b])
            self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 516, output_value=[n, m])
            self.master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 716, output_value=[x, y])
        except:
            # print('写入显示屏失败....')
            pass

def data_run():
    #a = Get_Data_4_20MA("COM3", 100)
    b = Get_Data_485("COM3", 100)
    t_list = []

    def T_parse(n):
        print('开启多线程/当前线程{}....'.format(n))
        #a.data_parse_4_20MA(t_id="t-{}".format(n), ph_id="ph-{}".format(n), ox_id="ox-{}".format(n))
        b.data_parse_485(t_id="t-{}".format(n), ph_id="ph-{}".format(n), ox_id="ox-{}".format(n))
        #print('当前是第{}个线程..'.format(n))

    while True:
        #for i,j in zip((4,5,6),(1,2,3)) 多串口， 多类实例化的多线程传参

        pool = ThreadPool(26)
        for i in range(1, 27):
                # t = Thread(target=T_parse, args=(i,))
                # t_list.append(t)
                # t.start()
            pool.apply_async(T_parse, args=(i, ))

        pool.close()
        pool.join()


        # for t in t_list:
        #     t.join()

        # time.sleep(1)

def data_run_1():
    a1 = Get_Data_485("COM3", 100, 9600)
    a2 = Get_Data_485("COM3", 101, 9600)
    a3 = Get_Data_485("COM3", 102, 9600)
    a4 = Get_Data_485("COM3", 103, 9600)
    a5 = Get_Data_485("COM3", 104, 9600)
    a6 = Get_Data_485("COM3", 105, 9600)
    a7 = Get_Data_485("COM3", 106, 9600)
    a8 = Get_Data_485("COM3", 107, 9600)
    a9 = Get_Data_485("COM3", 108, 9600)
    a10 = Get_Data_485("COM3", 109, 9600)
    a11 = Get_Data_485("COM3", 110, 9600)
    a12 = Get_Data_485("COM3", 111, 9600)
    a13 = Get_Data_485("COM3", 112, 9600)

    a14 = Get_Data_485("COM3", 113, 19200)
    a15 = Get_Data_485("COM3", 114, 19200)
    a16 = Get_Data_485("COM3", 115, 19200)
    a17 = Get_Data_485("COM3", 116, 19200)
    a18 = Get_Data_485("COM3", 117, 19200)
    a19 = Get_Data_485("COM3", 118, 19200)
    a20 = Get_Data_485("COM3", 119, 19200)
    a21 = Get_Data_485("COM3", 120, 19200)
    a22 = Get_Data_485("COM3", 121, 19200)
    a23 = Get_Data_485("COM3", 122, 19200)
    a24 = Get_Data_485("COM3", 123, 19200)
    a25 = Get_Data_485("COM3", 124, 19200)
    a26 = Get_Data_485("COM3", 125, 19200)


    def T_parse(n):
        print('开启多线程/当前线程{}....'.format(n))
        getattr(locals()['a{}'.format(n)], 'data_parse_485', 'not find')(t_id="t-{}".format(n), ph_id="ph-{}".format(n), ox_id="ox-{}".format(n))

    while True:
        for i in range(1, 27): #多串口， 多类实例化的多线程传参
            print(i)

        pool = ThreadPool(26)
        for i in range(1, 27):
            pool.apply_async(T_parse, args=(i,))

        pool.close()
        pool.join()


def fun_test():
    b = Get_Data_485("COM3", 100, 9600)
    while True:
        b.data_parse_485(t_id="t-{}".format(1), ph_id="ph-{}".format(1), ox_id="ox-{}".format(1))
        time.sleep(0.7)


if __name__ == '__main__':
    #data_run()
    fun_test()
