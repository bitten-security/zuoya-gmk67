import re,glob
for f in sorted(glob.glob('hidlog*.txt')):
    rows=[]
    for l in open(f):
        m=re.match(r'([\d.]+) IOCTL 0xb0191 in\[65\] (\w+)',l)
        if m: rows.append((float(m[1]),bytes.fromhex(m[2])[1:]))
    if not rows: continue
    t0=rows[0][0]
    for i,(t,b) in enumerate(rows):
        if b[:2]==bytes([4,0x17]):
            d=rows[i+1][1]
            print(f, round(t-t0,1), [(j,hex(x)) for j,x in enumerate(d) if x])
