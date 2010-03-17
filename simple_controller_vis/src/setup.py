from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages


setup(
    name='ScipySim',
    version='0.1.1',
    author='Brian Thorne',
    author_email='hardbyte@gmail.com',

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3', 'pyttk', 'numpy>=1.3.0', 'scipy'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    packages=find_packages(), #['scipysim','scipysim.models','scipysim.actors'],


    scripts=['scipy-sim', ],

    test_suite="nose.collector",

    url='http://code.google.com/p/scipy-sim/',
    license='GPLv3',
    description='Simulation in Python.',
    keywords="simulation, scipy, discrete events",
    long_description=open('README.txt').read(),
)
