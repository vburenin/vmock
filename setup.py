from setuptools import setup, find_packages

install_requires = [
]

tests_require = install_requires + [
    'nose', 'nosexcover'
]

setup(
    name='vmock',
    description='Advanced Mock library following record and replay approach.',
    version='0.1',
    author='Volodymyr Burenin',
    author_email='vburenin@gmail.net',
    maintainer='Volodymyr Burenin',
    maintainer_email='vburenin@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    extras_require={
        'test': tests_require,
    },
    url='https://github.com/vburenin/vmock',
    license='MIT',
    classifiers=['License :: MIT',
                 'Development Status :: 4 - Beta/Stable',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python :: 3.4'],
)
