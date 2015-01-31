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



How to cuse peda alongside gxf:
-------------------------------

.. code-block:: diff

  diff --git a/peda.py b/peda.py
  index fd5b8d9..cc74b07 100644
  --- a/peda.py
  +++ b/peda.py
  @@ -5965,8 +5965,9 @@ signal.signal(signal.SIGINT, sigint_handler)
  
  # custom hooks
  peda.define_user_command("hook-stop",
  -    "peda context\n"
  -    "session autosave"
  +    "\n"
  +    # "peda context\n"
  +    # "session autosave"
       )
 
   # common used shell commands aliases

