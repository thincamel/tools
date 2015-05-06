#coding: utf-8

import os

## block cc攻击 的ip

CMD = "netstat -ntup | grep -v SYN |awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr"
MAX_CONN = 50


def block_ip():

    lines = os.popen(CMD).readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        conn_num, ip = line.split()
        if int(conn_num) > MAX_CONN:
            if ip.startswith('127.0.0'):
                print '内网ip:%s,conn:%s' % (ip, conn_num)
            elif ip.startswith('10.'):
                print '内网ip:%s,conn:%s' % (ip, conn_num)
            else:
                print 'ip:%s,conn:%s' % (ip, conn_num)
                cmd = "iptables -A INPUT -s %s -j  DROP" % ip
                print cmd
                os.system(cmd)
        else:
            return

if __name__ == "__main__":

    block_ip()