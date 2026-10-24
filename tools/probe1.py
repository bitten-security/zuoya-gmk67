import hid,time,sys
d=[x for x in hid.enumerate(0x05ac,0x24f) if x['usage_page']==1 and x['usage']==6 and x['interface_number']==0 and x['product_string']=='USB DEVICE'][0]
h=hid.device(); h.open_path(d['path'])
def s(b):
    p=bytearray(65); p[1:1+len(b)]=bytes(b); h.send_feature_report(bytes(p)); time.sleep(0.03); h.get_feature_report(0,65)
def light(mode,r=0xff,g=0,b=0,bright=0x10,speed=0x0b,x=0,y=0):
    s([4,0x18]); s([4,0x13,0,0,0,0,0,0,1])
    s([mode,r,g,b,0,0,0,0,1,bright,speed,x,y,0,0xaa,0x55]); s([4,0xf0])
for name,args in [('mode02 ff0000',(2,0xff,0,0)),('mode02 00ff00',(2,0,0xff,0)),('mode02 0000ff',(2,0,0,0xff))]:
    print(name,flush=True); light(*args); time.sleep(5)
h.close()
