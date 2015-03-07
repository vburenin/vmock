"""Class code generator with mocked methods.
"""

import inspect
import types

from vmock import vmock_defs
from vmock.methodmock import MethodMock
from vmock.methodmock import MethodStub


CLASS_TMPL = """
class {0}(object):
    def __init__(self, mc, var_list, interface, mocker):
        self.__mc = mc
        self.__mocker = mocker
        self.__interface = interface
        self.__m = dict()
        for v in var_list:
            setattr(self, v.name, v.object)
            setattr(self.__class__, v.name, v.object)
        """


TMPL_MOCKER_PROP = """
        self.__m['{0}__get_prop'] = mocker(interface['{0}__get_prop'],
                                       mc, 'get_' + '{0}')
        self.__m['{0}__set_prop'] = mocker(interface['{0}__set_prop'],
                                       mc, 'set_' + '{0}')
        self.__m['{0}__del_prop'] = mocker(interface['{0}__del_prop'],
                                       mc, 'del_' + '{0}')"""

METHOD_TMPL = """
    def {0}(self, *args, **kwargs):
        if '{0}' not in self.__m:
            self.__m['{0}'] = self.__mocker(self.__interface['{0}'],
                                            self.__mc, None)
        return self.__m['{0}'](*args, **kwargs)"""


PROP_TMPL = """
    @property
    def {0}(self):
        return self.__m['{0}__get_prop']()

    @{0}.setter
    def {0}(self, value):
        self.__m['{0}__set_prop'](value)

    @{0}.deleter
    def {0}(self):
        self.__m['{0}__del_prop']()"""


def init_fake_class(mc, class_def, class_name, is_stub):
    """Initializes fake class.

    :param MockControl mc: Mockcontrol instance.
    :param class_def: Class definition to mock.
    :param class_name: Class name.
    :param is_stub: If True makes method stubs.
    """

    if is_stub:
        mocker = MethodStub
    else:
        mocker = MethodMock

    interface = {}
    var_list = []

    for attr in inspect.classify_class_attrs(class_def):
        if attr.name in vmock_defs.NOT_MOCKABLE_METHODS:
            continue
        # Methods such __str__ or __repr__ if not defined by user
        # can cause recursive call issues in case of error.
        if attr.defining_class is object:
            continue

        try:
            arg_spec = inspect.getfullargspec(getattr(class_def, attr.name))
        except TypeError:
            arg_spec = vmock_defs.ANY_ARGS_SPEC

        func_def = vmock_defs.FuncDef(name=attr.name, kind=attr.kind,
                                      func=None, arg_spec=arg_spec, owner=None)
        if attr.kind == 'property':
            interface[attr.name + '__get_prop'] = vmock_defs.FuncDef(
                name=attr.name, kind=attr.kind, func=None,
                arg_spec=vmock_defs.NO_ARGS_SPEC, owner=None)
            interface[attr.name + '__set_prop'] = vmock_defs.FuncDef(
                name=attr.name, kind=attr.kind, func=None,
                arg_spec=vmock_defs.VALUE_ARGS_SPEC, owner=None)
            interface[attr.name + '__del_prop'] = vmock_defs.FuncDef(
                name=attr.name, kind=attr.kind, func=None,
                arg_spec=vmock_defs.NO_ARGS_SPEC, owner=None)
        elif attr.kind != 'data':
            interface[attr.name] = func_def
        else:
            if not (attr.name.startswith('__') and attr.name.endswith('__')):
                var_list.append(attr)

    init_list = [CLASS_TMPL.format(class_name)]
    method_list = []

    for name, func_def in interface.items():
        if func_def.kind == 'property':
            if name.endswith('__get_prop'):
                init_list.append(TMPL_MOCKER_PROP.format(func_def.name))
                method_list.append(PROP_TMPL.format(func_def.name))
        elif func_def.kind == 'data':
            var_list.append(func_def)
        else:
            method_list.append(METHOD_TMPL.format(name))

    init_list.extend(method_list)
    code = '\n'.join(init_list)

    class_module = types.ModuleType('')
    exec(code, class_module.__dict__)
    return class_module.__dict__[class_name](mc, var_list, interface, mocker)


