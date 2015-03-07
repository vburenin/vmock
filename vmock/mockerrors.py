"""Mock errors classes.
"""


class MockError(Exception):

    """Base class for all Mock Library exceptions."""

    pass


class InterfaceError(MockError):

    """Raised if there is interface error."""

    pass


class CallSequenceError(MockError):

    """Raised if there is an incorrect in series calls."""

    pass


class UnexpectedCall(MockError):

    """Raised if there is unexpected call of mocked method."""

    pass


class CallsNumberError(MockError):

    """Raised if stub is called more time than it is allowed."""

    pass
