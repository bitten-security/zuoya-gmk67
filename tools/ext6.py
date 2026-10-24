import re
rows=[]
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if m: rows.append((float(m[1]),bytes.fromhex(m[2])[1:]))
t0=rows[0][0]
writes=[i for i,(t,b) in enumerate(rows) if b[:2]==bytes([4,0x15]) and b[8]==9]
print(len(writes),'writes')
for w in (writes[-1],):
    buf=b''.join(r[1] for r in rows[w+1:w+10])
    print('table',[int.from_bytes(buf[i:i+2],'little') for i in range(0,16,2)])
    body=buf[400:]
    end=len(body.rstrip(b'\0'))
    print(body[:end].hex(' '))
    for i in range(0,end,8): print(i, body[i:i+8].hex(' '))
