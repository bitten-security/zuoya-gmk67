import re
rows=[]
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if m: rows.append((float(m[1]),bytes.fromhex(m[2])[1:]))
t0=rows[0][0]
W=[i for i,(t,b) in enumerate(rows) if b[:2]==bytes([4,0x11]) and b[8]==9]
for w in W:
    buf=b''.join(r[1] for r in rows[w+1:w+10])
    print(round(rows[w][0]-t0,1),[(i//4,i%4,hex(x)) for i,x in enumerate(buf[:574]) if x])
