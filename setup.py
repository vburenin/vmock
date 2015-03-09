from setuptools import setup, find_packages


setup(
    name='vmock',
    description='Advanced Mock library following record and replay approach.',
    version='0.2',
    author='Volodymyr Burenin',
    author_email='vburenin@gmail.net',
    maintainer='Volodymyr Burenin',
    maintainer_email='vburenin@gmail.com',
    packages=find_packages(),
    install_requires=[],
    tests_require=['nose', 'nosexcover'],
    test_suite='nose.collector',
    extras_require={
        'test': ['nose', 'nosexcover'],
    },
    url='https://github.com/vburenin/vmock',
    license='MIT',
    classifiers=['License :: OSI Approved :: MIT License',
                 'Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Topic :: Software Development :: Quality Assurance',
                 ],
)
