import re,collections
c=collections.Counter(); first={}
t0=None
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if not m: continue
    t=float(m[1]); t0=t0 or t
    h=bytes.fromhex(m[2])[1:].rstrip(b'\0').hex()
    k=h[:4] if h.startswith('04') else ('data'+str(len(h)//2))
    c[k]+=1; first.setdefault(k,(round(t-t0,1),h[:60]))
print(c); print(first); print(round(t-t0,1))
