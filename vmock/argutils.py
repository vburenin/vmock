"""Different argument utils."""


def args_to_str(args, kwargs):
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
