INCLUDES = -I$(abs_top_builddir)

PYSRC = $(top_srcdir)/lang/python
if DEBUG
PY_SETUP_DEBUG = -g
endif
all-local: _wiredtiger.so
$(PYSRC)/wiredtiger_wrap.c: $(top_srcdir)/src/include/wiredtiger.in $(PYSRC)/wiredtiger.i
	@(cd $(PYSRC) && \
	    $(SWIG) -python -nodefaultctor -nodefaultdtor -threads -I$(abs_top_builddir) wiredtiger.i)

_wiredtiger.so: $(top_builddir)/libwiredtiger.la $(PYSRC)/wiredtiger_wrap.c
	$(PYTHON) $(PYSRC)/setup.py build_ext -b . -t . -f $(PY_SETUP_DEBUG)

TESTS = $(top_srcdir)/examples/python/run-ex_access
