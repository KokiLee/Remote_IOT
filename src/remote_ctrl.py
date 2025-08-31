#!/usr/bin/python3
# coding: utf-8
#####!で始まる1行目の記述はShebangスクリプト自体を実行
#####2行目に、マジックコメントを記述文字エンコーディング
#
# ファイル名：IR-remocon01-commandbase.py   python3用
# バージョン：2017/12/13 v1.0 python2用
#           2018/2/14   v2.0 python3用
#           2018/4/12   v2.1 python3,raspbian（2018/3/14版）対応
# 　　　　　　　　　　　仕様変更：ＯＳ関係コマンド廃止、ディレクトリ固定
#
# ビット・トレード・ワン社提供のラズベリー・パイ専用 学習リモコン基板(型番：ADRSIR)用のツール
# 　著作権者:(C) 2015 ビット・トレード・ワン社
# 　ライセンス: ADL(Assembly Desk License)
#  実行方法：./IR-remocon01-commandbase.py
#
# ****コマンドベース　実行コマンド　ファイル単位
# 読み込みコマンド（ｒ:read）：、読込先の記憶No.（memo_no)、保存ファイル名（filename)
# 書き込みコマンド（ｗ:write）：、書込先の記憶No.（memo_no)、読込ファイル名（filename)
# 送信コマンド(t)：、読み込みファイル名（filename)
# ＰＩＣ→ラズハ゜イ　ディレクトリ読込コマンド（rd:read　directry)：、保存ディレクトリ名（dir_name)
# ＰＩＣ←ラズハ゜イ　ディレクトリ書込コマンド（wd:write　directry)：、読込ディレクトリ名（dir_name)
# 　e　コマンド：終了
#
# 　　コマンド
# 　　command: rd/wd/r/w/t/e
#
#
# 　******Ｉ２Ｃ関係内部コマンド
# cmd R1_memo_no_write 0x15 bus-write(ADR,cmd,n)
# cmd R2_data_num_read 0x25 bus-read(ADR,cmd,n)
# cmd R3_data_read     0x35 bus-read(ADR,cmd,n)
# cmd W1_memo_no_write 0x19 bus-write(ADR,cmd,n)
# cmd W2_data_num_write0x29 bus-write(ADR,cmd,n)
# cmd W3_data_write    0x39 bus-read(ADR,cmd,n)
# cmd W4_flash_write   0x49 bus-read(ADR,cmd,n)
# cmd T1_trans_start   0x59 bus-write(ADR,cmd,n)
#

import threading
from datetime import datetime, timedelta
from pathlib import Path

import gpiozero as gpio
import smbus  # I2C enable in raspi Interface option

from mod_logger import Logger
from mqtt_publish_response import publish_command

logger_set = Logger("loggerConfig/logConfig.json", Path(__file__).stem)
logger = logger_set.get_log()


# gpio is set to pull_up
gpio.Button(pin=4, pull_up=True)
gpio.Button(pin=17, pull_up=True)
gpio.Button(pin=27, pull_up=True)
gpio.Button(pin=18, pull_up=True)
gpio.Button(pin=5, pull_up=True)
gpio.Button(pin=6, pull_up=True)
gpio.Button(pin=13, pull_up=True)
gpio.Button(pin=12, pull_up=True)
gpio.Button(pin=22, pull_up=True)
gpio.Button(pin=23, pull_up=True)


# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)

# This must match in the Arduino Sketch
# SLAVE_ADDRESS = 0x04
SLAVE_ADDRESS = 0x52


