#!/usr/bin/env python

"""

source: https://github.com/pone-software/pone_offline/tree/master/Examples

"""

# import required icecube-related stuff
from icecube import icetray
from icecube.icetray import I3Units
from I3Tray import I3Tray
import icecube
# command line options required to configure the simulation
import argparse
import os
from icecube import phys_services
from segments.GenerateCosmicRayMuons import GenerateSingleMuons
from segments import PropagateMuons
from Utilities.GeoUtility import get_geo_from_gcd

import os
from os.path import expandvars
import numpy as np
import argparse

parser = argparse.ArgumentParser(description = "A scripts to run the neutrino generation simulation step using Neutrino Generator")

parser.add_argument("-o", "--outfile", type=str, default="MuonGunSingleMuons_", help="")
parser.add_argument("-r", "--runnumber", type=int, default="1", 
                    help="The run/dataset number for this simulation, is used as seed for random generator")
parser.add_argument("-g", "--gcdfile", default=os.getenv('PONESRCDIR') +
                    "/GCD/PONE_10String_7Cluster.i3.gz", help="Readin GCD file")
parser.add_argument("-n", "--numEvents", type=int, default=10, help="Number of events to run.")

args = parser.parse_args()

numEvents = int(args.numEvents)

cylinder_radius, cylinder_length = get_geo_from_gcd(args.gcdfile)

tray = I3Tray()
tray.AddModule('I3InfiniteSource', Prefix=args.gcdfile)

# Now fire up the random number generator with that seed
randomService = phys_services.I3SPRNGRandomService(
                seed = int(args.runnumber),
               nstreams = int(4e7),
                streamnum = int(args.runnumber))

tray.context['I3RandomService'] = randomService

tray.Add("I3MCEventHeaderGenerator",
         EventID=1,
         IncrementEventID=True)

surface_center = icecube.dataclasses.I3Position(
    0.0*icecube.icetray.I3Units.m, 0.0*I3Units.m, 0.0*I3Units.m)

surface = icecube.MuonGun.Cylinder(length=cylinder_length*I3Units.m,
                                   radius=cylinder_radius*I3Units.m, center=surface_center)

tray.AddSegment(GenerateSingleMuons, "makeMuons",
                Surface=None,  #surface
                GCDFile=args.gcdfile,
                GeometryMargin=60.*I3Units.m,
                NumEvents=args.numEvents,
                FromEnergy=100.*I3Units.GeV,
                ToEnergy=1.*I3Units.PeV,
                BreakEnergy=1.*I3Units.TeV,
                GammaIndex=1.,
                ZenithRange=[0., 180.0*I3Units.deg]
                )

tray.Add(PropagateMuons, 'ParticlePropagators',
         RandomService=randomService,
         SaveState=True,
         InputMCTreeName="I3MCTree_preMuonProp",
         OutputMCTreeName="I3MCTree",
         PROPOSAL_config_file=os.getenv('PONESRCDIR')+"/configs/PROPOSAL_config.json")

event_id = 1
def get_header(frame):
    global event_id 
    header          = icecube.dataclasses.I3EventHeader()
    header.event_id = event_id
    header.run_id   = int(args.runnumber)
    frame.Delete("I3EventHeader")
    frame["I3EventHeader"] = header
    event_id += 1
tray.AddModule(get_header, streams = [icetray.I3Frame.DAQ])

tray.Add("I3Writer", filename = args.outfile+"_"+str(args.runnumber)+".i3.gz",
        streams = [icetray.I3Frame.TrayInfo, icetray.I3Frame.DAQ],)

tray.Execute()
tray.Finish()