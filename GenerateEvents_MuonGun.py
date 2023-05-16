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

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outfile", type=str, default="MuonGunSingleMuons_", help="")
parser.add_argument("-r", "--run", type=int, default=0, help="")
parser.add_argument("-g", "--gcdfile", default=os.getenv('PONESRCDIR') +
                    "/GCD/PONE_10String_7Cluster.i3.gz", help="Readin GCD file")
parser.add_argument("-n", "--nevents", type=int, default=10, help="Number of events to run.")

args = parser.parse_args()

cylinder_radius, cylinder_length = get_geo_from_gcd(args.gcdfile)

tray = I3Tray()
tray.AddModule('I3InfiniteSource', Prefix=args.gcdfile)

randomService = phys_services.I3SPRNGRandomService(
    seed=args.run*args.run,
    nstreams=100000000,
    streamnum=args.run)

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
                NumEvents=args.nevents,
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

tray.AddModule('I3Writer', 'writer',
               Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.TrayInfo],
               filename=args.outfile)
tray.Execute()
tray.Finish()
