"""VMock library matchers tests.
"""

import re
import unittest

from vmock import matchers


class TestVmockMatchers(unittest.TestCase):

    def test_regex_match(self):
        regex_match = matchers.regex_match(re.compile('^[ab]sdf$'))
        self.assertTrue(regex_match.compare('asdf'))
        self.assertFalse(regex_match.compare('csdf'))
        self.assertEqual(regex_match,
                         matchers.regex_match(re.compile('^[ab]sdf$')))

    def test_str_with(self):
        str_with = matchers.str_with('val')
        self.assertTrue(str_with.compare('test val'))
        self.assertFalse(str_with.compare('test al'))
        self.assertEqual(str_with, matchers.str_with('val'))

    def test_str_without(self):
        str_without = matchers.str_without('val')
        self.assertFalse(str_without.compare('test val'))
        self.assertTrue(str_without.compare('test al'))
        self.assertEqual(str_without, matchers.str_without('val'))

    def test_is_function(self):
        is_function = matchers.is_function()
        self.assertTrue(is_function.compare(lambda x: 10))
        self.assertFalse(is_function.compare('str'))

    def test_is_type(self):
        is_type = matchers.is_type((str, int))
        self.assertTrue(is_type.compare('ewdwed'))
        self.assertTrue(is_type.compare(20))
        self.assertFalse(is_type.compare(lambda x: 10))

    def test_is_str(self):
        is_str = matchers.is_str()
        self.assertFalse(is_str.compare(10))
        self.assertTrue(is_str.compare('str'))

    def test_is_int(self):
        is_int = matchers.is_int()
        self.assertTrue(is_int.compare(10))
        self.assertTrue(is_int.compare(-10))
        self.assertFalse(is_int.compare(10.1))
        self.assertFalse(is_int.compare('rferf'))

    def test_is_float(self):
        is_float = matchers.is_float()
        self.assertTrue(is_float.compare(10.1))
        self.assertFalse(is_float.compare(10))
        self.assertFalse(is_float.compare(-10))
        self.assertFalse(is_float.compare(10))
        self.assertFalse(is_float.compare('rferf'))

    def test_is_number(self):
        is_number = matchers.is_number()
        self.assertTrue(is_number.compare(10))
        self.assertTrue(is_number.compare(-10))
        self.assertTrue(is_number.compare(10))
        self.assertTrue(is_number.compare(10.1))
        self.assertFalse(is_number.compare('rferf'))

    def test_is_dict(self):
        is_dict = matchers.is_dict()
        self.assertTrue(is_dict.compare({}))
        self.assertFalse(is_dict.compare([]))

    def test_is_list(self):
        matcher = matchers.is_list()
        self.assertTrue(matcher.compare([]))
        self.assertFalse(matcher.compare({}))

    def test_is_tuple(self):
        matcher = matchers.is_tuple()
        self.assertTrue(matcher.compare(()))
        self.assertFalse(matcher.compare([]))

    def test_list_or_tuple_contains(self):
        matcher = matchers.list_or_tuple_contains([1, 2, 3])
        self.assertTrue(matcher.compare((1, 5, 6, 2, 3)))
        self.assertFalse(matcher.compare((1, 5, 6, 3)))

    def test_tuple_contains(self):
        matcher = matchers.tuple_contains([1, 2, 3])
        self.assertTrue(matcher.compare((1, 5, 6, 2, 3)))
        self.assertFalse(matcher.compare((1, 5, 6, 2)))
        self.assertFalse(matcher.compare([1, 5, 6, 2, 3]))
        self.assertFalse(matcher.compare([1, 5, 6, 3]))

    def test_list_contains(self):
        matcher = matchers.list_contains([1, 2, 3])
        self.assertTrue(matcher.compare([1, 5, 6, 2, 3]))
        self.assertFalse(matcher.compare([1, 5, 6, 2]))
        self.assertFalse(matcher.compare((1, 5, 6, 2, 3)))
        self.assertFalse(matcher.compare((1, 5, 6, 3)))

if __name__ == '__main__':
    unittest.main()
