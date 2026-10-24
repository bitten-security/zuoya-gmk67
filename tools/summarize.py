import re,sys
rows=[]
for l in open('hidlog.txt'):
    m=re.match(r'([\d.]+) (IOCTL 0x(\w+) in\[\d+\]|  -> out\[\d+\]) (\w+)',l)
    if not m: continue
    t=float(m[1]); kind='SET' if m[3]=='b0191' else 'GET' if m[3]=='b0192' else 'RSP'
    h=m[4].rstrip('0'); h+= '0'*(len(h)%2)
    rows.append((t,kind,h))
t0=rows[0][0]; prev=None
for t,k,h in rows:
    if h in ('',): continue
    print(f'{t-t0:8.2f} {k} {h}')
print(len(rows))
