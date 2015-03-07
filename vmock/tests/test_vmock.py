"""VMock library test.
"""

import unittest

import some_classes as sc

from vmock import mockcontrol
from vmock import mockerrors


class TestVmockMatchers(unittest.TestCase):

    def setUp(self):
        self.mc = mockcontrol.MockControl()
        self.addCleanup(self.td)

        self.orig_f = sc.func_with_one_arg
        self.orig_f2 = sc.simple_func
        self.tear_down_call_flag = False

    def call_teardown(self):
        if not self.tear_down_call_flag:
            self.tear_down_call_flag = True
            self.mc.tear_down()

    def td(self):
        self.call_teardown()
        sc.func_with_one_arg = self.orig_f
        sc.simple_func = self.orig_f2

    def test_restore_one_func(self):
        orig_simple_func = sc.simple_func
        self.mc.mock_method(sc, 'simple_func')
        self.assertNotEqual(orig_simple_func, sc.simple_func)
        self.call_teardown()
        self.assertEqual(orig_simple_func, sc.simple_func)

    def test_restore_two_funcs(self):
        orig_simple_func = sc.simple_func
        orig_func_with_one_arg = sc.func_with_one_arg

        self.mc.mock_method(sc, 'simple_func')
        self.mc.mock_method(sc, 'func_with_one_arg')
        self.assertNotEqual(orig_simple_func, sc.simple_func)
        self.assertNotEqual(orig_func_with_one_arg, sc.func_with_one_arg)

        self.call_teardown()
        self.assertEqual(orig_simple_func, sc.simple_func)
        self.assertEqual(orig_func_with_one_arg, sc.func_with_one_arg)

    def test_func_stub_anytimes(self):
        self.mc.mock_method(sc, 'simple_func')().returns(1111).anyorder()
        self.mc.replay()

        for _ in range(100):
            self.assertEqual(1111, sc.simple_func())

        self.mc.verify()

    def test_func_stub_10_times(self):
        self.mc.mock_method(sc, 'simple_func')().returns(1111).anyorder().times(10)
        self.mc.replay()

        for _ in range(11):
            self.assertEqual(1111, sc.simple_func())

        self.assertRaises(mockerrors.CallsNumberError, self.mc.verify)

    def test_func_mock_3_times(self):
        self.mc.mock_method(sc, 'simple_func')().returns(1111).times(3)
        self.mc.replay()

        self.assertEqual(1111, sc.simple_func())
        self.assertEqual(1111, sc.simple_func())
        self.assertEqual(1111, sc.simple_func())

        self.mc.verify()

    def test_func_mock_3_times_call_only_2_times(self):
        self.mc.mock_method(sc, 'simple_func')().returns(1111).times(3)
        self.mc.replay()

        self.assertEqual(1111, sc.simple_func())
        self.assertEqual(1111, sc.simple_func())

        self.assertRaises(mockerrors.CallSequenceError, self.mc.verify)

    def test_static_mock_any_times(self):
        self.mc.stub_method(sc, 'simple_func')().returns(2222)
        for _ in range(111):
            self.assertEqual(2222, sc.simple_func())
        self.mc.replay()
        self.mc.verify()

    def test_static_mock_10_times_but_called_11_times(self):
        self.mc.stub_method(sc, 'simple_func')().returns(2222).times(10)
        for _ in range(11):
            self.assertEqual(2222, sc.simple_func())
        self.mc.replay()
        self.assertRaises(mockerrors.CallsNumberError, self.mc.verify)

    def test_property_mock(self):
        m_class = self.mc.mock_class(sc.SimpleClass, display_name='mcls')

        m_class.hl = 6
        m_class.hl.returns(11)
        del m_class.hl

        self.mc.replay()
        m_class.hl = 6
        self.assertEqual(11, m_class.hl)
        del m_class.hl
        try:
            del m_class.hl
            self.fail()
        except mockerrors.CallSequenceError:
            pass
        # Check if error reraised.
        self.assertRaises(mockerrors.CallSequenceError, self.mc.verify)

    def test_mock_whole_class(self):
        m_class = self.mc.mock_class(sc.SimpleClass)
        m_class.method_without_args()
        m_class.method_with_one_arg(1)
        m_class.static_method_with_two_args(1, 2)
        m_class.method_with_any_args(1, 2, 3)
        self.mc.replay()
        m_class.method_without_args()
        m_class.method_with_one_arg(1)
        m_class.static_method_with_two_args(1, 2)
        m_class.method_with_any_args(1, 2, 3)
        self.mc.verify()


    def test_funcs_mock_different_sequence(self):
        f1 = self.mc.mock_method(sc, 'simple_func')
        f2 = self.mc.mock_method(sc, 'func_with_one_arg')
        f1().returns(1)
        f1().returns(2).times(3)
        f2(2).returns(3)
        f1().returns(4)
        f2(2).returns(5)
        f2(3).raises(IOError('error'))

        self.mc.replay()
        self.assertEqual(1, f1())
        self.assertEqual(2, f1())
        self.assertEqual(2, f1())
        self.assertEqual(2, f1())
        self.assertEqual(3, f2(2))
        self.assertEqual(4, f1())
        self.assertEqual(5, f2(2))
        self.assertRaises(IOError, f2, 3)
        self.mc.verify()

    def test_mock_does(self):
        def does_func():
            return 'a'

        f1 = self.mc.stub_method(sc, 'simple_func')
        f1().does(does_func)

        self.assertEqual('a', f1())

    def test_stub_does_args(self):
        def does_func(a, b=1):
            return a + b

        f1 = self.mc.stub_method(sc, 'func_with_one_arg_and_many_other_kwargs')
        f1(1, b=2).does(does_func)

        self.assertEqual(3, f1(1, b=2))

    def test_mock_does_args(self):
        def does_func(a, b=1):
            return a + b

        f1 = self.mc.mock_method(sc, 'func_with_one_arg_and_many_other_kwargs')
        f1(1, b=2).does(does_func)

        self.mc.replay()
        self.assertEqual(3, f1(1, b=2))
        self.mc.verify()

    def test_min_max_times_ok(self):
        f1 = self.mc.stub_method(sc, 'simple_func')
        f1().mintimes(2).maxtimes(5)

        self.mc.replay()
        f1()
        f1()
        f1()
        self.mc.verify()

    def test_min_max_times_less_than_expected(self):
        f1 = self.mc.stub_method(sc, 'simple_func')
        f1().mintimes(2).maxtimes(5)

        self.mc.replay()
        f1()
        self.assertRaises(mockerrors.CallsNumberError, self.mc.verify)

    def test_min_max_times_more_than_expected(self):
        f1 = self.mc.stub_method(sc, 'simple_func')
        f1().mintimes(1).maxtimes(2)

        self.mc.replay()
        f1()
        f1()
        f1()
        self.assertRaises(mockerrors.CallsNumberError, self.mc.verify)

    def test_funcs_mock_more_calls_than_needed(self):
        f1 = self.mc.mock_method(sc, 'simple_func')
        f2 = self.mc.mock_method(sc, 'func_with_one_arg')
        f1().returns(1)
        f2(2).returns(3)

        self.mc.replay()
        self.assertEqual(1, f1())
        self.assertEqual(3, f2(2))
        self.assertRaises(mockerrors.CallSequenceError, f1)
        self.assertRaises(mockerrors.CallSequenceError, self.mc.verify)

    def test_ctor_and_class_mock(self):
        m_class = self.mc.mock_class(sc.SimpleClass)
        self.mc.mock_constructor(sc, 'SimpleClass')(1, 2).returns(m_class)
        m_class.method_with_one_arg(1).returns(3)
        m_class.method_with_two_args(3, 4).returns(11).anyorder()

        self.mc.replay()
        s_class = sc.SimpleClass(1, 2)
        self.assertEqual(11, s_class.method_with_two_args(3, 4))
        self.assertEqual(3, s_class.method_with_one_arg(1))
        self.assertEqual(11, s_class.method_with_two_args(3, 4))
        self.assertEqual(100, s_class.VARIABLE)
        self.mc.verify()

    def test_interface_check_func_without_args(self):
        s_func = self.mc.stub_method(sc, 'simple_func')
        try:
            s_func(g=5)
            self.fail()
        except mockerrors.InterfaceError:
            pass

        self.assertRaises(mockerrors.InterfaceError, s_func, 1)
        s_func()

    def test_interface_check_func_with_default_value(self):
        s_func = self.mc.stub_method(sc, 'func_with_defaults')
        s_func(1)
        s_func(1, 2)
        s_func(a=1, b=2)
        try:
            s_func(c=1)
            self.fail()
        except mockerrors.InterfaceError:
            pass

    def test_intefrace_check_func_with_one_arg(self):
        s_func = self.mc.stub_method(sc, 'func_with_one_arg')
        try:
            s_func(1, g=5)
            self.fail()
        except mockerrors.InterfaceError:
            pass

        s_func(param1=1)

        self.assertRaises(mockerrors.InterfaceError, s_func, 1, 2)

    def test_intefrace_check_func_with_one_arg_and_many_other_args(self):
        s_func = self.mc.stub_method(sc, 'func_with_one_arg_and_many')
        s_func(1, 5, 6)
        try:
            s_func(1, 5, 6, g=5)
            self.fail()
        except mockerrors.InterfaceError:
            pass

    def test_intefrace_check_func_with_one_arg_and_many_kwargs(self):
        s_func = self.mc.stub_method(
            sc, 'func_with_one_arg_and_many_other_kwargs')
        s_func(1, g=5, c=5, a=6)
        s_func(param1=1, g=5, c=5, a=6)
        try:
            s_func(1, 5, g=5)
            self.fail()
        except mockerrors.InterfaceError:
            pass

    def test_handled_error_regenerated(self):
        other_func = self.mc.mock_method(sc, 'func_with_one_arg')
        s_func = self.mc.mock_method(sc, 'simple_func')
        s_func()
        self.mc.replay()
        try:
            other_func(123)
        except Exception:
            # Suppress all exception
            pass
        self.assertRaises(mockerrors.UnexpectedCall, s_func)

    def test_make_mock(self):
        m0 = self.mc.make_mock()
        m1 = self.mc.make_mock()
        m0(1, 2, 3).returns(1)
        m1(1).returns(2)
        m0(2, 2).returns(3)
        m1(1, 1).returns(4)
        m0(2, 2).returns(5)
        self.mc.replay()
        self.assertEqual(1, m0(1, 2, 3))
        self.assertEqual(2, m1(1))
        self.assertEqual(3, m0(2, 2))
        self.assertEqual(4, m1(1, 1))
        self.assertEqual(5, m0(2, 2))
        self.mc.verify()

    def test_make_stub(self):
        m0 = self.mc.make_stub()
        m1 = self.mc.make_stub()
        m0(1, 2, 3).returns(1)
        m1(1).returns(2)
        m0(2, 2).returns(3)
        self.assertEqual(1, m0(1, 2, 3))
        self.assertEqual(2, m1(1))
        self.assertEqual(3, m0(2, 2))
        self.assertEqual(1, m0(1, 2, 3))
        self.assertEqual(2, m1(1))
        self.assertEqual(3, m0(2, 2))
        self.assertEqual(1, m0(1, 2, 3))
        self.assertEqual(2, m1(1))
        self.assertEqual(3, m0(2, 2))

if __name__ == '__main__':
    unittest.main()
