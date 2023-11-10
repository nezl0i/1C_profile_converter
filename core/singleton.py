import time


def who_time(function):
    def wrapped(*args):
        start_time = time.perf_counter()
        res = function(*args)
        end_time = time.perf_counter()
        print(f"{function.__name__} {end_time - start_time:.6f} seconds")
        return res
    return wrapped


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
