#!/usr/bin/env python3

import logging
import sys

from mwr.common import logger

from ..server import Server

logger.setLevel(logging.INFO)
logger.addStreamHandler()

Server().run(sys.argv[2::])
