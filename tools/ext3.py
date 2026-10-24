import re
t0=None;last=None
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if not m: continue
    t=float(m[1]); t0=t0 or t
    h=bytes.fromhex(m[2])[1:].rstrip(b'\0').hex()
    if h.startswith('04f5') or h=='0402' or h=='': continue
    if h==last: continue
    last=h
    print(f'{t-t0:7.2f} {h}')
