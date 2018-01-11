# -*- coding: utf-8 -*-
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr, formataddr
import poplib

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
import smtplib

from logging_config import *
import time
from config_command import config_command
import queue
email_q = queue.Queue()
email_send_q = queue.Queue()
# 输入邮件地址, 口令和POP3服务器地址:
'''
email_addr = 'speak_robot@163.com'
password = 'z785843091'
pop3_server = 'pop.163.com'
'''
email_addr = '378131766@qq.com'
password = 'gbeqvlvtfbsubhcg'
pop3_server = 'pop.qq.com'

from_email_list = ['cilizuo@163.com', '785843091@qq.com', '154007170@qq.com']

to_addr = '785843091@qq.com'
smtp_server = 'smtp.qq.com'

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr('sr <%s>' % email_addr)
    msg['To'] = _format_addr('z <%s>' % to_addr)
    msg['Subject'] = Header('robot', 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(0)
    server.login(email_addr, 'gbeqvlvtfbsubhcg')
    server.sendmail(email_addr, [to_addr], msg.as_string())
    server.quit()

def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def print_info(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)            
            print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain' or content_type=='text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))
            
def get_info(msg, indent=0):
    if indent == 0:
        head_dict = {'From' : {'name' : 1, 'addr' : 1}, 'To' : {'name' : 1, 'addr' : 1}, 'Subject' : 3}
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header=='Subject':
                    value = decode_str(value)
                    head_dict[header] = value
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)                    
                    value = u'%s <%s>' % (name, addr)
                    head_dict[header]['name'] = name
                    head_dict[header]['addr'] = addr
            #print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        msg = parts[0]
    
    content_type = msg.get_content_type()
    if content_type=='text/plain' or content_type=='text/html':
        content = msg.get_payload(decode=True)
        charset = guess_charset(msg)
        if charset:
            content = content.decode(charset)
        #print('%sText: %s' % ('  ' * indent, content + '...'))
    else:
        print('%sAttachment: %s' % ('  ' * indent, content_type))
    return(head_dict, content)

def login_email(debuglevel):
    global email_addr, password, pop3_server
    try:
        # 连接到POP3服务器:
        server = poplib.POP3_SSL(pop3_server, port=995)
        #server = poplib.POP3(pop3_server)
        # 可以打开或关闭调试信息:
        server.set_debuglevel(debuglevel)
        # 可选:打印POP3服务器的欢迎文字:
        #print(server.getwelcome().decode('utf-8'))
        # 身份认证:
        server.user(email_addr)
        server.pass_(password)
        # stat()返回邮件数量和占用空间:
        #print('Messages: %s. Size: %s' % server.stat())
        return server
    finally:
        pass
    
def logout_email(server):
    # 关闭连接:
    server.quit()
    
def check_new_emails(server):
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    #print(mails)
    # 获取最新一封邮件, 注意索引号从1开始:
    num_mails = len(mails)
    return num_mails

def read_email(server, index):
    resp, lines, octets = server.retr(index)
    # lines存储了邮件的原始文本的每一行,
    # 可以获得整个邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析出邮件:
    msg = Parser().parsestr(msg_content)
    #print_info(msg)
    head_dict, content = get_info(msg)
    
    #print('head:\r', head_dict, '\r content:\r', content)
    return head_dict, content


def delete_email(server, index):
    # 可以根据邮件索引号直接从服务器删除邮件:
    server.dele(index)


def receive_one_email():
    command = [] 
    data = []
    server = login_email(0)
    num_mails = check_new_emails(server)
    if num_mails > 0:
        head_dict, content = read_email(server, 1)
        if head_dict['From']['addr'] in from_email_list:
            command, data = config_command.get_all_command(content)
        #delete_email(server, 1)
    logout_email(server)
    return command, data

def receive_email_t(error_q):
    try:
        while True:
            if not email_send_q.empty():
                content = email_send_q.get()
                #send_email(content)
            command, data = receive_one_email()
            if len(command) > 0:
                email_q.put([command, data])
            time.sleep(10)
    except BaseException as e:
        error_q.put([e, 'email'])
        logging.error('Email error: %s' %(e))
        

def receive_email():
    server = login_email(0)
    num_mails = check_new_emails(server)
    if num_mails > 0:
        for index in range(num_mails):
            head_dict, content = read_email(server, index + 1)
            if head_dict['From']['addr'] in from_email_list:
                command, data = config_command.get_all_command(content)
            #delete_email(server, index + 1)
    logout_email(server)
'''
content = receive_one_email()
print(content)
'''