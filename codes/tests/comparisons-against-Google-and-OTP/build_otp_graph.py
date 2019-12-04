# -*- coding: utf-8 -*-
"""
build_otp_graph.py 

Created on Wed Jun 12 15:47:57 2019

@author: hentenka
"""

import graphbuilder as gbr
import os
import glob
import shutil
import mrouter

# Filepaths
data_dir = r"C:\HY-DATA\hentenka\KOODIT\Uni\manuscripts\2019_TravelTimeMatrix\data\otp-data\Helsinki"

# Build the graph and print the processing outputs, and use 12 Gb of memory for building (makes it faster)
src_file = gbr.OSMGraph().build_otp_graph(data_dir, verbose=False, allocated_memory=12)

# Launch OTP server
mrouter.launch_otp_server(data_dir)
