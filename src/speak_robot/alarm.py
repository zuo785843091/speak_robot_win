# -*- coding: utf-8 -*-
# 闹钟设置
from config_command import config_command
import time
import SYN7318
import logging
logging.basicConfig(level=logging.INFO)

'''
import smbus
#/dev/i2c-1
bus = smbus.SMBus(1)
'''
W = {0 : "Sun", 1 : "Mon", 2 : "Tues", 3 : "Wed", 4 : "Thur", 5 : "Fri", 6 : "Sat"}
week_dict = {"Sun" : 0, "Mon" : 1, "Tues" : 2, "Wed" : 3, "Thur" : 4, "Fri" : 5, "Sat" : 6}
class ds3231(object):

    def __init__(self):
        self.address = 0x68
        self.time_register = 0x00
        self.alarm_register = [0x07, 0x0B]
        self.control_register = 0x0E
        self.state_register = 0x0F
        self.temperature_register = 0x11
        #                sec   min   hour  week   day  mout  year
        self.now_time = [0x00, 0x47, 0x08, 0x00, 0x06, 0x08, 0x17]
        self.alarm2_time = [0x00,0x47,0x08,0x00,0x06,0x08,0x17]
        self.year = 17
        self.month = 8
        self.day = 5
        self.weekday = 'Sat'
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.time_tpye = 24
        self.get_local_time()

    def BCD_to_int(self, data):
        return (data >> 4) * 10 + (data & 0x0F)
        
    def int_to_BCD(self, data):
        return ((data // 10) << 4) + (data % 10)
    
    def get_local_time(self):
        local_tm = time.localtime()
        self.year = local_tm.tm_year
        self.month = local_tm.tm_mon
        self.day = local_tm.tm_mday
        self.weekday = W[6 - local_tm.tm_wday]
        self.hour = local_tm.tm_hour
        self.minute = local_tm.tm_min
        self.second = local_tm.tm_sec
        
'''
    def ds3231SetTime(self):
        bus.write_i2c_block_data(self.address, self.time_register, self.now_time)
        
    def ds3231ReadTime(self):
        time = bus.read_i2c_block_data(self.address, self.time_register, 7);
        self.second  = self.BCD_to_int(time[0] & 0x7F) #sec
        self.minute  = self.BCD_to_int(time[1] & 0x7F)  #min
        self.hour    = self.BCD_to_int(time[2] & 0x3F)  #hour
        self.weekday = W[time[3] & 0x07 - 1]  #week
        self.day     = self.BCD_to_int(time[4] & 0x3F)  #day
        self.month   = self.BCD_to_int(time[5] & 0x1F)  #mouth
        self.year    = self.BCD_to_int(time[6] & 0xFF) #year
        
    def ds3231ReadTemperature(self):
        temp = bus.read_i2c_block_data(self.address, self.temperature_register, 2);
        temperature = temp[0] + (temp[1] >> 6) * 0.25
        return temperature
    
    def ds3231SetAlarm1(self, hour, minute, second = 0):
        bus.write_i2c_block_data(self.address, 0x07, [second & 0x7F, minute & 0x7F, hour & 0x7F, 0x80])
    
    def ds3231SetAlarm2(self, hour, minute):
        bus.write_i2c_block_data(self.address, 0x0B, [minute & 0x7F, hour & 0x7F, 0x80])
        
    def ds3231OpenAlarm1(self):
        control = bus.read_i2c_block_data(self.address, self.control_register, 1)
        bus.write_i2c_block_data(self.address, self.control_register, [control[0] | 0x05])
        
    def ds3231OpenAlarm2(self):
        control = bus.read_i2c_block_data(self.address, self.control_register, 1)
        bus.write_i2c_block_data(self.address, self.control_register, [control[0] | 0x06])
        
    def ds3231CloseAlarm1(self):
        control = bus.read_i2c_block_data(self.address, self.control_register, 1)
        bus.write_i2c_block_data(self.address, self.control_register, [control[0] & ~0x05])
        
    def ds3231CloseAlarm2(self):
        control = bus.read_i2c_block_data(self.address, self.control_register, 1)
        bus.write_i2c_block_data(self.address, self.control_register, [control[0] & ~0x06])
    #检查时间是否可靠
    def ds3231Check_OSF(self):
        OSF_state = bus.read_i2c_block_data(self.address, self.state_register, 1);
        if OSF_state and 0x80:
            return False
        else:
            return True
        
    def ds3231Check_alarm(self, alarm_number):
        alarm_state = bus.read_i2c_block_data(self.address, self.state_register, 1);
        if alarm_state[0] & alarm_number:
            bus.write_i2c_block_data(self.address, self.state_register, [alarm_state[0] & ~alarm_number]);
            return True
        else:
            return False
'''
class alarm(ds3231, config_command):
    def __init__(self, dict_no, alarm_q):
        ds3231.__init__(self)
        self.alarm_config_path = '../config/alarm_config'
        self.file_path = 'E:/3-闹铃/'
        self.alarm_day    = [int(x) for x in self.get_config(self.alarm_config_path, 'alarm_day').split(',')]
        self.alarm_hour   = [int(x) for x in self.get_config(self.alarm_config_path, 'alarm_hour').split(',')]
        self.alarm_minute = [int(x) for x in self.get_config(self.alarm_config_path, 'alarm_minute').split(',')]
        self.alarm_flag   = [int(x) for x in self.get_config(self.alarm_config_path, 'alarm_flag').split(',')]
        self.alarm_ring_flag = self.alarm_enable = int(self.get_config(self.alarm_config_path, 'alarm_ring_flag'))
        self.alarm_enable = int(self.get_config(self.alarm_config_path, 'alarm_enable'))
        self.alarm_ring_type  = int(self.get_config(self.alarm_config_path, 'alarm_ring_type'))
        self.alarm_ring_time  = int(self.get_config(self.alarm_config_path, 'alarm_ring_time'))
        self.alarm_ring_tts   = self.get_config(self.alarm_config_path, 'alarm_ring_tts')
        self.alarm_ring_mp3   = self.get_config(self.alarm_config_path, 'alarm_ring_mp3')
        self.alarm_h = 8
        self.alarm_m = 0
        self.run_times = 1
        self.dict_no = dict_no
        self.alarm_q = alarm_q
    
    def open_alarm(self):
        self.alarm_enable = 1
        self.set_config(self.alarm_config_path, 'alarm_enable', self.alarm_enable)
        
    def close_alarm(self):
        self.alarm_enable = 0
        self.set_config(self.alarm_config_path, 'alarm_enable', self.alarm_enable)

    def pause_alarm(self):
        self.alarm_ring_flag = 0

    def set_alarm_time(self, alarm_h, alarm_m):
        self.ds3231SetAlarm2(self.int_to_BCD(alarm_h), self.int_to_BCD(alarm_m))        

    def alarm_ring(self):
        if self.alarm_ring_type == 1: #语音合成
            SYN7318.serial_tts(self.alarm_ring_tts, False)
        else: #MP3
            file_name = self.file_path + self.alarm_ring_mp3 + '.mp3'            
            SYN7318.play_mp3(file_name)

    def alarm_stop_ring(self):
        SYN7318.stop_play()

    def set_alarm(self, command_id, entry_id):
        if self.run_times == 1:
            SYN7318.serial_tts('请输入小时')
            logging.info('请输入小时')
            self.dict_no = 0x04
            self.run_times = 2
        elif self.run_times == 2:
            SYN7318.serial_tts('您输入的小时为' + str(entry_id))
            SYN7318.serial_tts('请问是否正确')
            self.alarm_h = entry_id
            self.dict_no = 0x03
            self.run_times = 3
        elif self.run_times == 3:
            if command_id == 0x01:
                self.alarm_hour[week_dict[self.weekday]] = self.alarm_h
                SYN7318.serial_tts('请输入分钟')
                logging.info('请输入分钟')
                self.dict_no = 0x04
                self.run_times = 4
            elif command_id == 0x00:
                SYN7318.serial_tts('请重新输入小时')
                logging.info('请重新输入小时')
                self.dict_no = 0x04
                self.run_times = 2
            else:
                SYN7318.serial_tts('请说正确或者不正确')
                logging.info('请说正确或者不正确')
        elif self.run_times == 4:
            SYN7318.serial_tts('您输入的分钟为' + str(entry_id))
            SYN7318.serial_tts('请问是否正确')
            self.alarm_m = entry_id
            self.dict_no = 0x03
            self.run_times = 5
        elif self.run_times == 5:
            if command_id == 0x01:
                self.alarm_minute[week_dict[self.weekday]] = self.alarm_m
                SYN7318.serial_tts('设置完毕，您的闹铃将在xx时间响起')
                logging.info('设置完毕，您的闹铃将在xx时间响起')
                self.open_alarm()
                self.dict_no = 0x03
                self.run_times = 6
            elif command_id == 0x00:
                SYN7318.serial_tts('请重新输入分钟')
                logging.info('请重新输入分钟')
                self.dict_no = 0x04
                self.run_times = 4
            else:
                SYN7318.serial_tts('请说正确或者不正确')
                logging.info('请说正确或者不正确')

    def check_alarm(self):
        self.get_local_time()
        # print(self.alarm_hour[week_dict[self.weekday]], self.hour, self.alarm_minute[week_dict[self.weekday]], self.minute)
        '''
        self.ds3231ReadTime()
        '''
        hour_error = (self.time_tpye + (self.alarm_hour[week_dict[self.weekday]] - self.hour)) % self.time_tpye
        minute_error = hour_error * 60 + self.alarm_minute[week_dict[self.weekday]] - self.minute
        minute_error = (1440 + minute_error) % 1440
        print('alarm rest minutes', minute_error)
        return minute_error

    def alarm_handle(self, error_q):
        sleep_time = 60
        ring_start_time = 0
        try:
            while True:
                if not self.alarm_q.empty():
                    print('alarm_threat end')
                    break
                if self.alarm_enable and self.alarm_flag[week_dict[self.weekday]]:
                    minute_error = self.check_alarm()
                    sleep_time = (minute_error * 60 / 30) + 5
                    if sleep_time > 60:
                        sleep_time = 60
                    if minute_error == 0:
                        self.alarm_ring_flag = 1
                        ring_start_time = time.time()
                    
                    if self.alarm_ring_flag:
                        if time.time() - ring_start_time <= self.alarm_ring_time:
                            self.alarm_ring()
                        else:
                            self.alarm_stop_ring()
                            self.alarm_ring_flag = False
                time.sleep(sleep_time)
        except BaseException as e:
            error_q.put([e, 'alarm'])
            logging.error('alarm error: %s' %(e))
'''
test_alarm = alarm(3)
test_alarm.alarm_handle()
'''

'''
test_alarm = alarm()
#test_alarm.now_time = [0x00, 0x20, 0x10, 0x00, 0x06, 0x08, 0x17]
#test_alarm.ds3231SetTime()
test_alarm.ds3231ReadTime()
temperature = test_alarm.ds3231ReadTemperature()
print('date: ', test_alarm.year, test_alarm.month, test_alarm.day, test_alarm.weekday, test_alarm.hour, test_alarm.minute, test_alarm.second)
print('temperature: ', temperature)
test_alarm.set_alarm(11, 22)
while True:
    if test_alarm.check_alarm():
        print('alarm ring')
    time.sleep(10)
'''
