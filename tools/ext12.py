import re,glob,collections
c=collections.Counter(); ex={}
for f in sorted(glob.glob('hidlog*.txt')):
    for l in open(f):
        m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
        if not m: continue
        b=bytes.fromhex(m[2])[1:]
        if b[0]==4 and b[1] not in (2,):
            k=(hex(b[1]),b[8],b[2:8].hex()); c[k]+=1; ex.setdefault(k,f)
for k,v in sorted(c.items()): print(k,v,ex[k])
