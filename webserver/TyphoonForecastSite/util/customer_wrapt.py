import time
import wrapt


def get_time(func):
    def inner(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f'{func}耗时共计:{end - start}s')
        return res

    return inner
