# -*- coding: utf-8 -*
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

from_addr = 'cilizuo@163.com'
password = '==785843091'
to_addr = '378131766@qq.com'
smtp_server = 'smtp.163.com'

msg = MIMEText('check_song_status', 'plain', 'utf-8')
msg['From'] = _format_addr('speak_robot <%s>' % from_addr)
msg['To'] = _format_addr('z <%s>' % to_addr)
msg['Subject'] = Header('test_email', 'utf-8').encode()

server = smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(0)
server.login(from_addr, password)
server.sendmail(from_addr, [to_addr], msg.as_string())
server.quit()
