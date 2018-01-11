# -*- coding: utf-8 -*-
from config_command import config_command
import network

class pi_system(config_command):
    def __init__(self):
        self.sys_config_path = '../config/sys_config'
        self.cpu_temperature = self.get_cpu_temperature()
        self.config_data = self.get_all_config(self.sys_config_path)
        self.time = 0
        self.net_flag = network.check_network()

    def get_cpu_temperature(self):
        return 50
        '''
        with open("/sys/class/thermal/thermal_zone0/temp") as fd:
            temp = float(fd.read()) / 1000
            return temp
        '''

'''
pi = pi_system()
print(pi.config_data)
print(pi.cpu_temperature)
print(pi.get_config(pi.sys_config_path, 'vol_level'))
'''