class Remote_Command:

    data_numH = 0x31
    data_numL = 0x32
    data_numHL = [0x00, 0x31, 0x32]
    data_num = 10

    # command
    R1_memo_no_write = 0x15  # bus-write(ADR,cmd,1)
    R2_data_num_read = 0x25  # bus-read(ADR,cmd,3)
    R3_data_read = 0x35  # bus-read(ADR,cmd,n)
    W1_memo_no_write = 0x19  # bus-write(ADR,cmd,1)
    W2_data_num_write = 0x29  # bus-write(ADR,cmd,3)
    W3_data_write = 0x39  # bus-read(ADR,cmd,n)
    W4_flash_write = 0x49  # bus-read(ADR,cmd,n)
    T1_trans_start = 0x59  # bus-write(ADR,cmd,1)

    def __init__(self, SLAVE_ADDRESS):
        self.SLAVE_ADDRESS = SLAVE_ADDRESS
        self.block = []
        self.str_block = ""

    ############# read command
    def read_command(self, filename, memo_no):
        """
        Read the selected memory address
        """
        self.block = []
        # cmd R1_memo_no_write 0x15 bus-write(ADR,cmd,1)
        logger.info(f"memo_no write= {memo_no}")
        bus.write_i2c_block_data(
            self.SLAVE_ADDRESS, self.R1_memo_no_write, memo_no
        )  # = 0x15  #bus-write(ADR,cmd,1)

        # cmd R2_data_num_read 0x25 bus-read(ADR,cmd,3)
        data_numHL = bus.read_i2c_block_data(
            self.SLAVE_ADDRESS, self.R2_data_num_read, 3
        )  # = 0x25 #bus-read(ADR,cmd,3)
        data_num = data_numHL[1]
        data_num *= 256
        data_num += data_numHL[2]
        if data_num < 65535:
            logger.info(f"data_num = {data_num}")

            # cmd R3_data_read           0x35 bus-read(ADR,cmd,n)
            self.block = []
            block_dat = bus.read_i2c_block_data(
                self.SLAVE_ADDRESS, self.R3_data_read, 1
            )  # = 0x35 #bus-read(ADR,cmd,n)
            for i in range(data_num):
                block_dat = bus.read_i2c_block_data(
                    self.SLAVE_ADDRESS, self.R3_data_read, 4
                )  # = 0x35 #bus-read(ADR,cmd,n)
                self.block.append(block_dat[0])
                self.block.append(block_dat[1])
                self.block.append(block_dat[2])
                self.block.append(block_dat[3])
            logger.debug(f"block= {self.block}")  # for denug
            logger.info(f"filename= {filename}")
            logger.debug(f"data_num= {data_num}")
            with open(filename, "w") as f:
                for i in range(len(self.block)):
                    # f.write('format(self.block[i]{ X}
                    f.write("{:02X}".format(self.block[i]))
        else:
            logger.error(f"data_num error= {data_num}")

    def write_command(self, filename, memo_no):
        """
        write the selected memory address
        """
        self.str_block = ""

        with open(filename, "r") as f:
            self.str_block = f.read()

        logger.debug(f"Write the File Code= {self.str_block}")
        logger.debug(f"Number of characters= {len(self.str_block)}")
        str_tmp = ""
        int_tmp = []
        for i in range(len(self.str_block) // 2):
            str_tmp = self.str_block[i * 2] + self.str_block[i * 2 + 1]
            int_tmp.append(int(str_tmp, 16))
        logger.debug(f"int_tmp= {int_tmp}")
        logger.debug(f"int_tmp_length= {len(int_tmp)}")
        # cmd W1_memo_no_write 0x19 bus-write(ADR,cmd,1)
        bus.write_i2c_block_data(SLAVE_ADDRESS, self.W1_memo_no_write, memo_no)  # =
        # cmd W2_data_num_write 0x29 bus-write(ADR,cmd,3)
        data_num = len(int_tmp) // 4  # for test
        data_numHL = [0x31, 0x32]  # for test
        data_numHL[0] = data_num // 256
        data_numHL[1] = data_num % 256
        bus.write_i2c_block_data(SLAVE_ADDRESS, self.W2_data_num_write, data_numHL)  # =
        # cmd W3_data_write           0x39 bus-read(ADR,cmd,n)
        logger.debug(data_num)
        data_numHL = [0x31, 0x32, 0x33, 0x34]  # for test
        for i in range(data_num):
            data_numHL[0] = int_tmp[i * 4 + 0]
            data_numHL[1] = int_tmp[i * 4 + 1]
            data_numHL[2] = int_tmp[i * 4 + 2]
            data_numHL[3] = int_tmp[i * 4 + 3]
            bus.write_i2c_block_data(SLAVE_ADDRESS, self.W3_data_write, data_numHL)  # =
        # cmd W4_flash_write           0x49 bus-read(ADR,cmd,n)
        bus.write_i2c_block_data(SLAVE_ADDRESS, self.W4_flash_write, memo_no)  # =

    def trans_command(self, filename):
        """
        Send the filename(Send code)
        """

        self.str_block = ""

        with open(filename, "r") as f:
            self.str_block = f.read()

        logger.debug(f"{filename} = {self.str_block}")
        logger.debug(f"{filename} length = {len(self.str_block)}")
        str_tmp = ""
        int_tmp = []
        for i in range(len(self.str_block) // 2):
            str_tmp = self.str_block[i * 2] + self.str_block[i * 2 + 1]
            int_tmp.append(int(str_tmp, 16))
        logger.debug(int_tmp)
        logger.debug(len(int_tmp))
        # cmd W2_data_num_write 0x29 bus-write(ADR,cmd,3)
        data_num = len(int_tmp) // 4  # for test
        data_numHL = [0x31, 0x32]  # for test
        data_numHL[0] = data_num // 256
        data_numHL[1] = data_num % 256
        bus.write_i2c_block_data(SLAVE_ADDRESS, self.W2_data_num_write, data_numHL)  # =
        # cmd W3_data_write           0x39 bus-read(ADR,cmd,n)
        logger.debug(data_num)
        data_numHL = [0x31, 0x32, 0x33, 0x34]  # for test
        for i in range(data_num):
            data_numHL[0] = int_tmp[i * 4 + 0]
            data_numHL[1] = int_tmp[i * 4 + 1]
            data_numHL[2] = int_tmp[i * 4 + 2]
            data_numHL[3] = int_tmp[i * 4 + 3]
            bus.write_i2c_block_data(
                self.SLAVE_ADDRESS, self.W3_data_write, data_numHL
            )  # =
        # cmd T1_trans_start             0x59 bus-write(ADR,cmd,1)
        # memo_no = [0x00]  # for dummy
        bus.write_i2c_block_data(self.SLAVE_ADDRESS, self.T1_trans_start, [0])  # =


def start_timer():
    start_time = datetime.now()
    finish_time = start_time + timedelta(hours=3)
    delay_seconds = (finish_time - start_time).total_seconds()

    timer = threading.Timer(interval=delay_seconds, function=exe_after_3_hours)
    timer.start()

    logger.info(f"Remaining time(min): {(finish_time - datetime.now()) / 60}")

    return timer


def exe_after_3_hours():
    publish_command(topic="home/device/command", payload=10, qos=1)


memo_no = [0x00]
filename = "ch" + str(memo_no[0]) + ".data"

start_command = "command/aircon_cooler_start.data"
stop_command = "command/aircon_stop.data"
temp_24_command = "command/aircon_temp_24.data"
temp_27_command = "command/aircon_temp_27.data"
temp_29_command = "command/aircon_temp_29.data"

turn_on_ceilinglight = "command/turn_on_ceilinglight.data"
turn_off_ceilinglight = "command/turn_off_ceilinglight.data"


remote_command = Remote_Command(SLAVE_ADDRESS)

# remote_command.read_command(filename, memo_no)

# remote_command.trans_command(filename=temp_27_command)


def remote_control(ctrl_num: int):
    """_summary_

    Args:
        ctrl_num (int): _description_
        0 = cancel
        1 = turn on aircon
        2 = set temp 29 celsius
        3 = set temp 27 celsius
        4 = turn off aircon
        5 = cancel
        6 = turn on ceilinglight
        7 = turn off ceilinglight
        8 = set temp 24 celsius
        9 = set turn off 3 hour
    """
    start_command = "command/aircon_cooler_start.data"
    stop_command = "command/aircon_stop.data"
    temp_24_command = "command/aircon_temp_24.data"
    temp_27_command = "command/aircon_temp_27.data"
    temp_29_command = "command/aircon_temp_29.data"

    turn_on_ceilinglight = "command/turn_on_ceilinglight.data"
    turn_off_ceilinglight = "command/turn_off_ceilinglight.data"

    match ctrl_num:
        case 0:
            print("Cancel")
        case 1:
            remote_command.trans_command(filename=start_command)
        case 2:
            remote_command.trans_command(filename=temp_29_command)
        case 3:
            remote_command.trans_command(filename=temp_27_command)
        case 4:
            remote_command.trans_command(filename=stop_command)
        case 5:
            print("Cancel")
        case 6:
            remote_command.trans_command(filename=turn_on_ceilinglight)
        case 7:
            remote_command.trans_command(filename=turn_off_ceilinglight)
        case 8:
            remote_command.trans_command(filename=temp_24_command)
        case 9:
            start_timer()
        case 10:
            remote_command.trans_command(filename=stop_command)


if __name__ == "__main__":
    print("1 = turn on aircon")
    print("2 = set temp 29 celsius")
    print("3 = set temp 27 celsius")
    print("4 = turn off aircon")
    print("5 = cancel")
    print("6 = turn on ceilinglight")
    print("7 = turn off ceilinglight")
    print("8 = set temp 24 celsius")
    select_code = int(input())

    match select_code:
        case 1:
            remote_command.trans_command(filename=start_command)
        case 2:
            remote_command.trans_command(filename=temp_29_command)
        case 3:
            remote_command.trans_command(filename=temp_27_command)
        case 4:
            remote_command.trans_command(filename=stop_command)
        case 5:
            print("Cancel")
        case 6:
            remote_command.trans_command(filename=turn_on_ceilinglight)
        case 7:
            remote_command.trans_command(filename=turn_off_ceilinglight)
        case 8:
            remote_command.trans_command(filename=temp_24_command)
