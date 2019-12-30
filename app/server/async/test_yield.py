def foo():
    print("starting...")
    while True:
        res = yield 4
        print("res:", res)


g = foo()

# print(next(g))
# print("*"*20)
# print(next(g))


def yield_test(n):
    for i in range(n):
        yield i*2
        print("i=", i)
    print("do something")
    print("end")

# k = yield_test(5)
# print(next(k), ",")
# print(next(k), ",")
# for i in yield_test(5):
#     print(i, ",")


#生产者消费者模型
def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()

c = consumer()
produce(c)