"""MockControl mock management class.
"""
# pylint: disable=raising-bad-type

import inspect
import types

from vmock.methodmock import MethodMock, MethodStub
from vmock.callaction import ActionConfig
from vmock.mockerrors import CallSequenceError
from vmock.mockerrors import CallsNumberError
from vmock.mockerrors import MockError

from vmock import mock_src_gen
from vmock.vmock_defs import ANY_ARGS_SPEC
from vmock.vmock_defs import FuncDef
from vmock.vmock_defs import NOT_MOCKABLE_METHODS


class MockControl(object):

    """This class creates mock objects such as class objects,
    class constructors, functions. It also controls all calls
    to mock methods, sequence of calls and restore everything
    back at the end.
    """

    def __init__(self):
        self._exp_queue = []
        self._stubs = {}
        self._static_stubs = {}
        self._object_mocks = {}
        self._recording = True
        self.__play_pointer = 0
        self._current_action = None
        self.__error = None

    def mock_constructor(self, module, class_name,
                         arg_spec=None, display_name=None):
        """Mocks the constructor of the specified class.

        :param module: Module where you want to mock your class constructor.
        :param class_name: String name of the class.
        :param arg_spec: If constructor arguments are not known, you may
                specify your own in format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.__init__' you will
                see string like: display_name.__init__
        :return: Constructor mock object.
        """
        return self.create_ctor_mock(module, class_name, arg_spec,
                                     False, display_name)

    def stub_constructor(self, module, class_name,
                         arg_spec=None, display_name=None):
        """Creates immediately responsive constructor stub of the specified class.


        :param module: Module where you want to stub your class constructor.
        :param class_name: String name of the class.
        :param arg_spec: If constructor arguments are not known, you may
                specify your own in format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.__init__' you will
                see string like: display_name.__init__
        :return: Constructor stub object.
        """
        return self.create_ctor_mock(module, class_name, arg_spec,
                                     True, display_name)

    def mock_class(self, class_definition, display_name=None):
        """Creates new fake object with all mocked class methods.

        Rather than mocking some specific class methods, you may create
        fake object with all the class methods where each method is mocked.
        It doesn't mock original class, it creates a copy of that one.

        Because of Python specific some methods can not be mocked.
        All of them are defined in NOT_MOCKABLE_METHODS constant.
        So, it means they will not be copied at all.
        Pay attention, that we are not mocking __init__ method too,
        since it is a special case. To mock it, you should do it separately.

        mock_class also mocks 'properties'. It is really nice feature.

        :param class_definition: Class that you'd like to mock.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.do_something' you will
                see string like: display_name.do_something
        :return: Fake object class.
        """

        return self.create_object_mock(class_definition, False, display_name)

    def stub_class(self, class_definition, display_name=None):
        """Creates immediately responsive obj stub based on class definition.

        Rather than stubbing some specific class methods, you may create
        fake object with all the class methods where each method is a stub.
        It doesn't stub original class, it creates a copy of that one.

        Because of Python specific some methods can not be stubbed.
        All of them are defined in NOT_MOCKABLE_METHODS constant.
        So, it means they will not be copied at all.
        Pay attention, that we are not stubbing __init__ method too,
        since it is a special case. To stub it, use stub_constructo.

        :param class_definition: Class that you'd like to stub.
        :param display_name: Name that will be used for stubbed object
                when error happens. Instead 'MethodMock.do_something' you will
                see string like: display_name.do_something
        :return: Fake object class.
        """
        return self.create_object_mock(class_definition, True, display_name)

    def mock_obj(self, obj, display_name=None):
        """Creates mocked object mock based on obj definition.

        This method works absolutely like mock_class, but it scans
        not a class definition, it scans instantiated object with all its
        attributes which could be added after instantiation.

        Look mock_class help for examples.

        :param obj: object.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.do_something' you will
                see string like: display_name.do_something
        :return: Fake object based on object.
        """
        return self.create_object_mock(obj, False, display_name)

    def stub_obj(self, obj, display_name=None):
        """Creates immediately responsive obj stub based on obj definition.

        This method works absolutely like stub_class, but it scans
        not a class definition, it scans instantiated object with all its
        attributes which could be added after instantiation.

        Look stub_class help for examples.

        :param obj: object.
        :param display_name: Name that will be used for stubbed object
                when error happens. Instead 'MethodMock.do_something' you will
                see string like: display_name.do_something
        :return: Fake object based on object.
        """
        return self.create_object_mock(obj, True, display_name)

    def mock_method(self, obj, method_name, arg_spec=None, display_name=None):
        """Create method/function mock.

        :param obj: The module/object/class where function of method should be
                mocked.
        :param method_name: String method name.
        :param arg_spec: If func/method arguments are not known, you may
                specify your own in format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.func_name' you will
                see string like: display_name.func_name
        """

        func_def = FuncDef(name=method_name, kind=None, func=None,
                           arg_spec=arg_spec, owner=obj)

        return self.create_mock(func_def, False, display_name)

    def stub_method(self, obj, method_name, arg_spec=None, display_name=None):
        """Create method/function immediately responsive stub.

        :param obj: The module/object/class where function of method should be
                stubbed.
        :param method_name: String method name.
        :param arg_spec: If func/method arguments are not known, you may
                specify your own in format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for stubbed object
                when error happens. Instead 'MethodMock.func_name' you will
                see string like: display_name.func_name
        """
        func_def = FuncDef(name=method_name, kind=None, func=None,
                           arg_spec=arg_spec, owner=obj)

        return self.create_mock(func_def, True, display_name)

    def make_mock(self, arg_spec=None, display_name=None):
        """Creates a mock of a function not mocking anything.

        :param arg_spec: Arg specs you want to use for this mock
                in a format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.mock' you will
                see string like: display_name.method_name
        """

        class FakeMockClass(object):
            @staticmethod
            def mock(*args, **kwargs):
                pass

        fmc = FakeMockClass()
        return self.mock_method(fmc, 'mock', arg_spec=arg_spec,
                                display_name=display_name)

    def make_stub(self, arg_spec=None, display_name=None):
        """Creates a stub of a function not stubbing anything.

        :param arg_spec: Arg specs you want to use for this mock
                in a format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for stubbed object
                when error happens. Instead 'MethodMock.mock' you will
                see string like: display_name.method_name
        """

        class FakeStubClass(object):
            @staticmethod
            def stub(*args, **kwargs):
                pass

        fsc = FakeStubClass()
        return self.stub_method(fsc, 'stub', arg_spec=arg_spec,
                                display_name=display_name)

    def replay(self):
        """Switches from recording to replay mode."""
        self._save_current_action()
        self._recording = False

    def verify(self):
        """Do post execution verification."""
        # Verify possible handled vmock errors.
        self.check_error()

        # Verify expectation queue.
        next_expected = self.pop_current_record()
        if next_expected is not None:
            err_txt = 'There are more steps to call. ' \
                      'Current call is: ' + str(next_expected)
            raise CallSequenceError(err_txt)

        # Verify stubs.
        errors = []
        for stub in self._stubs.values():
            for action in stub:
                error_text = action.check_errors()
                if error_text:
                    errors.append(str('%s - %s' % (str(action), error_text)))

        # Verify static stubs.
        for stub in self._static_stubs.values():
            for action in stub:
                error_text = action.check_errors()
                if error_text:
                    errors.append(str('%s - %s' % (str(action), error_text)))

        if errors:
            raise CallsNumberError('\n'.join(errors))

    def tear_down(self):
        """Restore all mocked function/method/classes back."""
        for methods in self._object_mocks.values():
            for method_data in methods.values():
                if method_data is not None:
                    method_data._restore_original()

    def raise_error(self, error):
        """Generated errors must be stored, otherwise if test code
        contains except/finally clauses incorrect error can be generated at
        the end because mock control error may be handled in those clauses.
        """
        self.__error = error
        raise error

    def check_error(self):
        """Raise an error if it happened already but was handled."""
        if self.__error is not None:
            raise self.__error

    def new_action(self, obj, args, kwargs):
        """Saves current action and creates new one."""
        assert self._recording, 'The play mode is set'
        self._save_current_action()
        self._current_action = ActionConfig(obj, args, kwargs)
        return self._current_action

    def new_static_action(self, obj, args, kwargs):
        """Creates new static action."""

        assert self._recording, 'The play mode is set'

        static_action_cfg = ActionConfig(obj, args, kwargs)
        # Default static action can be called any number of times.
        static_action = static_action_cfg.anytimes().make_action()

        # Check if there is no stubs already exists.
        for action in self._static_stubs.get(obj, []):
            if static_action.cmp_args(action.args, action.kwargs):
                raise ValueError('Static stub already exists!')

        # Create container for MethodMock stubs.
        if obj not in self._static_stubs:
            self._static_stubs[obj] = []

        self._static_stubs[obj].append(static_action_cfg)

        return static_action_cfg

    def redefine_static_action(self, obj, args, kwargs):
        """Redefines static action for the stub.
        """

        assert self._recording, 'The play mode is set'

        static_action = ActionConfig(obj, args, kwargs)
        # Default static action can be called any times times.
        static_action.anyorder().anytimes()

        self._static_stubs[obj] = [static_action]
        return static_action

    def is_recording(self):
        """Check if we are in recording mode."""
        return self._recording

    def find_stub(self, mock_obj, args, kwargs):
        """Find existing stub and increase call counter."""
        for action in self._stubs.get(mock_obj, []):
            if action.cmp_args(args, kwargs):
                return action
        return None

    def compile_stub(self, mock_obj):
        new_actions = []
        actions = self._static_stubs.get(mock_obj, [])
        for a in actions:
            if isinstance(a, ActionConfig):
                a = a.make_action()
            new_actions.append(a)
        self._static_stubs[mock_obj] = new_actions
        return new_actions

    def find_static_mock(self, mock_obj, args, kwargs):
        """Find existing stub."""
        for action in self.compile_stub(mock_obj):
            if action.cmp_args(args, kwargs):
                return action

        return None

    def pop_current_record(self):
        """Pop next record from the expectation queue."""
        assert not self._recording, "MockControl is still in record mode"
        try:
            if self.__play_pointer > 0:
                exp_call = self._exp_queue[self.__play_pointer - 1]
                if not exp_call.is_times_limit():
                    return exp_call

            self.__play_pointer += 1
            return self._exp_queue[self.__play_pointer - 1]
        except IndexError:
            return None

    def create_ctor_mock(self, module, class_name, arg_spec,
                         is_stub, display_name):
        """Creates mock for class constructor."""
        if arg_spec is None:
            class_def = getattr(module, class_name)
            try:
                arg_spec = inspect.getfullargspec(class_def.__init__)
                if arg_spec.args:
                    arg_spec.args.pop(0)
            except (TypeError, AttributeError):
                arg_spec = ANY_ARGS_SPEC

        func_def = FuncDef(name=class_name, kind='function',
                           func=None, arg_spec=arg_spec,
                           owner=module)
        return self.create_mock(func_def, is_stub, display_name)

    def create_object_mock(self, obj_class, is_stub, display_name):
        """Scans an object interface and mock each found method"""

        is_class = inspect.isclass(obj_class)
        if is_class:
            class_def = obj_class
        else:
            class_def = obj_class.__class__

        if display_name is None:
            display_name = class_def.__name__
        return mock_src_gen.init_fake_class(
            self, class_def, display_name, is_stub)

    @staticmethod
    def _extend_func_def(func_def):
        func = getattr(func_def.owner, func_def.name)
        if func_def.arg_spec is None:
            try:
                arg_spec = inspect.getfullargspec(func)
            except TypeError:
                arg_spec = ANY_ARGS_SPEC
        else:
            assert isinstance(func_def.arg_spec, inspect.FullArgSpec), \
                'Incorrect arg_spec type, must be inspect.FullArgSpec'
            arg_spec = func_def.arg_spec

        kind = None
        if func_def.kind is None:
            if inspect.ismethod(func):
                kind = 'method'
            elif inspect.ismodule(func_def.owner):
                kind = 'function'
            elif inspect.isclass(func_def.owner):
                m = getattr(func_def.owner, func_def.name)
                if isinstance(m, staticmethod):
                    kind = 'static method'
                elif isinstance(m, classmethod):
                    kind = 'class method'
                elif isinstance(m, property):
                    kind = 'property'
                elif isinstance(m, types.FunctionType):
                    kind = 'class method'
                else:
                    raise ValueError('Unknown method type')
        else:
            kind = func_def.kind

        return FuncDef(name=func_def.name, kind=kind, func=func,
                       arg_spec=arg_spec, owner=func_def.owner)

    def create_mock(self, func_def, is_stub, display_name):
        """Creates mock for function or class/object method."""

        if func_def.name in NOT_MOCKABLE_METHODS:
            raise MockError('Method %s is not mockable' % func_def.name)

        if not hasattr(func_def.owner, func_def.name):
            raise ValueError(
                'Object does not have such method: ' + func_def.name)

        func_def = self._extend_func_def(func_def)

        owner_mocks = self._object_mocks.setdefault(func_def.owner, {})

        # None must be stored to do not rollback in case of tear_down.
        if func_def.name not in owner_mocks:
            owner_mocks[func_def.name] = None

        old_method = getattr(func_def.owner, func_def.name)

        if isinstance(old_method, MethodMock):
            raise MockError('Method "%s" is already mocked!' % (func_def.name,))

        if is_stub:
            new_mock = MethodStub(func_def, self, display_name)
        else:
            new_mock = MethodMock(func_def, self, display_name)
        owner_mocks[func_def.name] = new_mock

        setattr(func_def.owner, func_def.name, new_mock)

        return new_mock

    def _save_current_action(self):
        """Saves current action if new one is requested."""
        assert self._recording, 'The play mode is set'

        if self._current_action is None:
            return

        action = self._current_action.make_action()

        # Check if there is no stubs already exists.
        for stub_action in self._stubs.get(action.mock, []):
            if action.cmp_args(stub_action.args, stub_action.kwargs):
                raise ValueError('Stub already exists!')

        if action.non_ordered:
            # If action is stub we should check if such doesn't exist already
            # in the expectation queue.
            for e_call in self._exp_queue:
                if action.cmp_args(e_call.args, e_call.kwargs):
                    raise ValueError('Pattern exists in the expect queue')
            # Create container for MethodMock stubs.
            if action.mock not in self._stubs:
                self._stubs[action.mock] = []
            self._stubs[action.mock].append(action)
        else:
            # Save as sequence if it is not a stub.
            self._exp_queue.append(action)

        self._current_action = None