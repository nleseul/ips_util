from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ips_util',
    version='1.0',
    description='A Python package for manipulating IPS patches',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: Freeware',
        'Natural Language :: English'
        'Programming Language :: Python :: 3.2',
        'Topic :: Utilities'
    ],
    url='https://github.com/nleseul/ips_util',
    author='NLeseul',
    author_email='nleseul@this-life.us',
    license='Unlicense',
    packages=['ips_util'],
    entry_points = {
        'console_scripts': ['ips_util=ips_util.__main__:main'],
    },
    test_suite='ips_util.tests',
    python_requires='>=3.2',
    zip_safe=False)