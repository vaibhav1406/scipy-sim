# Requirements #

Scipysim requires:
  * [Python](http://python.org/download/) 2.x (x >= 7)
  * [NumPy](http://numpy.scipy.org/) (>= 1.3.0)
  * [SciPy](http://scipy.org/) (>= 0.7.0)
  * [matplotlib](http://matplotlib.sourceforge.net/)
  * [pyttk](http://code.google.com/p/python-ttk/) (requires Tk 8.5)

Optional packages:
  * epydoc (to create the documentation)

These should be installable with [PIP](http://pip.openplans.org/) or [easy\_install](http://packages.python.org/distribute/easy_install.html).

Debian/Ubuntu package names required are:
python python-numpy python-scipy python-matplotlib tk8.5 python-tk tix epydoc

# Installation #

You can install scipysim to your main site-packages folder with:
```
        sudo python setup.py install
```
on Linux or Mac OS X; and:
```
        python setup.py install
```
on Windows. To install in a more sandboxed "development" environment
substitute develop for install, e.g.:
```
        sudo python setup.py develop
```
This installs an egg at the current directory and links to the package
in your site-packages folder.

## easy\_install ##

Scipysim is also available from the [Python Package Index](http://pypi.python.org/pypi/ScipySim). If you use `easy_install`, you should be able to install scipysim to your site-packages directory simply by using
```
        easy_install scipysim
```

## ttk and Tile ##

Using the installer should take care of a lot of the requirements listed above. If you run into problems with ttk, make sure that you have Tile installed, and that the TILE\_LIBRARY environment variable is set. Tile and ttk are nominally included in Tk 8.5. But note that if you've installed the ActiveState distribution of Tk 8.5 you may need to also take the extra step of running
```
        teapot install tile
```

# Testing #

To test that your installation is working correctly you can use the test\_scipysim.py script. From the base directory of the scipysim installation run
```
        scipysim/test_scipysim.py
```
This will execute a series of unit tests that verify the operation of the various components of scipysim. Assuming everything has been installed correctly, you should see all tests pass.