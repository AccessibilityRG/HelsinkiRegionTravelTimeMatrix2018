# -*- coding: utf-8 -*-
"""
run_otp_validation_tests.py

Run validation analyses using OpenTripPlanner between 100 locations in Helsinki Region.

Created on Thu Jun 13 11:16:36 2019

@author: hentenka
"""
import os
from inspect import getsourcefile

def get_current_dir():
    """Get directory of current file (i.e. where utils.py is located)"""
    return os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))

# Filepaths
mrouter_path = os.path.join(get_current_dir(), "one_to_many_otp.py")

otp_path = "otp-1.3.0-shaded.jar"
base_dir = "data"
data_dir = os.path.join(base_dir, 'otp-data', 'Helsinki')
output_dir = os.path.join(base_dir, 'validation', 'results')
conf_fp = os.path.join(data_dir, 'config_bike.json')
origs_fp = os.path.join(base_dir, 'validation_sample_100_points.csv')
dests_fp = origs_fp
name = "OTP_results_for_validation_Jan_29_2018_fast_biker"
orig_id = 'ID'
dest_id = 'ID'

# Construct command for one-to-many on Windows
print("Go from command prompt to: ", os.path.join(os.path.dirname(mrouter_path), 'bin'))
cmd = "java -cp {otp};jython27.jar org.python.util.jython {router} -c {conf} -g {graph} -o {origins} -d {destinations} -O {outdir} -n {name} -i {orig_id} -I {dest_id}".format(
        otp=otp_path, 
        router=mrouter_path,
        conf=conf_fp,
        graph=data_dir,
        origins=origs_fp,
        destinations=dests_fp,
        outdir = output_dir,
        name = name,
        orig_id = orig_id,
        dest_id = dest_id
              )

print("Run from command prompt:\n", cmd)
