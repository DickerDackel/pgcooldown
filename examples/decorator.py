from time import sleep
from functools import wraps

from cooldown import Cooldown, cooldown

class X:
    def __init__(self):
        self.cooldown = Cooldown(3)

    @cooldown
    def update(self):
        print('Update!')

x = X()
while True:
    x.update()
    sleep(0.2)
