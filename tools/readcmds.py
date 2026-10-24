import hid
d=[x for x in hid.enumerate(0x05ac,0x24f) if x['usage_page']==1 and x['usage']==6 and x['interface_number']==0 and x['product_string']=='USB DEVICE'][0]
h=hid.device(); h.open_path(d['path'])
def s(*b):
    p=bytearray(65); p[1:1+len(b)]=bytes(b); h.send_feature_report(bytes(p))
def g(): return bytes(h.get_feature_report(0,65))[1:]
for cmd in (0x23,0x11,0x27,0x17,0x13):
    s(4,0x18); g(); s(4,cmd,0,0,0,0,0,0,9); print('CMD',hex(cmd),g().hex()[:24])
    prev=None
    for i in range(12):
        r=g()
        if r==prev: break
        prev=r; print(' ',i,r.hex())
    s(4,2); g(); s(4,0xf0); g()
h.close()
