#
# Makefile for SWIG processing of SNAP Python
#	Use this Makefile to compile SNAP Python from scratch
# 

# set the path to your SNAP directory here
GITDIR = ../../snapr

# include compilation parameters
include $(GITDIR)/Makefile.config

SNAPDIR = $(GITDIR)/$(SNAP)
GLIBDIR = $(GITDIR)/$(GLIB)
SNAPEXPDIR = $(GITDIR)/$(SNAPEXP)
SNAPDIRLIST = -I$(SNAPDIR) -I$(GLIBDIR)

UNAME := $(shell uname)

ifeq ($(UNAME), Linux)
  # Linux flags
  SWIGFLAGS += -D_CMPWARN -D__stdcall -DSW_SNAPPY -D_OPENMP -DNONUMPY
  CXXFLAGS += -fPIC -D__STDC_LIMIT_MACROS -DSW_SNAPPY -fopenmp
  LDFLAGS += -shared -fopenmp
else ifeq ($(UNAME), Darwin)
  # OS X flags
  SWIGFLAGS += -D_CMPWARN -D__stdcall -DSW_SNAPPY -DNONUMPY
  CXXFLAGS += -DSW_SNAPPY
  LDFLAGS += -lpython -dynamiclib
else ifeq ($(shell uname -o), Cygwin)
  # Cygwin flags
  SWIGFLAGS += -D_CMPWARN -D__stdcall -DSW_SNAPPY -DNONUMPY
  CXXFLAGS += -shared -D__STDC_LIMIT_MACROS -DSW_SNAPPY
  LIBS += -lpython2.6
endif

all: snap.py _snap.so

snap_wrap.cxx: snap.i snap_types.i tvec.i pneanet.i pungraph.i pngraph.i pgraph.i pngraphmp.i\
	snapswig.h snap_types.h printgraph.h goodgraph.cpp
	swig $(SWIGFLAGS) -python -c++ -w302,312,317,325,362,383,384,389,401,503,508,509 -O $(SNAPDIRLIST) snap.i

snap_wrap.o: snap_wrap.cxx
	g++ $(CXXFLAGS) -c snap_wrap.cxx $(SNAPDIRLIST) -I/usr/include/python2.6 -I/usr/include/python2.7 -I/usr/lib/python2.7/dist-packages/numpy/core/include

Snap.o: 
	$(CC) $(CXXFLAGS) -c $(SNAPDIR)/Snap.cpp $(SNAPDIRLIST)

_snap.so: snap_wrap.o Snap.o
	g++ $(LDFLAGS) -o _snap.so snap_wrap.o Snap.o $(LIBS)

snap.py: snap_wrap.cxx

install: setup.py snap.py _snap.so
	sudo python setup.py install

dist: setup.py snap.py _snap.so
	python setup.py sdist

install-win: setup.py snap.py _snap.pyd
	/cygdrive/c/Python27/python.exe setup.py install

dist-win: setup.py snap.py _snap.pyd
	cp MANIFEST.win MANIFEST
	/cygdrive/c/Python27/python.exe setup.py sdist

clean:
	rm -f *.o *_wrap.cxx _*.so *.pyc snap.py _snap.*

