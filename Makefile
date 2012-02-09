CC=pycompile
CFLAGS=

all: pirb.py
	@echo Compile pirb
	@$(CC) $(CFLAGS) pirb.py
	@echo Compile src
	@$(CC) $(CFLAGS) src/*.py
	@echo Compile modules
	@$(CC) $(CFLAGS) modules/*.py
	@echo Done - make install for install binaries

bin: pirb.py
	@echo Compile binary
	@$(CC) $(CFLAGS) pirb.py

install: pirb.pyc
	@echo Install pirb.pyc -> pirb
	@cp pirb.pyc pirb
	@echo Done

clean:
	@echo Cleaning base
	@echo Cleaning modules
	@rm -rf modules/*.pyc
	@echo Cleaning src
	@rm -rf src/*.pyc
	@echo Done

dist-clean: pirb
	@echo Remove pirb-binary
	@rm -rf pirb
	@rm -rf pirb.pyc
	@echo Remove modules-binaries
	@rm -rf modules/*.pyc
	@echo Remove src-binaries
	@rm -rf src/*.pyc
	@echo Done
