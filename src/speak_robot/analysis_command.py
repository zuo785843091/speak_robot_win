# -*- coding: utf-8 -*
# Email 命令解析
import re
import network
import SYN7318
import pi_email


#email command
SYN7318_command = ['set_vol_level', 'add_vol_levle', 'reduce_vol_levle', 'set_vol_name']

alarm_command = ['set_alarm_time', 'set_alarm_day', 'set_alarm_hour', 
                 'set_alarm_minute', 'set_alarm_stop', 'set_alarm_open',
                 'set_alarm_ring_type', 'set_alarm_ring_tts', 'set_alarm_ring_mp3',
                 'set_alarm_ring_time', 'check_alarm_status']

song_command = ['set_song_mode', 'set_song_index', 'set_song_name'
                'set_song_stop', 'set_song_start', 'check_song_status']

story_command = ['set_story_mode', 'set_story_index', 'set_story_name'
                'set_story_stop', 'set_story_start', 'check_story_status']

network_command = ['check_network', 'set_ip', 'set_mark', 'set_mast', 'set_DNS',
                   'set_network_mode', 'set_network_up', 'set_network_down', 
                   'set_network_web_up', 'set_network_web_down']

wireless_command = ['check_wireless', 'scan_wireless', 'set_wireless_up', 
                    'set_wireless_down', 'set_wireless_connect', 'set_wireless_disconnect',
                    'set_wireless_web_up', 'set_wireless_web_down']

online_speak_command = ['sample_rate', 'frame_type', 'num_channels', 
                        'chunk_duration_ms', 'num_window_chunks_start', 
                        'num_window_chunks_end', 'start_voice_parameter',
                        'end_voice_parameter', 'mute_time', 'voice_time',
                        'TE_MIN', 'TE_MAX', 'TZ_MIN', 'TZ_MAX', 
                        'TO_MIN', 'To_MAX', 'check_online_speak_statues']

sys_command = ['start_tts', 'set_']

def set_online_speak_command(command, data, pi_sys):
    pi_sys.set_config(pi_sys.sys_config_path, command, data)

def set_SYN7318(command, data, pi_sys):
    print(command, data)
    if command == 'set_vol_level':
        if data.test_isdigit():
            if int(data) in range(1, 10):
                vol_level = int(data)
                pi_sys.config_data['vol_level'] = str(vol_level)
                SYN7318.serial_vol_level(vol_level)
                pi_sys.set_config(pi_sys.sys_config_path, 'vol_level', vol_level)
    elif command == 'add_vol_levle':
        vol_level = int(pi_sys.config_data['vol_level']) + 1
        pi_sys.config_data['vol_level'] = str(vol_level)
        SYN7318.serial_vol_level(vol_level)
        pi_sys.set_config(pi_sys.sys_config_path, 'vol_level', vol_level)
    elif command == 'reduce_vol_levle':
        vol_level = int(pi_sys.config_data['vol_level']) - 1
        pi_sys.config_data['vol_level'] = str(vol_level)
        SYN7318.serial_vol_level(vol_level)
        pi_sys.set_config(pi_sys.sys_config_path, 'vol_level', vol_level)
    elif command == 'set_vol_name':
        if data in SYN7318.sound_people_dict:
            pi_sys.config_data['vol_name'] = data
            SYN7318.serial_tts(SYN7318.sound_people_dict[data])
            pi_sys.set_config(pi_sys.sys_config_path, 'vol_name', data)

