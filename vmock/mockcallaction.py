"""MockCallAction class to store call data.
"""
# pylint: disable=raising-bad-type
from vmock import matchers
from vmock import mockerrors


class MockCallResult:
    """Types of expected result."""

    RETURN_VALUE = 1
    RAISE_EXCEPTION = 2
    EXECUTE_FUNCTION = 3


class MockCallAction(object):
    """MockCallAction is a storage of parameters for one particular calls.

        It contains all information that required to return appropriate value
    on call, raise exception or call custom function.
    """

    def __init__(self, obj, args, kwargs):
        """Constructor.

        :param obj: Parent MethodMock object.
        :param args: Expected args.
        :param kwargs: Expected keyword args.
        """
        self.__obj = obj
        self.__args = args
        self.__kwargs = kwargs

        self.__calls_counter = 0
        self.__max_times = 1
        self.__min_times = 1
        self.__result_type = MockCallResult.RETURN_VALUE
        self.__return_value = None

        # May be used for debug purpose if it is difficult to find
        # a source of error.

        self.__raise_call_error = False
        self.__non_ordered = False

    def __str__(self):
        return '%s, with args: %s' % \
               (str(self.__obj),
                self.__obj._args_to_str(self.__args, self.__kwargs))

    def get_call_error(self):
        if self.__max_times > 0 and self.__calls_counter > self.__max_times:
            return 'Method called %d of %d' % (self.__calls_counter,
                                               self.__max_times)

        if self.__min_times > 0 and self.__calls_counter < self.__min_times:
            return 'Number of calls is only: %d of %d' % (self.__calls_counter,
                                                          self.__min_times)
        return None

    def _is_times_limit(self):
        """Check if number of calls reached its limit.

        :return: True if CallAction reaches limit, otherwise False.
        """
        return self.__max_times == self.__calls_counter and self.__max_times > 0

    def _get_result(self, *args, **kwargs):
        """Does/Returns recorded result.

        Each result getter call increases call counter.
        """
        self.__calls_counter += 1
        if self.__raise_call_error:
            self.obj._mc.raise_error(
                mockerrors.UnexpectedCall('Unexpected call caught!'))
        if self.__result_type == MockCallResult.RETURN_VALUE:
            return self.__return_value
        elif self.__result_type == MockCallResult.RAISE_EXCEPTION:
            raise self.__return_value
        elif self.__result_type == MockCallResult.EXECUTE_FUNCTION:
            return self.__return_value(*args, **kwargs)

    @property
    def args(self):
        """Expected call arguments."""
        return self.__args

    @property
    def kwargs(self):
        """Expected call keyword arguments."""
        return self.__kwargs

    @property
    def obj(self):
        """Parent method mock."""
        return self.__obj

    @property
    def is_ordered(self):
        """Returns True if MockCall expected to be a non-ordered"""
        return self.__non_ordered

    def _compare_args(self, args, kwargs):
        """Compares external call arguments with CallAction arguments"""

        # Check if there are any arguments matcher.
        if (self.args and len(self.args) == 1 and
                isinstance(self.args[0], matchers.AnyArgsMatcher)):
            return True

        # Check if there are any arguments matcher.
        if (args and len(args) == 1 and
                isinstance(args[0], matchers.AnyArgsMatcher)):
            return True

        # Make sure that length of expected args is equal to actual args.
        if len(self.args) != len(args) or len(self.kwargs) != len(kwargs):
            return False

        # Verify difference between kwargs keys.
        if bool(set(self.kwargs.keys()).difference(set(kwargs.keys()))):
            return False

        # Verify call args including matchers.
        for e_arg, a_arg in zip(self.args, args):
            if not self.__compare_values(e_arg, a_arg):
                return False

        for key in kwargs.keys():
            if not self.__compare_values(self.kwargs[key], kwargs[key]):
                return False

        return True

    def __compare_values(self, e_val, a_val):
        """Compare call values, it take into consideration matchers."""
        if (isinstance(e_val, matchers.MockMatcher) and
                not isinstance(a_val, matchers.MockMatcher)):
            return e_val.compare(a_val)
        else:
            return e_val == a_val

    def mintimes(self, times):
        """Set minimum number of method mock calls. Must be non-ordered.

        :param times: Minimum amount of expected calls.
        """
        assert self.is_ordered, 'Object must be a non-ordered to set this parameter'
        if self.__max_times > 0 and times > self.__max_times:
            raise ValueError('Min number of calls can not be greater than max')
        self.__min_times = times
        return self

    def maxtimes(self, times):
        """Set maximum number of method mock calls. Must be non-ordered.

        :param times: Maximum amount of expected calls.
        """
        if not self.is_ordered:
            raise ValueError(
                'Object must be a non-ordered to set this parameter')
        if self.__min_times > 0 and times < self.__min_times:
            raise ValueError('MZ number of calls can not be less than min')
        self.__max_times = times
        return self

    def anyorder(self):
        """Make it as non-ordered. Sequence of calls will not be controlled.

        Non-ordered may be called any times by default.
        """
        self.__non_ordered = True
        self.anytimes()
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
        self.__max_times = times
        self.__min_times = times
        return self

    def anytimes(self):
        """This mock can be called any number of times. Must be non-ordered."""
        if not self.is_ordered:
            raise ValueError('Must be non-ordered to call any times')
        self.__max_times = 0
        self.__min_times = 0
        return self

    def raise_debug_call(self):
        """When this method is called, it will cause sequence error exception.

        Use it for debug purposes if you are not sure in test failure point.
        """
        self.__raise_call_error = True
        return self

    def returns(self, val):
        """Set value that will be returned for such call.

        :param val: Value to return.
        """
        self.__result_type = MockCallResult.RETURN_VALUE
        self.__return_value = val
        return self

    def raises(self, exc):
        """Raise specific exception on call.

        :param exc: Instance of exception that should be raised.
        """
        self.__result_type = MockCallResult.RAISE_EXCEPTION
        self.__return_value = exc
        return self

    def does(self, func):
        """Call custom function on this particular call.

        Your custom function will receive all parameters that were used
        to call mocked method. Result of this function will be returned
        as mocked method call result.

        :param func: Function that will be called.
        """
        self.__result_type = MockCallResult.EXECUTE_FUNCTION
        self.__return_value = func
        return self
