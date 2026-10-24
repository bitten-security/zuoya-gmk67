import re,collections
c=collections.Counter(); ex={}; first={}
t0=None
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) +(IOCTL 0x(\w+) in\[(\d+)\]|-> out\[(\d+)\])(?: (\w+))?',l)
    if not m or not m[6]: continue
    t0=t0 or float(m[1])
    try: b=bytes.fromhex(m[6])
    except ValueError: continue
    k=(m[3] or 'out', m[4] or m[5], b[:3].hex())
    c[k]+=1; ex.setdefault(k,b.rstrip(b'\0').hex()[:90]); first.setdefault(k,round(float(m[1])-t0,1))
for k,v in c.most_common(40): print(v,first[k],k,ex[k])