def set_alarm(command, data, pi_alarm):
    if command == 'set_alarm_time':
        data_list = re.split(r',', data)
        if len(data_list) == 2:
            if data_list[0] >= 0 and data_list[0] <= 24 and data_list[1] > 0 and data_list[1] < 60:
                hour = int(data_list[0])
                minute = int(data_list[0])
                pi_alarm.alarm_hour = [hour, hour, hour, hour, hour, hour, hour]
                pi_alarm.alarm_minute = [minute, minute, minute, minute, minute, minute, minute]
        elif len(data_list) > 2:
            if data_list[0] >= 0 and data_list[0] <= 24 and data_list[1] > 0 and data_list[1] < 60:
                hour = int(data_list[0])
                minute = int(data_list[0])
                for day in data_list[1:]:
                    if int(day) in range(7):
                        pi_alarm.alarm_hour = [hour, hour, hour, hour, hour, hour, hour]
                        pi_alarm.alarm_minute = [minute, minute, minute, minute, minute, minute, minute]
    if command == 'set_alarm_day':
        on_off_dict = {'on' : 1, 'off' : 0}
        data_list = re.split(r',', data)
        if data_list[0] == 'on' or data_list[0] == 'off':
            for day in data_list[1:]:
                if day.test_isdigit():
                    if int(day) in range(7):
                        pi_alarm.alarm_flag[int(day)] = on_off_dict[data_list[0]]
    elif command == 'set_alarm_hour':
        data_list = re.split(r',', data)
        if data_list[0] >= 0 and data_list[0] <= 24:
            hour = int(data_list[0])
            if len(data_list[1:]) > 0:
                for day in data_list[1:]:
                    if int(day) in range(7):
                        pi_alarm.alarm_hour[int(day)] = hour
            else:
                pi_alarm.alarm_hour = [hour, hour, hour, hour, hour, hour, hour]        
    elif command == 'set_alarm_minute':
        data_list = re.split(r',', data)
        if data_list[0] >= 0 and data_list[0] <= 60:
            minute = int(data_list[0])
            if len(data_list[1:]) > 0:
                for day in data_list[1:]:
                    if day.test_isdigit():
                        if int(day) in range(7):
                            pi_alarm.alarm_minute[int(day)] = minute
            else:
                pi_alarm.alarm_minute = [minute, minute, minute, minute, minute, minute, minute]
    elif command == 'set_alarm_stop':
        pi_alarm.close_alarm()
    elif command == 'set_alarm_open':
        pi_alarm.open_alarm()
    elif command == 'set_alarm_ring_type':
        if data.test_isdigit():
            if int(data) in range(1,3):
                pi_alarm.alarm_ring_type = int(data)
    elif command == 'set_alarm_ring_tts':
        pi_alarm.alarm_ring_tts = data
    elif command == 'set_alarm_ring_mp3':
        pi_alarm.alarm_ring_mp3 = data
    elif command == 'set_alarm_ring_time':
        if data.test_isdigit():
            if int(data) in range(5 * 60):
                pi_alarm.alarm_ring_time = int(data)
    elif command == 'check_alarm_status':
        alarm_status = 'alarm_day %s \r\n' %str(pi_alarm.alarm_day) + \
                       'alarm_hour %s \r\n' %str(pi_alarm.alarm_hour) + \
                       'alarm_minute %s \r\n' %str(pi_alarm.alarm_minute) + \
                       'alarm_flag %s \r\n' %str(pi_alarm.alarm_flag) + \
                       'alarm_enable %d \r\n' %pi_alarm.alarm_enable + \
                       'alarm_ring_type %d \r\n' %pi_alarm.alarm_ring_type + \
                       'alarm_ring_time %d s\r\n' %pi_alarm.alarm_ring_time + \
                       'alarm_ring_tts %s \r\n' %pi_alarm.alarm_ring_tts + \
                       'alarm_ring_mp3 %s \r\n' %pi_alarm.alarm_ring_mp3
        pi_email.email_send_q.put(alarm_status)
        #pi_email.send_email(alarm_status)
        #send alarm status to email
    print(command, data)

def set_song(command, data, song):
    if command == 'set_song_mode':
        if data.test_isdigit():
            if int(data) in range(6):
                song.play_mode = int(data)
                song.set_config(song.play_mode, 'play_mode', song.play_mode)
    elif command == 'set_song_index':
        if data.test_isdigit():
            if int(data) in range(song.file_number+1):            
                song.index = int(data)
                song.set_config(song.index, 'index', song.index)
                song.play_flag = True
    elif command == 'set_song_name':
        if data in song.list:
            file_name = song.file_path + data + '.mp3'
            SYN7318.play_mp3(file_name, True)
    elif command == 'set_song_stop':
        song.stop_play()
    elif command == 'set_song_start':
        song.play_flag = True
    elif command == 'check_song_status':
        song_status = 'index %d \r\n' %song.index + \
                       'play_mode %s \r\n' %song.play_mode + \
                       'list %s \r\n' %str(song.list) + \
                       'file_number %d \r\n' %song.file_number + \
                       'play_flag %d \r\n' %song.play_flag

        pi_email.email_send_q.put(song_status)
        #pi_email.send_email(alarm_status)
    SYN7318.logging.info('set_song\r command: %s data: %s' %(command, data))

