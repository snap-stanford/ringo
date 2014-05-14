#
# Makefile for non-Microsoft compilers
#

all: MakeAll

test: TestAll

MakeAll:
	$(MAKE) -C swig

TestAll:
	#$(MAKE) test -C test
	$(MAKE) test -C test-snappy
	$(MAKE) test -C test-snapr

clean:
	$(MAKE) clean -C swig
	$(MAKE) clean -C test-snappy
	$(MAKE) clean -C test-snapr

