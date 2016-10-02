"""
    Module which gives access to debugging utilities, especially for mix-in
related bugs.

"""
TESTING = True

#--built-in imports
from functools import wraps


class Debugger:
    """
        Debugging utility. Tracks method calls and returns. Very useful when
    dealing with mix-ins.

    """

    depth = 0

    def cdebug(self, cls):
        global TESTING
        for name, func in cls.__dict__.items():
            if callable(func) and TESTING:
                setattr(cls, name, self.debug(func, cls))
        return cls

    def debug(self, func, cls):
        @wraps(func)
        def debugged(*args, **kwargs):
            print('  '*self.depth, cls.__name__, func.__name__)

            self.depth += 1
            results = func(*args, **kwargs)
            self.depth -= 1

            print('  '*self.depth, 'End', cls.__name__, func.__name__)

            return results
        return debugged


debug = Debugger().cdebug # convenience decorator
