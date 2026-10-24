import time
from gmk67.audio import Volume
v=Volume(); last=None; t0=time.time()
while time.time()-t0<600:
    s=v.read()
    if s!=last: print(f'{time.time()-t0:5.1f}s volume/mute = {s}', flush=True); last=s
    time.sleep(0.05)

