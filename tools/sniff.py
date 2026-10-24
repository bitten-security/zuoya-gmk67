"""Spawns the vendor DeviceDriver.exe and logs every HidD_SetFeature/GetFeature buffer."""
import frida, sys, time
EXE = r"C:\Program Files (x86)\ZUOYO GMK67 Driver\DeviceDriver.exe"
LOG = sys.argv[1] if len(sys.argv) > 1 else "hidlog.txt"
JS = r"""function hexs(p, n){ n=Math.min(n,96); return Array.from(new Uint8Array(p.readByteArray(n))).map(b=>('0'+b.toString(16)).slice(-2)).join(''); }
const nt = Process.getModuleByName('ntdll.dll');
Interceptor.attach(nt.getExportByName('NtDeviceIoControlFile'), {
  onEnter(a){ const code=a[5].toUInt32(); this.code=code; this.out=a[8]; this.olen=a[9].toUInt32();
    const inb=a[6], ilen=a[7].toUInt32();
    if (ilen>0 && !inb.isNull()) send('IOCTL 0x'+code.toString(16)+' in['+ilen+'] '+hexs(inb,ilen)); else send('IOCTL 0x'+code.toString(16)+' in[0] out['+this.olen+']'); },
  onLeave(r){ if (this.olen>0 && !this.out.isNull() && this.code!=0) send('  -> out['+this.olen+'] '+hexs(this.out,this.olen)); }
});
Interceptor.attach(nt.getExportByName('NtWriteFile'), {
  onEnter(a){ const n=a[6].toUInt32(); send('WRITE['+n+'] '+hexs(a[5],n)); }
});"""
f = open(LOG, "a", buffering=1)
pid = int(sys.argv[2]); s = frida.attach(pid)
sc = s.create_script(JS)
sc.on("message", lambda m, d: f.write(f"{time.time():.3f} {m.get('payload', m)}\n"))
sc.load()
print("running", pid, flush=True)
while True: time.sleep(1)


