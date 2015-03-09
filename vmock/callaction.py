"""MockCallAction class to store call data.
"""

from vmock import argutils
from vmock import matchers


class CallAction(object):
    def __init__(self, mock, args, kwargs, min_times, max_times,
                 non_ordered, result):
        self.mock = mock
        self.args = args
        self.kwargs = kwargs
        self.min_times = min_times
        self.max_times = max_times
        self.non_ordered = non_ordered
        self.result = result

        self.call_counter = 0

    def call(self, args, kwargs):
        self.call_counter += 1
        return self.return_result(args, kwargs)

    def return_result(self, args, kwargs):
        raise NotImplementedError()

    def __str__(self):
        return '{} with args: {}'.format(
            str(self.mock),
            argutils.args_to_str(self.args, self.kwargs))

    def check_errors(self):
        if 0 < self.max_times < self.call_counter:
            return 'Method called {} of {}'.format(
                self.call_counter, self.max_times)

        if self.min_times > 0 and self.call_counter < self.min_times:
            return 'Number of calls is only: {} of {}'.format(
                self.call_counter, self.min_times)
        return None

    def is_times_limit(self):
        """Check if number of calls reached its limit.

        :return: True if CallAction reaches limit, otherwise False.
        """
        return self.max_times == self.call_counter and self.max_times > 0

    def cmp_args(self, args, kwargs):
        """Compares external call arguments with CallAction arguments"""

        # Check if there are any arguments matcher.
        if (len(self.args) == 1 and
                isinstance(self.args[0], matchers.AnyArgsMatcher)):
            return True

        # Check if there is any arguments matcher.
        if len(args) == 1 and isinstance(args[0], matchers.AnyArgsMatcher):
            return True

        # Make sure that length of expected args is equal to actual args.
        if len(self.args) != len(args) or len(self.kwargs) != len(kwargs):
            return False

        # Verify difference between kwargs keys.
        if bool(set(self.kwargs.keys()).difference(set(kwargs.keys()))):
            return False

        # Verify call args including matchers.
        for expected_arg, actual_arg in zip(self.args, args):
            if not matchers.compare_values(expected_arg, actual_arg):
                return False

        for key in kwargs.keys():
            if not matchers.compare_values(self.kwargs[key], kwargs[key]):
                return False

        return True


class ValueAction(CallAction):
    """An action to return value"""
    def return_result(self, args, kwargs):
        return self.result


class ExceptionAction(CallAction):
    """An action to raise exception"""
    def return_result(self, args, kwargs):
        raise self.result


class FunctionAction(CallAction):
    """An action to call user defined function"""
    def return_result(self, args, kwargs):
        return self.result(*args, **kwargs)


class ActionConfig(object):
    """ActionConfig is a storage of parameters for one particular calls.

        It contains all information that required to return appropriate value
    on call, raise exception or call custom function.
    """

    def __init__(self, mock, args, kwargs):
        """Constructor.

        :param mock: Parent MethodMock object.
        :param args: Expected args.
        :param kwargs: Expected keyword args.
        """
        self._mock = mock
        self._args = args
        self._kwargs = kwargs

        self._calls_counter = 0
        self._max_times = 1
        self._min_times = 1
        self._result_type = ValueAction
        self._return_value = None

        self._non_ordered = False

    @property
    def args(self):
        """Expected call arguments."""
        return self._args

    @property
    def kwargs(self):
        """Expected call keyword arguments."""
        return self._kwargs

    @property
    def obj(self):
        """Parent method mock."""
        return self._mock

    @property
    def is_ordered(self):
        """Returns True if MockCall expected to be a non-ordered"""
        return self._non_ordered

    def mintimes(self, times):
        """Set minimum number of method mock calls. Must be non-ordered.

        :param times: Minimum amount of expected calls.
        """
        if not self.is_ordered:
            raise ValueError(
                'Object must be a non-ordered to set this parameter')
        if 0 < self._max_times <= times:
            raise ValueError('Min number of calls can not be greater than max')
        self._min_times = times
        return self

    def maxtimes(self, times):
        """Set maximum number of method mock calls. Must be non-ordered.

        :param times: Maximum amount of expected calls.
        """
        if not self.is_ordered:
            raise ValueError(
                'Object must be a non-ordered to set this parameter')
        if self._min_times > 0 and times < self._min_times:
            raise ValueError('MZ number of calls can not be less than min')
        self._max_times = times
        return self

    def anyorder(self):
        """Make it as non-ordered. Sequence of calls will not be controlled.

        Non-ordered may be called any times by default.
        """
        self.anytimes()
        self._non_ordered = True
        return self

    def once(self):
        """It should be called once."""
        return self.times(1)

    def twice(self):
        """It should be called twice."""
        return self.times(2)

    def times(self, times):
        """It should be called specified number of times in series.

        :param times: Number of times that it expected to be called.
        """
        if times <= 0:
            raise ValueError('Times must be > 0')
        self._max_times = times
        self._min_times = times
        return self

    def anytimes(self):
        """This mock can be called any number of times."""
        self._non_ordered = True
        self._max_times = 0
        self._min_times = 0
        return self

    def returns(self, val):
        """Set value that will be returned for such call.

        :param val: Value to return.
        """
        self._result_type = ValueAction
        self._return_value = val
        return self

    def raises(self, exc):
        """Raise specific exception on call.

        :param exc: Instance of exception that should be raised.
        """
        self._result_type = ExceptionAction
        self._return_value = exc
        return self

    def does(self, func):
        """Call custom function on this particular call.

        Your custom function will receive all parameters that were used
        to call mocked method. Result of this function will be returned
        as mocked method call result.

        :param func: Function that will be called.
        """
        self._result_type = FunctionAction
        self._return_value = func
        return self

    def make_action(self):
        """Makes final action object."""
        return self._result_type(self._mock, self._args, self._kwargs,
                                 self._min_times, self._max_times,
                                 self._non_ordered, self._return_value)
