class ProxyException(Exception):
    def __init__(self, err='ProxyException'):
        Exception.__init__(self, err)


class ProxyLoseException(ProxyException):
    def __init__(self, err='ProxyLoseException'):
        ProxyLoseException.__init__(self, err)


# def testRaise():
#     raise PreconditionsException()
#
#
# try:
#     testRaise()
# except PreconditionsException as e:
#     print(e)