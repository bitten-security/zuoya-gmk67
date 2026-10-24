import time
from gmk67.protocol import Keyboard
from gmk67.audio import Volume
probes = {39:(3,0xe9,0,0), 40:(3,0,0xe9,0), 41:(4,0xe9,0,0), 42:(4,0,0xe9,0), 44:(5,0xe9,0,0), 43:(2,0,0x1a,0)}
k=Keyboard(); k.open()
table=bytearray(576)
for idx,e in probes.items(): table[idx*4:idx*4+4]=bytes(e)
table[574:576]=b"\xaa\x55"
empty=bytearray(576); empty[574:576]=b"\xaa\x55"
for cmd,data in ((0x11,table),(0x27,empty)):
    k._send([4,0x18]); k._send([4,cmd,0,0,0,0,0,0,9])
    for i in range(9): k._send(list(data[i*64:(i+1)*64]))
    k._send([4,0xF0])
k.close()
print('written: W=[3,e9,0,0] E=[3,0,e9,0] R=[4,e9,0,0] T=[4,0,e9,0] U=[5,e9,0,0] Y=[2,0,w]', flush=True)
v=Volume(); last=None; t0=time.time()
while time.time()-t0<40:
    s=v.read()
    if s!=last: print(f'{time.time()-t0:5.1f}s volume/mute = {s}', flush=True); last=s
    time.sleep(0.1)
