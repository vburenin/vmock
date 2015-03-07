"""VMock definitions.
"""
import inspect
from collections import namedtuple


FuncDef = namedtuple('FuncDef', ['name', 'kind', 'func',
                                 'arg_spec', 'owner'])

NOT_MOCKABLE_METHODS = {
    '__class__', '__del__', '__dict__',
    '__getattr__', '__init__', '__instancecheck__',
    '__new__', '__setattr__', '__subclasscheck__',
    '__weakref__', '__getattribute__', '__subclasshook__'
}


ANY_ARGS_SPEC = inspect.FullArgSpec(
    args=[], varargs='args', varkw='kwargs',
    defaults=None, kwonlyargs=[], kwonlydefaults=None,
    annotations={})


VALUE_ARGS_SPEC = inspect.FullArgSpec(
    args=['value'], varargs=None, varkw=None,
    defaults=None, kwonlyargs=[], kwonlydefaults=None,
    annotations={})


NO_ARGS_SPEC = inspect.FullArgSpec(
    args=[], varargs=None, varkw=None,
    defaults=None, kwonlyargs=[], kwonlydefaults=None,
    annotations={})
