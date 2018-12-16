from setuptools import setup

setup(name='ips_util',
    version='0.0',
    description='ips_util',
    url='https://github.com/nleseul/ips_util',
    author='NLeseul',
    license='Unlicense',
    packages=['ips_util'],
    entry_points = {
        'console_scripts': ['ips_util=ips_util.__main__:main'],
    },
    test_suite='ips_util.tests',
    python_requires='>=3.6',
    zip_safe=False)