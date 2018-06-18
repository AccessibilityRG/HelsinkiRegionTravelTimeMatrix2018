# -*- coding: utf-8 -*-
"""
Time penalties for Digiroad 2.0. 

Created on Thu Apr 26 13:50:03 2018

@author: Henrikki Tenkanen
"""

penalties = {
        # Rush hour penalties for different road types ('rt')
        'r': {
                'rt12' : 12.195 / 60,
                'rt3' : 11.199 / 60,
                'rt456': 10.633 / 60,
                'median': 2.022762
                },
        # Midday penalties for different road types ('rt')
        'm': {
                'rt12' : 9.979 / 60,
                'rt3' : 6.650 / 60,
                'rt456': 7.752 / 60,
                'median': 1.667750
                },
        # Average penalties for different road types ('rt')
        'avg': {
                'rt12' : 11.311 / 60,
                'rt3' : 9.439 / 60,
                'rt456': 9.362 / 60,
                'median': 1.884662
                },
        }