def set_story(command, data, story):
    if command == 'set_story_mode':
        if len(data) > 0 and int(data[0]) in range(6):
            story.play_mode = int(data[0])
            story.set_config(story.play_mode, 'play_mode', story.play_mode)
    elif command == 'set_story_index':
        if data.test_isdigit():
            if int(data) in range(story.file_number+1):            
                story.index = int(data)
                story.set_config(story.index, 'index', story.index)
                story.play_flag = True
    elif command == 'set_story_name':
        if data in story.list:
            file_name = story.file_path + data + '.mp3'
            SYN7318.play_mp3(file_name, True)
    elif command == 'set_story_stop':
        story.stop_play()
    elif command == 'set_story_start':
        story.play_flag = True
    elif command == 'check_story_status':
        story_status = 'index %d \r\n' %story.index + \
                       'play_mode %s \r\n' %story.play_mode + \
                       'list %s \r\n' %str(story.list) + \
                       'file_number %d \r\n' %story.file_number + \
                       'play_flag %d \r\n' %story.play_flag

        pi_email.email_send_q.put(story_status)
        #pi_email.send_email(alarm_status)
    
    print('set_story')
    print(command, data)

def set_network(command, data):
    print(command, data)
    if command == 'check_network':
        network_status = network.check_network_status()
        #发送email返回网络状态
        pi_email.send_email(network_status)
    elif command == 'set_network_mode':
        if data == 'DHCP':
            network.set_dhcp('eth0')
        elif data == 'manuel':
            pass
    elif command == 'set_network_up':
        if data[0] == 'e':
            network.enable_interface(data)
        else:
            network.enable_interface('eth0')
    elif command == 'set_network_down':
        if data[0] == 'e':
            network.disable_interface(data)
        else:
            network.disable_interface('eth0')        
    elif command == 'set_ip':
        network.set_ip_addresses('eth0', data)
    elif command == 'set_mast':
        pass
    elif command == 'set_DNS':
        network.set_name_servers(data)
    elif command == 'set_network_web_up':
        pass
    elif command == 'set_network_web_down':
        pass
    
def set_wireless(command, data):
    print(command, data)
    if command == 'check_wireless':
        wireless_status = network.check_wireless_status()
        #发送email返回网络状态
        pi_email.send_email(wireless_status)
    elif command == 'scan_wireless':
        ssid = network.get_ssids(data)
        #发送email返回网络状态
        pi_email.send_email(ssid)
    elif command == 'set_wireless_up':
        if data[0] == 'w':
            network.enable_interface(data)
        else:
            network.enable_interface('wlan0')
    elif command == 'set_wireless_down':
        if data[0] == 'w':
            network.disable_interface(data)
        else:
            network.disable_interface('wlan0')
    elif command == 'set_wireless_connect':
        data_list = re.split(r',', data)
        if len(data_list) >= 2:
            interface_name = 'wlan0'
            ssid = data_list[0]
            key = data_list[1]
            network.connect_wireless_with_wpa(interface_name, ssid, key)
    elif command == 'set_wireless_disconnect':
        network.disconnect_wireless('wlan0')
    elif command == 'set_wireless_web_up':
        pass
    elif command == 'set_wireless_web_down':
        pass


def set_sys(command, data):
    print(command, data)
    if command == 'start_tts':
        SYN7318.serial_tts(data)
    elif command == 'set_':
        pass

def analysis_content(command, data, pi_sys, mp3, pi_alarm):
    for i in range(len(command)):
        if command[i] in SYN7318_command:
            set_SYN7318(command[i], data[i], pi_sys)
        elif command[i] in alarm_command:
            set_alarm(command[i], data[i], pi_alarm)
        elif command[i] in song_command:
            set_song(command[i], data[i], mp3)
        elif command[i] in story_command:
            set_story(command[i], data[i], mp3)
        elif command[i] in network_command:
            set_network(command[i], data[i])
        elif command[i] in wireless_command:
            set_wireless(command[i], data[i])
        elif command[i] in sys_command:
            set_sys(command[i], data[i])
        