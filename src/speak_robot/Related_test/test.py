# -*- coding: utf-8 -*-

import time 
import sys 
import os 
def restart_program(): 
    python = sys.executable 
    os.execl(python, python, * sys.argv) 
if __name__ == "__main__": 
    print('start...')
    #  answer = raw_input("Do you want to restart this program ? ") 
    #  if answer.strip() in "y Y yes Yes YES".split(): 
    #    restart_program() 
    print("3秒后,程序将结束...")
    time.sleep(3) 
    restart_program()
  
'''
from SYN7318 import *
from multiprocessing import Process, Queue
import os, time
import pi_email
# 子进程要执行的代码
def run_proc(name):
    print('Run child process %s (%s)...' % (name, os.getpid()))

if __name__=='__main__':
    q = Queue()
    
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_proc, args=('test',))
    print('Child process will start.')
    p.start()
    while True:
        if not q.empty():
            print(q.get())
        time.sleep(1)
    p.join()
    print('Child process end.')
'''
'''
import threading
import queue
import time
import random
q = queue.Queue()   
class thread(object):
    def __init__(self):
        self.t = 0
        self.j = 0
        
    def run(self):  
        while True:
            time.sleep(self.j)
            self.t += 1
            self.j = random.randint(1, 3)
            t = [1, 2]
            q.put(t)
        
def main():    
    m_thread = thread()
    reveive_status_t = threading.Thread(target=m_thread.run, name='receive_status_Thread');
    reveive_status_t.start()
    
    while True:
        
        if not q.empty():
            c = q.get()
            print(c)
            print(m_thread.t, m_thread.j)
    reveive_status_t.join()
    
main()
'''
'''
class MyThread(threading.Thread):
    def __init__(self, q, t, j):
        super(MyThread, self).__init__()
        self.q = q
        self.t = t
        self.j = j

    def run(self):
        time.sleep(self.j)
        self.q.put('I an the %d threading, I sleeped %d seconds, The corrent time is %s' % (self.t, self.j, time.ctime()))

count = 0
threads = []
for i in range(15):
    j = random.randint(1, 8)
    threads.append(MyThread(q, i, j))
for mt in threads:
    mt.start()
print('start time: ', time.ctime())
while True:
    if not q.empty():
        print(q.get())
        count += 1
    if count == 15:
        break
'''
'''
from  multiprocessing import Process,Queue
import os,time
def f(q,n):
    q.put([n,'hello'])
if __name__ == '__main__':
    
    q=Queue()
    
    for i in range(5):
        p=Process(target=f,args=(q,i))
        p.start()
    time.sleep(1)
    
    for i in range(q.qsize()):
        print(q.get())
    p.join()
'''

'''
import re
class alarm(object):    
    def __init__(self):        
        self.alarm_config_path = 'E:/Eclipse_python3/speak_robot/src/config/alarm_config'
        self.alarm_day    = [int(x) for x in self.get_config('alarm_day').split(',')]
        self.alarm_hour   = [int(x) for x in self.get_config('alarm_hour').split(',')]
        self.alarm_minute = [int(x) for x in self.get_config('alarm_minute').split(',')]
        self.alarm_flag   = [int(x) for x in self.get_config('alarm_flag').split(',')]
        self.enable       = int(self.get_config('alarm_enable'))
        self.alarm_runing_type   = int(self.get_config('alarm_runing_type'))
        self.alarm_runing_tts   = self.get_config('alarm_runing_tts')
        self.alarm_runing_mp3   = self.get_config('alarm_runing_mp3')
    
    def get_config(self, paramenter_name):
        paramenter_data = []
        with open(self.alarm_config_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line[0] != '#' and line[0] != '\n':
                    line = line.strip()
                    line_list = re.split(r':', line)
                    if line_list[0] == paramenter_name:
                        paramenter_data = line_list[1]
                        break
        return paramenter_data
    
    def set_config(self, paramenter_name, value):
        lines = []
        with open(self.alarm_config_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line_list = re.split(r':', line)
                if line_list[0] == paramenter_name:
                    if type(value) != type(line_list):
                        value = [value]
                    line_list[1] = value
                    line = line_list[0] + ':' + ', '.join(map(str,line_list[1])) + '\n'
                lines.append(line)
        with open(self.alarm_config_path, 'w', encoding='utf-8') as f:
            s = ''.join(lines)
            f.write(s)

test_alarm = alarm()
test_alarm.set_config('alarm_day', [0, 1, 2, 3, 4, 5, 6])
test_alarm.set_config('alarm_runing_type', 2)
'''
'''
print(test_alarm.alarm_day)
print(test_alarm.alarm_hour)
print(test_alarm.alarm_minute)
print(test_alarm.alarm_flag)
print(test_alarm.enable)
print(test_alarm.alarm_ring_type)
print(test_alarm.alarm_runing_tts)
print(test_alarm.alarm_runing_mp3)
'''