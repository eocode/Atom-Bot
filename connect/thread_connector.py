import threading

from functools import wraps


def limit(number):
    """
        This decorator limits the number of simultaneous Threads
    """
    sem = threading.Semaphore(number)

    def wrapper(func):
        @wraps(func)
        def wrapped(*args):
            with sem:
                return func(*args)

        return wrapped

    return wrapper


def async_fn(f):
    """
        This decorator executes a function in a Thread
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = threading.Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
