#!/usr/bin/env python3

import logging
import sys

from mwr.common import logger

from ..ssl import SSLManager

logger.setLevel(logging.DEBUG)
logger.addStreamHandler()

SSLManager().run(sys.argv[2::])
    
