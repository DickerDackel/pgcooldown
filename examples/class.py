import time

from functools import wraps
from cooldown import Cooldown, cooldown

c = Cooldown(3)

# for i in range(2):
#     while not c.cold:
#         print(f'still not cold: {c.temperature}')
#         time.sleep(0.1)
#     print('cold')
#     c.reset(2)

c = Cooldown(3)
d = Cooldown(1)
print('pause test')
while True:
    if c.cold:
        break
    if d.cold and not c.paused:
        print('pausing c')
        c.pause()
        d.reset()
    elif d.cold and c.paused:
        print('restarting c')
        c.start()
        d.pause()
    print('c is running', c.temperature)
    time.sleep(0.1)

print('done')
