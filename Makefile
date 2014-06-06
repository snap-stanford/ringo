#
# Makefile for non-Microsoft compilers
#

.PHONY: TestAll Setup clean

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

Setup:
	$(MAKE) dist -C setup

clean:
	$(MAKE) clean -C swig
	$(MAKE) clean -C test-snappy
	$(MAKE) clean -C test-snapr
	$(MAKE) clean -C test-ringo
	$(MAKE) clean -C setup
