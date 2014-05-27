#
# Makefile for non-Microsoft compilers
#

all: dist

dist: CopyAll Setup

clean:
	rm -f *.o _*.so *.pyc

CopyAll:
	cp ../swig/snap.py .
	cp ../swig/_snap.so .
	cp ../ringo-engine-python/ringo.py .

Setup:
	python setup.py sdist