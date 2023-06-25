#!/usr/bin/env python3

from icecube import icetray, dataio, dataclasses
from icecube.common_variables import direct_hits
from icecube import phys_services
from I3Tray import *
import numpy as np

import argparse

parser = argparse.ArgumentParser(
    description="Takes I3Photons from step2 of the simulations and generates DOM hits"
)
parser.add_argument(
    "-i",
    "--infile",
    default="./test_input.i3.gz",
    help="Write output to OUTFILE (.i3{.gz} format)",
)

parser.add_argument("-r", "--runnumber", type=int, default="1", 
                    help="used as seed for random generator")

parser.add_argument(
    "-o",
    "--outfile",
    default="./test_output.i3.gz",
    help="Write output to OUTFILE (.i3{.gz} format)",
)
parser.add_argument(
    "-g", "--gcdfile", default="./PONE_Phase1.i3.gz", help="Read in GCD file"
)
args = parser.parse_args()

pulses_map_name    = 'PMTResponse_nonoise'
reco_particle_name = 'LLHFit_mmsreco'

dh_defs = [
    direct_hits.I3DirectHitsDefinition("A", -15*I3Units.ns, 15*I3Units.ns)
]

tray = I3Tray()

# Now fire up the random number generator with that seed
randomService = phys_services.I3SPRNGRandomService(
                seed = int(args.runnumber),
               nstreams = int(4e7),
                streamnum = int(args.runnumber))

tray.context['I3RandomService'] = randomService

infile = args.infile +str(args.runnumber)+".i3.gz"
outfile = args.outfile +str(args.runnumber)+".i3.gz"

tray.Add("I3Reader", FilenameList=[args.gcdfile, infile])

tray.AddSegment(direct_hits.I3DirectHitsCalculatorSegment, 'dh_reco',
    DirectHitsDefinitionSeries       = dh_defs,
    PulseSeriesMapName               = pulses_map_name,
    ParticleName                     = reco_particle_name,
    OutputI3DirectHitsValuesBaseName = reco_particle_name+'DirectHits',
    BookIt                           = True
)

tray.Add("I3Writer", Filename = outfile,
        Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
        DropOrphanStreams=[icetray.I3Frame.Calibration, icetray.I3Frame.DAQ])

tray.Execute()
tray.Finish()