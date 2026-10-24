import re
rows=[]
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if m: rows.append((float(m[1]),bytes.fromhex(m[2])[1:]))
t0=rows[0][0]
W=[i for i,(t,b) in enumerate(rows) if b[:2] in (bytes([4,0x11]),bytes([4,0x27])) and b[8]==9]
print(len(W))
bufs=[]
for w in W:
    buf=b''.join(r[1] for r in rows[w+1:w+10]); bufs.append((round(rows[w][0]-t0,1),rows[w][1][1],buf))
for t,c,b in bufs: print(t,hex(c),len(b))
# compare consecutive writes of same command
by={}
for t,c,b in bufs: by.setdefault(c,[]).append((t,b))
for c,l in by.items():
    for (t1,b1),(t2,b2) in zip(l,l[1:]):
        d=[(i,b1[i],b2[i]) for i in range(576) if b1[i]!=b2[i]]
        print('cmd',hex(c),t1,'->',t2,'diff',[(i,hex(x),hex(y)) for i,x,y in d][:30])
t,c,b=bufs[0]
print('first write layout (4B entries):')
for i in range(0,576,32): print(i,b[i:i+32].hex(' '))
