#!/usr/bin/env python
import os
import sys
#from django.core.management import execute_from_command_line
from fbreply.CustomDjango.management import execute_from_command_line

def begin(argv):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbreply.settings')
    execute_from_command_line(argv)
