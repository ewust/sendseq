#!usr/bin/python

import socket
import time
import struct
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

s.connect(('127.0.0.1', 10500))
print 'connected'
last = time.time()
last_n = 0
last_buf = ''
extra = ''
s.send('HELLO')
while True:
    buf = s.recv(256)
    buf = extra + buf
    for i in xrange(len(buf)/4):
        n, = struct.unpack('!I', buf[4*i:4*i+4])
        if n != (last_n + 1) and n != 0:
            print '============ERROR: expected %08x got %08x at offset %d (len %d)' % (last_n+1, n, 4*i, len(buf))
            print ''
            print '----last buf:'
            print last_buf.encode('hex')
            print '----this buf:'
            print buf.encode('hex')
            sys.exit(1)
        last_n = n

        if (n % (256*1024)) == 0:
            now = time.time()
            bw = (256*1024*4)/(now - last)
            print '%.06f ---> %08x   %.3f MB/s' % (now, n, bw/1000000)
            last = now
    last_buf = buf
    extra = ''
    if (len(buf)%4) != 0:
        extra = buf[-(len(buf) % 4):]

