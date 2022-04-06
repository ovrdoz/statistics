##execution
##execute first
# $ yum install rpm-build rpmdevtools
##second 
# $ rpmbuild -ba ./build/bdist.linux-x86_64/rpm/SPECS/hub-statistics.spec
## run again
# $ python setup.py bdist_rpm
## look dist dir

from setuptools import setup

setup(name='hub-statistics',
    version='1.0',
    description='Hub Statistics',
    long_description='Hub Statistics tool for extract metrics of elasticsearch',
    author='Diego Maia',
    author_email='dmaia@santander.com.br',
    license='MIT',
    packages=['app'],
    zip_safe=False)


python pip-9.0.3-py2.py3-none-any.whl/pip install --no-index Flask-0.12.1-py2.py3-none-any.whl 
