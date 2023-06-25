
"""

source: https://github.com/pone-software/pone_offline/tree/master/Examples

"""

import argparse
import os
from I3Tray import *
from icecube import icetray
from icecube import phys_services
from icecube import clsim
# import WaterOpticalModel.MakePoneMediumPropertiesConservative as Medium
import WaterOpticalModel.MakePoneMediumPropertiesSpeculativeExtendedRange as Medium
from Utilities.DOMUtility import DOMProperties

parser = argparse.ArgumentParser(
    description="Takes I3Photons from step2 of the simulations and generates DOM hits")
parser.add_argument("-i", "--infile", default="./test_input.i3",
                    help="Write output to OUTFILE (.i3{.gz} format)")
parser.add_argument("-o", "--outfile", default="./test_output.i3",
                    help="Write output to OUTFILE (.i3{.gz} format)")
parser.add_argument("-r", "--runnumber", type=int, default=1,
                    help="The run/dataset number for this simulation, is used as seed for random generator")
parser.add_argument("-l", "--filenr", type=int, default=1,
                    help="File number, stream of I3SPRNGRandomService")
parser.add_argument("-g", "--gcdfile", default=os.getenv('PONESRCDIR') +
                    "/GCD/PONE_10String_7Cluster.i3.gz", help="Read in GCD file")
parser.add_argument("-e", "--efficiency", type=float, default=1.0,
                    help="DOM Efficiency ... the same as UnshadowedFraction")
parser.add_argument("-m", "--mctree", default="I3MCTree", help="I3MCTree to go into clsim")
parser.add_argument("-c", "--crossenergy", type=float, default=200.0,
                    help="The cross energy where the hybrid clsim approach will be used")
parser.add_argument("-f", "--frames", type=int, default=100, help="N Frames")
args = parser.parse_args()

# load DOM properties
dom_properties = DOMProperties()

photon_series = "I3Photons"

tray = I3Tray()

# Now fire up the random number generator with that seed
# from globals import max_num_files_per_dataset
randomService = phys_services.I3SPRNGRandomService(
    seed=int(args.runnumber),
    nstreams=int(4e7),
    streamnum=int(args.runnumber))

tray.context['I3RandomService'] = randomService

tray.AddModule('I3Reader', 'reader',
               FilenameList=[args.infile]
               )

tray.AddSegment(clsim.I3CLSimMakePhotons, 'goCLSIM',
                # UseCPUs=True,
                UseGPUs=True,
                MCTreeName=args.mctree,
                UseI3PropagatorService=False,
                PhotonSeriesName=photon_series,
                MCPESeriesName='',
                RandomService=randomService,
                IceModelLocation=Medium.MakePoneMediumProperties(),
                UnWeightedPhotons=False,
                # UnWeightedPhotonsScalingFactor = None,
                DOMRadius=(17.0*2.54*0.01/2.0)*icetray.I3Units.m,
                UseGeant4=False,
                CrossoverEnergyEM=None,
                PhotonHistoryEntries=0,
                StopDetectedPhotons=True,
                DoNotParallelize=False,
                WavelengthAcceptance=dom_properties.GetCLSimQETable(
                    factor=dom_properties.GetMaxAngularAcceptance()*1.05),
                DOMOversizeFactor=1.0,  # (17./13.),
                UnshadowedFraction=1.,  # normal in IC79 and older CLSim versions was 0.9, now it is 1.0
                GCDFile=args.gcdfile,  # gcd_file,
                )

tray.AddModule("I3Writer", "writer",
               # SkipKeys=SkipKeys,
               Filename=args.outfile,
               Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.TrayInfo],
               )

tray.AddModule("TrashCan", "adios")

tray.Execute()
tray.Finish()
