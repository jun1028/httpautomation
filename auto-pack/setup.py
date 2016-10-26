from setuptools import setup, find_packages

setup(
    name="auto",
    version='1.0',
    description="automation testing framwork.",
    keywords='automation ',
    author='water.zhang',
    author_email='jun_1910310@163.com',
    url='https://xxxxxx/',
    license='water',
    packages=find_packages(exclude=["docs", "tests*", "log"]),
   
    install_requires=[
        'pymssql',
        'mysql',
        'httplib',
        'httplib2',
        'xlrd',
        'poster',
        'pycurl',
        'redis',
        'cx_Oracle'
        ],
)
