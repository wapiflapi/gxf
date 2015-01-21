===============================
gxf
===============================


..
   .. image:: https://travis-ci.org/wapiflapi/gxf.png?branch=master
	   :target: https://travis-ci.org/wapiflapi/gxf

..
   .. image:: https://pypip.in/d/gxf/badge.png
	   :target: https://pypi.python.org/pypi/gxf


Gdb Extension Framework is a bunch of python code around the gdb api.

* Free software: MIT license
* Documentation: https://gxf.readthedocs.org

How to use:
-----------

.. code-block:: none

   $ python3 setup.py install # or develop
   $ gdb
   (gdb) python import gxf.extensions
   (gdb) help gx
   
   
 
How to compile gdb with python3:
--------------------------------

.. code-block:: none
   $ git clone git://sourceware.org/git/binutils-gdb.git
   $ cd binutils-gdb
   $ ./configure --with-python=python3
   $ make && sudo make install
