# sendseq

sendseq produces a sequence of 4-byte integers, encoded in big endian, and
sends/receives them over a network socket. In hex, this ends up sending
`00 00 00 00   00 00 00 01   00 00 00 02   00 00 00 03 ...`

Connect/Listen mode: determines if the instance will connect to or listen for
incomming connections.

Send/Receive mode: determines if the instance will send the sequence or receives
the sequence.


Listening server that will receive data when it is connected to:
```
./seq.py
```

Connecting client that will send data when it connects:
```
./seq.py -c -s
```
