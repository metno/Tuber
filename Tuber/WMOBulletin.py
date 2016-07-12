#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import re

def findAHL(message):
    """
    Find the abbreviated header line in a message

    Param message: message as bytes
    Returns a MatchObject witch may contain the AHL
    """

    return re.search(br'[A-Z]{4}\d{2} [A-Z]{4} \d{6}( [A-Z]{3})?', message)
