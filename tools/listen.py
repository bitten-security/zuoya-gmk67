import hid,time
hs=[]
for d in hid.enumerate(0x05ac,0x24f):
    if d['usage_page'] in (0xffff,0xffb5,0x1) and d['usage'] in (1,0x80) and d['interface_number']>=1 or d['usage_page'] in (0xffff,0xffb5,0xc):
        try:
            h=hid.device(); h.open_path(d['path']); h.set_nonblocking(True)
            hs.append((d['product_string'],hex(d['usage_page']),hex(d['usage']),h))
        except Exception as e: print('skip',d['product_string'],hex(d['usage_page']),e)
print(len(hs),'opened',flush=True)
t0=time.time()
while time.time()-t0<25:
    for n,u,us,h in hs:
        r=h.read(64)
        if r: print(f'{time.time()-t0:6.1f} {n} {u}/{us} {bytes(r).hex()}',flush=True)
    time.sleep(0.01)
