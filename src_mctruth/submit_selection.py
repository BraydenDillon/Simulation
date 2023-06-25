#!/usr/bin/env python
import os, sys
import subprocess

opts = {}
opts["out"] = '/home/users/bdillon/P-ONE/sim0002/reco_mctruth/selection'
opts["data"] = '/home/users/bdillon/P-ONE/sim0002/reco_mctruth'
opts["job"] = '/home/users/bdillon/P-ONE/sim0002/src_mctruth'
opts["gcd"] = '/home/users/bdillon/P-ONE/sim0002/gcdfile'

processfilename = 'run_selection'
submissionfilename = 'run_selection.submit'

job_string = '''#!/bin/bash

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/setup.sh`

bash /data/p-one/twagiray/trackreco/common_variables/env-shell.sh python {}/make_ldir_selection.py -i {} -o {} -r $1 -g {}

'''.format(opts["job"],
           opts["data"]+"/SingleMuon_",
           opts["out"]+"/SingleMuon_",
           opts["gcd"]+"/PONE_10String_7Cluster_standard.i3.gz")

with open(opts["job"] + "/" + processfilename + '.sh', 'w') as ofile:
	ofile.write(job_string)
	subprocess.Popen(['chmod','777',opts["job"] + "/" +  processfilename + '.sh'])

submit_string = '''
executable = {}/{}

Arguments = $(Item)
output = {}_$(Item).out
error = {}_$(Item).err
log = {}_$(Item).log


Universe = vanilla
request_memory = 4GB
request_cpus = 1
requirements = HasSingularity
requirements = CUDADeviceName == "NVIDIA TITAN Xp"

notification = never

+TransferOutput=""

queue from seq {} {} |
'''.format(opts["job"],
           processfilename + '.sh',
           opts["job"]+"/out/"+processfilename,
           opts["job"]+"/error/"+processfilename,
           opts["job"]+"/log/"+processfilename,
           1, 10)

with open(opts["job"] + "/" +  submissionfilename, 'w') as ofile:
	ofile.write(submit_string)

submit = subprocess.Popen(['condor_submit', opts["job"] + "/" + submissionfilename])
