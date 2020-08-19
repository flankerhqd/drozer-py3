#!/usr/bin/env python3

import logging
import sys

from mwr.common import logger

from ..agent.manager import AgentManager

logger.setLevel(logging.DEBUG)
logger.addStreamHandler()

AgentManager().run(sys.argv[2::])
