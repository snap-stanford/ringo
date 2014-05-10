#
# Makefile for non-Microsoft compilers
#

all: MakeAll

test: TestAll

MakeAll:
	$(MAKE) -C swig

TestAll:
	$(MAKE) test -C test

clean:
	$(MAKE) clean -C swig
	$(MAKE) clean -C test

