import re
rows=[]
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
    if m: rows.append((float(m[1]),bytes.fromhex(m[2])[1:]))
t0=rows[0][0]
for i,(t,b) in enumerate(rows):
    if b[:2]==bytes([4,0x15]) and b[8]==9 and t-t0>90:
        pages=[r[1] for r in rows[i+1:i+10]]
        print('MACRO WRITE at',round(t-t0,1))
        for n,p in enumerate(pages): print(n,p.hex())
        break

buf=b''.join(pages)
print(len(buf),buf[:2].hex())
body=buf[400:]
print(body[:80].hex(' '))
print([ (i,hex(x)) for i,x in enumerate(buf) if x][:60])
