# -*- coding: utf-8 -*-
"""
build_otp_graph.py 

Created on Wed Jun 12 15:47:57 2019

@author: hentenka
"""
import os
import os
from sys import platform
import subprocess
import shutil


def build_otp_graph(data_dir, otp_path, verbose=False, allocated_memory=12):
    """Builds OpenTripPlanner graph based on data found in data_dir"""
    cmd = "java -Xmx{allocated_memory} -jar {otp_exe} --build {otp_data_dir} --basePath {otp_data_dir} --analyst".format(
        otp_data_dir=data_dir, otp_exe=otp_path, allocated_memory="%sG" % allocated_memory)

    print("Building OTP graph. This will take a while..")
    if platform == "linux" or platform == "linux2":
        subprocess.call(["screen", "-S", "otp_graphbuilder", "-d", "-c", cmd], cwd=get_current_dir())
    else:
        result = subprocess.Popen(cmd, shell=True, bufsize=1, stdout=subprocess.PIPE)
        for line in result.stdout:
            if verbose:
                print(line.decode('utf-8'))

# Filepaths
data_dir = "data"
otp_path = "bin/otp-1.3.0-shaded.jar"

# Build the OpenTripPlanner graph using 12 Gb of memory for building 
build_otp_graph(data_dir=data_dir, otp_path=otp_path, verbose=True, allocated_memory=12)
