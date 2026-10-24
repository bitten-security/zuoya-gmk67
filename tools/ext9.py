import re
rows=[]
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if m: rows.append((float(m[1]),bytes.fromhex(m[2])[1:]))
t0=rows[0][0]
i=[k for k,(t,b) in enumerate(rows) if b[:2]==bytes([4,0x19])][-1]
for t,b in rows[i-3:i+14]: print(round(t-t0,2),b.rstrip(b'\0').hex()[:40])
i=[k for k,(t,b) in enumerate(rows) if b[:2]==bytes([4,0x11]) and b[8]==9][-1]
for t,b in rows[i-2:i+14]: print(round(t-t0,2),b.rstrip(b'\0').hex()[:40])
