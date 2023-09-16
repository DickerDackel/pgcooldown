from timeit import timeit
from pgcooldown import LerpThing
from statistics import mean, median, stdev

l = LerpThing(0, 1024, 60)

res = []
for i in range(5):
    res.append(timeit(lambda: l(), number=1_800_000))
    print(round(res[-1], 3))

print(f'{mean(res)=:.3}  {median(res)=:.3}  {stdev(res)=:.3}')
