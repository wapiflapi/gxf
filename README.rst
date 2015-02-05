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


FAQ
---

* ``TypeError: int() argument must be a string or a number, not 'list'``

  This error is *probably* due to your argcomplete version being too old and
  having bugs. See requirements.txt for the minimum version you need.

* I keep seeing lots of other tracebacks.

  That is expected for the moment, I'm focusing on the framework and don't
  bother catching all the exception in the extensions where I should be
  displaying decent error messages. This will be done in the future, but for the
  moment it is normal if you see tracebacks when gxf tries to access program
  memory that isn't mapped. This happend for example when rip or rsp is invalid.
