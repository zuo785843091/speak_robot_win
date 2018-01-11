#!/usr/bin/python3
# -*- coding: utf-8 -*
"""
网络设置脚本
在debian wheezy环境下测试通过
依赖命令：ip, iw, wpa_supplicant, wpa_cli, dhclient
注意：
- /etc/network/interfaces里面仅保留lo设备配置
- 与Gnome Network Manager/Wicd是否冲突未知
"""

import os
import sys
import traceback

import network as net


def test(v):
    test.result = v
    return v


def select_interface(interfaces):
    """
    选择一个已知接口
    返回接口名
    直接回车返回空字符串
    """
    while True:
        name = input('Enter interface name: ')
        if name == '' or name in interfaces:
            return name

def connect_wireless(interface_name):
    """
    连接无线
    """
    ssid = None
    while True:
        ssid = input('Enter SSID, RETURN for scanning: ')
        if not ssid:
            for s in net.get_ssids(interface_name):
                print(s)
        else:
            break

    sec = input('Select security method Open/WEP/WPA [0,1,2]: ')
    if sec == '0':
        net.connect_wireless(interface_name, ssid)
    elif sec == '1':
        keys = input('Enter comma separated keys: ').split(',')
        net.connect_wireless_with_wep(interface_name, ssid, keys)
    elif sec == '2':
        key = input('Enter key: ')
        net.connect_wireless_with_wpa(interface_name, ssid, key)

def setup_ip_gateway_dns(interface_name):
    """
    手工设置IP地址、默认网关和DNS
    """
    if test(input('Enter comma separated ip addresses: ')):
        ip_addresses = test.result.split(',')
        net.set_ip_addresses(interface_name, ip_addresses)
    if test(input('Enter gateway address: ')):
        ip_address = test.result
        net.set_default_route(interface_name, ip_address)
    if test(input('Enter comma separated dns addresses: ')):
        name_servers = test.result.split(',')
        net.set_name_servers(name_servers)

if __name__ == '__main__':
    # 提升到root权限
    if os.geteuid():
        args = [sys.executable] + sys.argv
        # 下面两种写法，一种使用su，一种使用sudo，都可以
        #os.execlp('su', 'su', '-c', ' '.join(args))
        os.execlp('sudo', 'sudo', *args)

    # 显示根菜单
    while True:
        try:
            interfaces = net.get_interfaces()

            #os.system('clear')
            net.print_state(interfaces, net.get_default_route(), net.get_name_servers())
        except Exception as ex:
            traceback.print_exc()
            break

        print('Root Menu:')
        print('    0 - Quit')
        print('    1 - cleanup all settings')
        print('    2 - enable interface')
        print('    3 - disable interface')
        print('    4 - connect interface')
        print('    5 - disconnect interface')
        print('    6 - setup ip, gateway and dns using dhcp')
        print('    7 - setup ip, gateway and dns manually')
        print('    8 - load preset')
        print('    9 - get ssids')
        print()
        #break
        try:
            choice = input('Enter your choice: ')
            if choice == '0':
                break
            elif choice == '1':
                if input('Are you sure? [y/n]: ').lower() == 'y':
                    net.cleanup_all(interfaces)
            elif choice in ('2', '3', '4', '5', '6', '7', '9') and test(select_interface(interfaces)):
                name = test.result
                if choice == '2':
                    if not interfaces[name]['enabled']:
                        net.enable_interface(name)
                elif choice == '3':
                    if interfaces[name]['enabled']:
                        if interfaces[name]['connected'] and interfaces[name]['wireless']:
                            net.disconnect_wireless(name)
                        net.disable_interface(name)
                elif choice == '4':
                    if interfaces[name]['enabled'] and interfaces[name]['wireless'] and (
                        not interfaces[name]['connected']):
                        connect_wireless(name)
                elif choice == '5':
                    if interfaces[name]['connected'] and interfaces[name]['wireless']:
                        net.disconnect_wireless(name)
                elif choice == '6':
                    if interfaces[name]['connected']:
                        net.set_dhcp(name)
                elif choice == '7':
                    setup_ip_gateway_dns(name)
                elif choice == '9':
                    ssids = net.get_ssids(name)
                    print(ssids)
        except KeyboardInterrupt as ex:
            print()
            break
        except Exception as ex:
            traceback.print_exc()
            input('Press any key to continue...')
