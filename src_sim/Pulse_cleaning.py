#!/usr/bin/env python3

"""

source: https://github.com/pone-software/pone_offline/tree/master/Examples

"""

from icecube import icetray, dataio, dataclasses, phys_services
from icecube import interfaces, simclasses, sim_services
from PulseCleaning.ClusterSelect import ClusterPulseCleaning
from PulseCleaning.CausalHits import CausalPulseCleaning
from Reconstruction.Linefit.LineFitReco import LineFitReco
from I3Tray import *
import sys
import time

import argparse

parser = argparse.ArgumentParser(
    description="Takes I3Photons from step2 of the simulations and generates DOM hits"
)
parser.add_argument(
    "-i",
    "--infile",
    default="./test_input.i3",
    help="Write output to OUTFILE (.i3{.gz} format)",
)
parser.add_argument(
    "-o",
    "--outfile",
    default="./test_output.i3",
    help="Write output to OUTFILE (.i3{.gz} format)",
)
parser.add_argument(
    "-g", "--gcdfile", default="./PONE_Phase1.i3.gz", help="Read in GCD file"
)
args = parser.parse_args()

tray = I3Tray()
tray.context["I3RandomService"] = phys_services.I3GSLRandomService(42)

tray.Add("I3Reader", FilenameList=[args.gcdfile, args.infile])

# Create P-Frame needed for strippedreco
tray.AddModule("I3NullSplitter", "fullevent")

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

tray.Add("I3Writer", Filename=args.outfile,
        Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
        DropOrphanStreams=[icetray.I3Frame.Calibration, icetray.I3Frame.DAQ])

tray.Execute()
tray.Finish()