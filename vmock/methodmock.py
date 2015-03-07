"""MethodMock class that keeps method data.
"""

import inspect
import functools

from vmock import matchers
from vmock.mockerrors import CallSequenceError
from vmock.mockerrors import InterfaceError
from vmock.mockerrors import UnexpectedCall


class MethodMock(object):

    """Method mock.

    Method mock object records all method calls with specific parameters,
    and store them in appropriate queue that depends on type of Mock Call.
    """

    def __init__(self, func_def, mock_control, display_name):
        """Constructor.

        :param func_def: Mocked function definitions.
        :param mock_control: Parent MockControl object.
        :param display_name: Name that will be displayed as class/module,
                name of mocked method/function
        """
        # Method/Function argument specification.

        self._func_def = func_def
        spec = func_def.arg_spec

        # If it is class method, let skip first 'self' parameter.
        if func_def.kind in ('method', 'class method'):
            if func_def.arg_spec.args:
                func_def.arg_spec.args.pop(0)

        defaults = None if spec.defaults is None else [
            0 for _ in spec.defaults]
        kwonlydefaults = None if spec.kwonlydefaults is None else {
            k: 0 for k in spec.kwonlydefaults}

        # [1:-1] removes parenthesis.
        txt_args = inspect.formatargspec(
            spec.args,
            varargs=spec.varargs,
            varkw=spec.varkw,
            defaults=defaults,
            kwonlyargs=spec.kwonlyargs,
            kwonlydefaults=kwonlydefaults)[1:-1]

        try:
            lambda_func = eval('lambda %s: None' % (txt_args,))
        except SyntaxError:
            # This should never happen unless there is a bug in vmock.
            import sys
            print(func_def.name, file=sys.stderr)
            print('lambda %s: None' % (txt_args,), file=sys.stderr)
            raise

        self._func = functools.wraps(func_def.func)(lambda_func)

        # Parent Mock Control.
        self._mc = mock_control

        # Name to be displayed for this method mock.
        self._display_name = display_name

    def __call__(self, *args, **kwargs):
        """Record or execute expected call.

        Behavior of MethodMock object call depends on current mode.
        In record mode it saves all calls and then reproduces them
        in replay mode.

        :param args, kwargs: Parameters are variable and depend on mocked
                method or function.
        """

        # Each mock call records an error if such has happened, since it may be
        # handled by function which you are testing. So, each next call of
        # other mocks will throw saved error.
        self._mc.check_error()
        if self._mc.is_recording():
            return self._save_call(args, kwargs)
        else:
            return self._make_call(args, kwargs)

    def __str__(self):
        if self._display_name:
            return '(MethodMock): ' + self._display_name
        else:
            return '(%s): %s' % (object.__str__(self), self.func_name)

    @property
    def func_name(self):
        """Mocked method name"""
        return self._func_def.name

    def _verify_interface(self, args, kwargs):
        """Verify mock call with original function interface.

        This method verify that is expected call fits the original
        function interface.

        :param args: Args how is method mock expected to be called.
        :param kwargs: Keyword args how is method mock expected to be called.
        """
        if args and isinstance(args[0], matchers.AnyArgsMatcher):
            return

        try:
            self._func(*args, **kwargs)
        except TypeError as e:
            err_txt = e.args[0].replace('<lambda>', self._func_def.name, 1)
            raise InterfaceError(err_txt) from None

    def _restore_original(self):
        """Restore original method/function"""
        setattr(self._func_def.owner, self.func_name, self._func_def.func)

    def _save_call(self, args, kwargs):
        """Save current call"""
        self._verify_interface(args, kwargs)
        return self._mc.get_new_action(self, args, kwargs)

    def _make_call(self, a_args, a_kwargs):
        """Mock call.

        Method performs a call of mocked method and returns an appropriate
        value. It checks what is going to be call, stub first and mock second.
        If there are no such call stub or expected call in the expectation
        queue. The CallSequenceError or UnexpectedCall exceptions will be
        raised.

        :params a_args: Actual call arguments.
        :params a_kwargs: Actual call keyword arguments.
        :return: Expected result.
        :raise: CallSequenceError or UnexpectedCall if call is unexpected.
        """

        # Find stub first.
        e_data = self._mc.find_stub(self, a_args, a_kwargs)

        # If there are no stubs, get call from the queue of expectors
        if e_data is None:
            e_data = self._mc.pop_current_record()

        # Failure if there are no stubs and expectors in the queue.
        if e_data is None:
            error = CallSequenceError(
                'No more calls are expected. \n'
                'Actual call: %s, with args: %s' %
                (str(self), self._args_to_str(a_args, a_kwargs)))
            self._mc.raise_error(error)

        if e_data.obj != self or not e_data._compare_args(a_args, a_kwargs):
            err_str = ('Unexpected method call.\n'
                       'Expected object: %s\n'
                       'Expected args: %s\n'
                       'Actual object: %s\n'
                       'Actual args: %s\n')
            fmt_params = (str(e_data.obj),
                          self._args_to_str(e_data.args, e_data.kwargs),
                          str(self), self._args_to_str(a_args, a_kwargs))
            error = UnexpectedCall(err_str % fmt_params)
            self._mc.raise_error(error)

        return e_data._get_result(*a_args, **a_kwargs)

    @staticmethod
    def _args_to_str(args, kwargs):
        """Format arguments in appropriate way."""
        args_str = []
        kwargs_str = {}
        for arg in args:
            if isinstance(arg, int):
                args_str.append(arg)
            else:
                args_str.append(str(arg))

        for key in kwargs.keys():
            if isinstance(kwargs[key], int):
                kwargs_str[key] = kwargs[key]
            else:
                kwargs_str[key] = str(kwargs[key])

        return '(%s, %s)' % (args_str, kwargs_str)


class MethodStub(MethodMock):

    """Used for immediate response after mocking."""

    def __call__(self, *args, **kwargs):
        self._mc.check_error()
        e_data = self._mc.find_static_mock(self, args, kwargs)
        if e_data is None:
            if self._mc.is_recording():
                self._verify_interface(args, kwargs)
                return self._mc.get_new_static_action(self, args, kwargs)
            else:
                self._mc.raise_error(CallSequenceError(
                    'There is no static mock for this call. \n'
                    'Actual call: %s, with args: %s' %
                    (str(self), self._args_to_str(args, kwargs))))
        else:
            return e_data._get_result(*args, **kwargs)

    def redefine(self, *args, **kwargs):
        """Redefine stub action."""

        return self._mc.redefine_static_action(self, args, kwargs)
