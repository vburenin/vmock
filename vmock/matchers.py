"""Matcher to use to mock complex parameters."""

import inspect


class MockMatcher(object):

    """Each mock matcher must be inherited from this class.

    This type is used to distinguish different object from matchers.
    """
    def compare(self, param):
        """Check if matcher hits parameter value"""

        raise NotImplementedError('This method must be implemented')


class CustomMatcher(MockMatcher):

    """Use custom matcher for your custom use cases."""

    def __init__(self, matching_func):
        """Constructor.

        :param matching_func: Your custom function to compare incoming value.
        """
        self.matching_func = matching_func

    def __str__(self):
        return str(self.matching_func)

    def __eq__(self, other):
        return (isinstance(other, CustomMatcher) and
                self.matching_func == other.matching_func)

    def compare(self, param):
        """Check if matcher hits parameter value"""
        return self.matching_func(param)


class AnyArgsMatcher(MockMatcher):

    """Special class, that substitutes all the parameters to anything."""

    def __str__(self):
        return '<Accept any number arguments and any values>'

    def compare(self, param):
        return True


class AnyMatcher(MockMatcher):

    def __str__(self):
        return '<Any value is accepted>'

    def __eq__(self, other):
        return isinstance(other, AnyMatcher)

    def compare(self, param):
        return True


class NoneMatcher(MockMatcher):

    def __str__(self):
        return '<None>'

    def __eq__(self, other):
        return isinstance(other, NoneMatcher)

    def compare(self, param):
        return param is None


class InStringMatcher(MockMatcher):

    """Checks if string contains some fragment."""

    def __init__(self, contains):
        """Constructor.

        :param contains: value that we are looking for.
        """

        self.contains = contains

    def __str__(self):
        return '<String containing \'%s\'>' % (self.contains,)

    def __eq__(self, other):
        return isinstance(other, InStringMatcher) and \
            self.contains == other.contains

    def compare(self, param):
        """Check if matcher hits parameter value"""
        if not isinstance(param, str):
            return False
        return self.contains in param


class NotInStringMatcher(MockMatcher):

    """Checks if string doesn't contain some fragment."""

    def __init__(self, not_contains):
        """Constructor.

        :param not_contains: value that we are looking for.
        """

        self.not_contains = not_contains

    def __str__(self):
        return '<String not containing \'%s\'>' % (self.not_contains,)

    def __eq__(self, other):
        return isinstance(other, NotInStringMatcher) and \
            self.not_contains == other.not_contains

    def compare(self, param):
        """Check if matcher hits parameter value"""
        if not isinstance(param, str):
            return False
        return self.not_contains not in param


class RegexMatcher(MockMatcher):

    """Checks if regex matches string."""

    def __init__(self, compiled_re):
        """Constructor.

        :param compiled_re: Compiled regex to match against string.
        """

        self.compiled_re = compiled_re

    def __str__(self):
        return "<Regex '%s'>" % (self.compiled_re.pattern,)

    def __eq__(self, other):
        return isinstance(other, RegexMatcher) and \
            self.compiled_re.pattern == other.compiled_re.pattern

    def compare(self, param):
        if not isinstance(param, str):
            return False
        return bool(self.compiled_re.search(param))


class TypeMatcher(MockMatcher):

    """Type matcher. Use it to match only type based expectations."""

    def __init__(self, match_type):
        """Constructor.

        :param match_type: Your expected type.
        """
        self.in_type = match_type

    def __str__(self):
        return str(self.in_type)

    def __eq__(self, other):
        return isinstance(other, TypeMatcher) and \
            self.in_type == other.in_type

    def compare(self, param):
        """Check if matcher hits parameter value"""
        return isinstance(param, self.in_type)


class FunctionMatcher(MockMatcher):

    """Matcher for parameters which are functions."""

    def __str__(self):
        return '<function or method>'

    def __eq__(self, other):
        return isinstance(other, FunctionMatcher)

    def compare(self, param):
        """Check if matcher hits parameter value"""
        return inspect.isfunction(param) or inspect.ismethod(param)


class ListMatcher(MockMatcher):

    """List and tuples matcher."""

    def __init__(self, contains, list_only=False, tuple_only=False):
        """Constructor.

        :param contains: List of values which are expected to be in list/tuple.
        :param list_only: Only list is expected.
        :param tuple_only: Only tuple is expected.
        """
        assert not (list_only and tuple_only), \
            'list_only and tuple_only parameters are mutually exclusive'

        self.contains = contains
        self.list_only = list_only
        self.tuple_only = tuple_only

    def __str__(self):
        if not self.list_only and not self.tuple_only:
            return '<list or tuple with: %s>' % (self.contains,)

    def __eq__(self, other):
        return isinstance(other, ListMatcher) and \
            self.contains == other.contains and \
            self.list_only == other.list_only and \
            self.tuple_only == other.tuple_only

    def compare(self, param):
        """Check if matcher hits parameter value"""
        if self.list_only and isinstance(param, tuple):
            return False

        if self.tuple_only and isinstance(param, list):
            return False

        if not isinstance(param, (list, tuple)):
            return False

        if isinstance(self.contains, (list, tuple)):
            for val in self.contains:
                try:
                    param.index(val)
                except ValueError:
                    return False
            return True

        return False


class DictMatcher(MockMatcher):

    """Dict matcher."""

    def __init__(self, contains):
        """Constructor.

        :param dict contains: List of key-values which are expected to be in
        dict.
        """
        self.contains = contains

    def __str__(self):
        return '<dict with: %s>' % (self.contains,)

    def __eq__(self, other):
        return isinstance(other, DictMatcher) and \
            self.contains == other.contains

    def compare(self, param):
        """Check if matcher hits parameter value"""
        if not isinstance(param, dict):
            return False

        return all(k in param and param[k] == v
                   for k, v in self.contains.items())


def str_with(val):
    """String contains value."""
    return InStringMatcher(val)


def str_without(val):
    """String doesn't contain value"""
    return NotInStringMatcher(val)


def regex_match(val):
    """Regex matches string"""
    return RegexMatcher(val)


def is_function():
    """Expects function."""
    return FunctionMatcher()


def is_type(expected_type):
    """Expects user custom type."""

    return TypeMatcher(expected_type)


def is_str():
    """Expect any string"""
    return is_type(str)


def is_bytes():
    """Expect bytes"""
    return is_type(bytes)


def is_int():
    """Expects any int value."""
    return is_type(int)


def is_float():
    """Expects any float value"""
    return is_type(float)


def is_number():
    """Expects any numeric value"""
    return is_type((int, float))


def is_dict():
    """Expects any dictionary"""
    return TypeMatcher(dict)


def is_list():
    """Expects any list"""
    return TypeMatcher(list)


def is_tuple():
    """Expects any tuple"""
    return TypeMatcher(tuple)


def list_or_tuple_contains(val):
    """Expects list or tuple containing value or list of values."""
    return ListMatcher(val)


def tuple_contains(val):
    """Expects tuple containing value or list of values."""
    return ListMatcher(val, tuple_only=True)


def list_contains(val):
    """Expects list containing value or list of values."""
    return ListMatcher(val, list_only=True)


def dict_contains(val):
    """Expects dict containing given key-values (subdict)"""
    return DictMatcher(val)


def any_args():
    """Accept any arguments, values, keyword values."""
    return AnyArgsMatcher()


def any_val():
    """Accept any value."""
    return AnyMatcher()


def is_none():
    """Matches none values."""
    return NoneMatcher()
