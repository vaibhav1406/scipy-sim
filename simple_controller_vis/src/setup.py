from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='ScipySim',
    version='0.1.2',
    author='Brian Thorne, Allan McInnes',
    author_email='hardbyte@gmail.com',

    classifiers=[
      "Programming Language :: Python :: 2.6",
      "Development Status :: 3 - Alpha",
      "Environment :: Console",
      "Intended Audience :: Science/Research",
      "License :: OSI Approved :: GNU General Public License (GPL)",
      "Operating System :: OS Independent",
      "Topic :: Scientific/Engineering"
                 ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['distribute',
                      'docutils>=0.3',
                      'pyttk',
                      'numpy>=1.3.0',
                      'scipy'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    packages=find_packages(), #['scipysim','scipysim.models','scipysim.actors'],

    # Scripts get installed in the /usr/local/bin folder on the target machine
    scripts=['scipy-sim', ],

    test_suite="nose.collector",

    url='http://code.google.com/p/scipy-sim/',
    license='GPLv3',
    description='Simulation in Python.',
    keywords="simulation, scipy, discrete events",
    long_description=open('README.txt').read(),
)
