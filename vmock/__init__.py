"""Entry point for a VMOCK.

Users should be using VMock class as a mock tracker by default.

"""

__author__ = 'Volodymyr Burenin'


from vmock import mockcontrol


class VMock(object):
    def __init__(self):
        self._mc = mockcontrol.MockControl()

    def mock_constructor(self, module, class_name,
                         arg_spec=None, display_name=None):

        """Mocks the constructor of the specified class.

        '__init__' method of the specified class will be mocked. To make this
        mock working, all call steps should be pre-recorded before going into
        replay mode. For example:

        :param module: Module where you want to mock your class constructor.
        :param class_name: String name of the class.
        :param arg_spec: If constructor arguments are not known, you may
                specify your own in format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.__init__' you will
                see string like: display_name.__init__
        :return: Constructor mock object.
        """
        return self._mc.create_ctor_mock(module, class_name, arg_spec,
                                         False, display_name)

    def stub_constructor(self, module, class_name,
                         arg_spec=None, display_name=None):
        """Creates immediately responsive constructor stub of the specified class.

        '__init__' method of the specified class will be replaced by stub.
        Stub become working immediately after it is defined how it is expected
        to be called. You should switch to replay mode for that. For example:

        :param module: Module where you want to stub your class constructor.
        :param class_name: String name of the class.
        :param arg_spec: If constructor arguments are not known, you may
                specify your own in format of 'inspect.FullArgSpec'.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.__init__' you will
                see string like: display_name.__init__
        :return: Constructor stub object.
        """
        return self._mc.create_ctor_mock(module, class_name, arg_spec,
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

        return self._mc.create_object_mock(class_definition,
                                           False, display_name)

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
        return self._mc.create_object_mock(class_definition, True, display_name)

    def mock_obj(self, obj, display_name=None):
        """Creates mocked object mock based on obj definition.

        This method works absolutely like mock_class, but it scans
        not a class definition, it scans instantiated object with all its
        attributes which could be added after instantiation.

        :param obj: object.
        :param display_name: Name that will be used for mocked object
                when error happens. Instead 'MethodMock.do_something' you will
                see string like: display_name.do_something
        :return: Fake object based on object.
        """
        return self._mc.create_object_mock(obj, False, display_name)

    def stub_obj(self, obj, display_name=None):
        """Creates immediately responsive obj stub based on obj definition.

        This method works absolutely like stub_class, but it scans
        not a class definition, it scans instantiated object with all its
        attributes which could be added after instantiation.

        :param obj: object.
        :param display_name: Name that will be used for stubbed object
                when error happens. Instead 'MethodMock.do_something' you will
                see string like: display_name.do_something
        :return: Fake object based on object.
        """
        return self._mc.create_object_mock(obj, True, display_name)

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

        func_def = mockcontrol.FuncDef(name=method_name, kind=None, func=None,
                                       arg_spec=arg_spec, owner=obj)

        return self._mc.create_mock(func_def, False, display_name)

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
        func_def = mockcontrol.FuncDef(name=method_name, kind=None, func=None,
                                       arg_spec=arg_spec, owner=obj)

        return self._mc.create_mock(func_def, True, display_name)

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
        self._mc.replay()

    def verify(self):
        """Do post execution verification.

        Verification checks for non called recorded actions.
        """
        self._mc.verify()

    @property
    def tear_down(self):
        return self._mc.tear_down
