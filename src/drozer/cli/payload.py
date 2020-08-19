#!/usr/bin/env python3

import logging
import sys

from mwr.common import logger

from ..payload.manager import PayloadManager

logger.setLevel(logging.DEBUG)
logger.addStreamHandler()

PayloadManager().run(sys.argv[2::])
