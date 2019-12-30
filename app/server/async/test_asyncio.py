import asyncio
import time

# async def compute(x, y):
#     print("Compute %s + %s ..." % (x, y))
#     await asyncio.sleep(1.0)
#     return x + y
#
# async def print_sum(x, y):
#     result = await compute(x, y)
#     print("%s + %s = %s" % (x, y, result))
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(print_sum(1, 2))
# loop.close()







#===========

async def sleep1():
    # await time.sleep(2)
    await asyncio.sleep(2)
    print(111)
    return 11

async def sleep2():
    await time.sleep(2)
    print(222)
    return 22
# @asyncio.coroutine
async def hello():
    print("Hello world!")
    # 异步调用asyncio.sleep(1):
    # r = await asyncio.sleep(1)
    r =   sleep1()
    r2 =  sleep2()
    print(r)
    print("Hello again!")

async def hello2():
    print("Hello2 world!")
    # 异步调用asyncio.sleep(1):
    # r = await asyncio.sleep(1)
    r =  sleep1()
    print(r)
    print("Hello2 again!")

# 获取EventLoop:
# loop = asyncio.get_event_loop()
# # 执行coroutine
# tasks = [hello()]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

sleep1()
print('333')