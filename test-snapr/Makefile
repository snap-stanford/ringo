#
# Makefile for non-Microsoft compilers
#

all:

test: TestAll

MakeAll:
	$(MAKE) -C swig

TestAll:
	cp ../swig/_snap.so .
	cp ../swig/snap.py .
	./test-snapr.sh

clean:
	rm -f *.pyc *.so snap.py *.bin *.graph *.net *.table

