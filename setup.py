#!/usr/bin/env python

from subprocess import Popen as shell

shell("python setup.py install", shell=True, cwd="deps/APScheduler").wait()