#!/usr/bin/env python3

"""

source: https://github.com/pone-software/pone_offline/tree/master/Examples

"""

from os.path import expandvars
import os, sys, random
import time
from I3Tray import *
from icecube import icetray, dataio, dataclasses, phys_services
from icecube import interfaces, simclasses, sim_services
from PulseCleaning.ClusterSelect import ClusterPulseCleaning
from PulseCleaning.CausalHits import CausalPulseCleaning
from Reconstruction.Linefit.LineFitReco import LineFitReco


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outfile",type = str, default="./test_output.i3", 
                    help="Write output to OUTFILE (.i3{.gz} format)")
parser.add_argument("-i", "--infile",type=str, default="./test_input.i3", 
                    help="Read input from INFILE (.i3{.gz} format)")
parser.add_argument("-r", "--runnumber", type=int, default="1", 
                    help="The run/dataset number for this simulation, is used as seed for random generator")

parser.add_argument("-g", "--gcdfile", default=os.getenv('PONESRCDIR')+"/GCD/PONE_Phase1.i3.gz", help="Read in GCD file")
parser.add_argument("-e", "--ext",default=".gz",help="compression extension")

args = parser.parse_args()
photon_series = "I3Photons"
tray = I3Tray()

# Now fire up the random number generator with that seed
randomService = phys_services.I3SPRNGRandomService(
                seed = int(args.runnumber),
               nstreams = int(4e7),
                streamnum = int(args.runnumber))

tray.context['I3RandomService'] = randomService

infile = args.infile +str(args.runnumber)+".i3"+args.ext
outfile = args.outfile +str(args.runnumber)+".i3"+args.ext

tray.AddModule('I3Reader', 'reader',
            FilenameList = [args.gcdfile, infile]
            )

# This pulse cleaning is promissing but still experimental.
tray.AddModule(CausalPulseCleaning, "CausalHit",
               # GCDFile=args.gcdfile,
               inputseries="PMTResponse",
               output="PMTResponse_clean"
               )
tray.AddModule(ClusterPulseCleaning, "ClusterHit",
               # GCDFile=gcd_file,
               inputseries="PMTResponse_clean",
               output="PMTResponse_clean_cluster"
               )

# Linefit for tracks
tray.AddModule(LineFitReco, "LineFit", inputseries="PMTResponse_clean_cluster", output="linefit")

def set_time_zero(frame):
    linefit = frame['linefit']
    newseed = dataclasses.I3Particle(linefit)
    newseed.time = 0.0
    frame['linefit_time'] = newseed
tray.Add(set_time_zero, "set_time_zero")


tray.Add("I3Writer", Filename = outfile,
        Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
        DropOrphanStreams=[icetray.I3Frame.Calibration, icetray.I3Frame.DAQ])

tray.Execute()
tray.Finish()