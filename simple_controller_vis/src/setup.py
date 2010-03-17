from setuptools import setup, find_packages


setup(
    name='ScipySim',
    version='0.1.0',
    author='Brian Thorne',
    author_email='hardbyte@gmail.com',
    
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3','pyttk', 'numpy>=1.3.0','scipy'],

    
    packages=find_packages(), #['scipysim','scipysim.models','scipysim.actors'],
    scripts=['scipysim/test_scipysim.py', ],
    
    url='http://code.google.com/p/scipy-sim/',
    license='LICENSE.txt',
    description='Simulation in Python.',
    long_description=open('README.txt').read(),
)
