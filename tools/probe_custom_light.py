import hid,time,sys
fmt=sys.argv[1]
d=[x for x in hid.enumerate(0x05ac,0x24f) if x['usage_page']==1 and x['usage']==6 and x['interface_number']==0 and x['product_string']=='USB DEVICE'][0]
h=hid.device(); h.open_path(d['path'])
def s(b):
    p=bytearray(65); p[1:1+len(b)]=bytes(b); h.send_feature_report(bytes(p)); time.sleep(0.03); h.get_feature_report(0,65)
data=bytearray(576)
keys={1:(255,0,0),38:(0,255,0),56:(0,0,255)}   # Esc red, Q green, A blue (light_index)
for idx,(r,g,b) in keys.items():
    if fmt=='A': data[idx*3:idx*3+3]=bytes((r,g,b))
    else: data[idx*4:idx*4+4]=bytes((idx,r,g,b))
data[574:576]=b'\xaa\x55'
s([4,0x18]); s([4,0x23,0,0,0,0,0,0,9])
for i in range(9): s(list(data[i*64:(i+1)*64]))
s([4,0xf0])
s([4,0x18]); s([4,0x13,0,0,0,0,0,0,1]); s([0x80,0xff,0,0,0,0,0,0,1,0x0f,0x0f,0,0,0,0xaa,0x55]); s([4,0xf0])
h.close(); print('sent',fmt)
