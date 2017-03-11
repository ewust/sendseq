#!/usr/bin/python

import socket
import time
import struct
import sys
from optparse import OptionParser
from threading import Thread




parser = OptionParser()
parser.add_option("-p", "--port", dest="port", default=8888,
                help="port to listen on or connect to")
parser.add_option("-c", "--connect", dest="connect",
                action="store_true", default=False, help="connect to remote host")
parser.add_option("-H", "--host", dest="host",
                default="127.0.0.1", help="remote host to connect to or bind on")
parser.add_option("-s", "--send", dest="send",
                action="store_true", default=False, help="send data")

(options, args) = parser.parse_args()

connect = options.connect
send = options.send
port = int(options.port)
host = options.host

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

conn = s

if connect:
    s.connect((host, port))
    print 'connected'
else:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    print 'Connection from', addr



last = time.time()
last_n = 0
last_buf = ''
extra = ''
#s.send('HELLO')

last_time = time.time()

def occasional_print(n, send=False):
    global last_time
    if (n % (16*1024)) == 0:
        now = time.time()
        bw = (16*1024)/(now - last_time)
        print '%s%.06f %s %08x   %.3f MB/s' % ('  ' if send else '', now, '-sent->' if send else '<-recv-', n, bw/1000000)
        last_time = now


BUF_SIZE = 1024
SEND_SIZE = 1024*1024*20    # 20MB


def send_thread(conn, delay):
    ##### SEND
    global SEND_SIZE, BUF_SIZE
    n = 0
    for i in xrange(SEND_SIZE/(BUF_SIZE/4)):
        buf = ''
        for j in xrange(BUF_SIZE/4):
            n += 1
            buf += struct.pack('!I', n)

            occasional_print(n, True)

        conn.sendall(buf)
        time.sleep(delay)

    conn.shutdown(socket.SHUT_WR)


thread = None
if send:
    thread = Thread(target=send_thread, args = (conn, 0))
    thread.start()
    #thread.join()


##### RECEIVE
extra = ''
last_buf = ''
last_n = 0
while True:
    buf = conn.recv(BUF_SIZE)
    buf = extra + buf
    if (buf == ''):
        print 'Closed at %08x' % last_n
        break
    for i in xrange(len(buf)/4):
        n, = struct.unpack('!I', buf[4*i:4*i+4])
        #if n == 0x1000:
            #print 'Calling shutdown...'
            #conn.shutdown(1)
            #time.sleep(5)
        if n != (last_n + 1) and n != 0:
            print '=========ERROR: expected %08x got %08x at offset %d (len %d)' % (last_n+1, n, 4*i, len(buf))
            print ''
            print '----last buf:'
            print last_buf.encode('hex')
            print '----this buf:'
            print buf.encode('hex')
            sys.exit(1)
        last_n = n

        occasional_print(n)
    last_buf = buf
    extra = ''
    if (len(buf)%4) != 0:
        extra = buf[-(len(buf) % 4):]

if thread is not None:
    thread.join()
