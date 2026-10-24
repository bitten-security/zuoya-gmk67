import re
t0=None
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if not m: continue
    t=float(m[1]); t0=t0 or t
    h=bytes.fromhex(m[2])[1:].rstrip(b'\0').hex()
    if h.startswith('0413') or (len(h)==32 and h.endswith('aa55')):
        print(f'{t-t0:7.2f} {h}')
