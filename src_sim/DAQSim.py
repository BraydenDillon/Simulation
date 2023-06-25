#!/usr/bin/env python

"""

source: https://github.com/pone-software/pone_offline/tree/master/Examples

"""

import os
from DOM.PONEDOMLauncher import SimpleDOMSimulation
from I3Tray import *
from icecube import icetray, dataio
from icecube import phys_services
import argparse
from Trigger.DOMTrigger import DOMTrigger
from Trigger.DetectorTrigger import DetectorTrigger

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outfile", type=str, default="./test_output.i3",
                    help="Write output to OUTFILE (.i3{.gz} format)")
parser.add_argument("-i", "--infile", type=str, default="./test_input.i3",
                    help="Read input from INFILE (.i3{.gz} format)")
parser.add_argument("-r", "--runnumber", type=int, default="1",
                    help="The run/dataset number for this simulation, is used as seed for random generator")
parser.add_argument("-l", "--filenr", type=int, default=1,
                    help="File number, stream of I3SPRNGRandomService")
parser.add_argument("-g", "--gcdfile", default=os.getenv('PONESRCDIR') +
                    "/GCD/PONE_10String_7Cluster.i3.gz", help="Read in GCD file")
parser.add_argument("-t", "--pulsesep", default=0.2,
                    help="Time needed to separate two pulses. Assume that this is 3.5*sample time.")
parser.add_argument("-e", "--ext", default=".zst", help="compression extension")
parser.add_argument("-s", "--dropstrings", nargs="+", default=[],
                    help="Strings to exclude from geometry")
parser.add_argument("-n", "--nDOMs", type=int, default=2,
                    help="Number of DOMs for detector trigger")

args = parser.parse_args()
photon_series = "I3Photons"
tray = I3Tray()

dropstrings = []
for string in args.dropstrings:
    dropstrings.append(int(string))

# from globals import max_num_files_per_dataset
randomService = phys_services.I3SPRNGRandomService(
    seed=1234567,
    nstreams=10000,
    streamnum=args.runnumber
)

tray.context['I3RandomService'] = randomService

tray.AddModule('I3Reader', 'reader',
               FilenameList=[args.gcdfile, args.infile]
               )

print(args.gcdfile)
gcd_file = dataio.I3File(args.gcdfile)

tray.AddModule(SimpleDOMSimulation, 'DOMLauncher',
               inputmap=photon_series,
               outputmap="PMTResponse",
               RandomService=randomService,
               minTsep=args.pulsesep,
               SplitDoms=True,
               dropstrings=dropstrings,
               add_noise=True
               )

tray.AddModule(DOMTrigger, "DOMTrigger",
               inputmap="PMTResponse",
               )

tray.AddModule(DetectorTrigger, "PONE_Trigger",
               output="_3PMT_2DOM",
               DOMPMTCoinc=3,
               FullDetectorCoincidenceN=args.nDOMs,
               CutOnTrigger=True,
               EventLength=10000,
               TriggerTime=2000,
               PulseSeriesIn="PMTResponse",
               PulseSeriesOut="EventPulseSeries"
               )

tray.AddModule("I3Writer", "writer",
               SkipKeys=["I3Photons"],
               Filename=args.outfile,
               Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.TrayInfo],
               )

tray.AddModule("TrashCan", "adios")

tray.Execute()
tray.Finish()
