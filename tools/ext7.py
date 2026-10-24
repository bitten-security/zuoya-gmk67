import re,collections
c=collections.Counter(); first={}
t0=None
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if not m: continue
    t=float(m[1]); t0=t0 or t
    b=bytes.fromhex(m[2])[1:]
    if b[0]==4:
        k=(hex(b[1]),b[8]); c[k]+=1; first.setdefault(k,round(t-t0,1))
for k,v in sorted(c.items()): print(k,v,first[k])
