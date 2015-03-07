"""Classes and function to test VMock functionality.
"""


class SimpleClass(object):
    VARIABLE = 100

    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
        self.__hl = 0

    def method_without_args(self):
        pass

    def method_with_one_arg(self, p1):
        pass

    @staticmethod
    def method_with_two_args(p1, p2):
        pass

    @staticmethod
    def static_method_with_two_args(p1, p2):
        pass

    def method_with_any_args(self, *args):
        pass

    def method_with_any_kwargs(self, **kargs):
        pass

    def method_with_any_args_kwargs(self, *args, **kargs):
        pass

    @property
    def hl(self):
        return self.__hl

    @hl.setter
    def hl(self, val):
        self.__hl = 1

    @hl.deleter
    def hl(self):
        self.__hl = None


def simple_func():
    pass


def func_with_one_arg(param1):
    pass


def func_with_one_arg_and_many(param1, *args):
    pass


def func_with_one_arg_and_many_other_kwargs(param1, **kwargs):
    pass


def func_with_defaults(a=1, b=2):
    pass
