#!/bin/bash

cd src

python <<EOF
from tests.importers import *
import unittest

unittest.main()

EOF






