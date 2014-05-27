#
# Makefile for non-Microsoft compilers
#

all: MakeAll

test: TestAll

dist: MakeAll Setup

MakeAll:
	$(MAKE) -C swig

TestAll:
	#$(MAKE) test -C test
	$(MAKE) test -C test-snappy
	$(MAKE) test -C test-snapr
	$(MAKE) test -C test-ringo

clean:
	$(MAKE) clean -C swig
	$(MAKE) clean -C test-snappy
	$(MAKE) clean -C test-snapr
	$(MAKE) clean -C test-ringo
	$(MAKE) clean -C setup

Setup:
	$(MAKE) dist -C setup
