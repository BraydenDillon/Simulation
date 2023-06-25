#!/usr/bin/env python3

from icecube import icetray, dataio, dataclasses, phys_services
from icecube import gulliver, lilliput, gulliver_modules
from I3Tray import *
import sys
import time
import numpy as np

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

parser.add_argument("-r", "--runnumber", type=int, default="1", 
                    help="used as seed for random generator")

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

load("mmsreco")

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

def make_seed(frame):
    newseed = frame['MCMuon']
    newseed.fit_status = dataclasses.I3Particle.FitStatus.OK
    newseed.shape = dataclasses.I3Particle.InfiniteTrack
    frame['MCTruth_seed'] = newseed
tray.AddModule(make_seed, 'make_seed')

PulsesName = "PMTResponse_nonoise"

tray.AddService(
    "I3GSLSimplexFactory",
    "minimizeit",
    Tolerance=0.01,
    SimplexTolerance=0.001,
    MaxIterations=50000,
)

# parameterization:
tray.AddService("I3HalfSphereParametrizationFactory", "simpleparam",
        DirectionStepsize = 0.3 * I3Units.deg,
        VertexStepsize = 5 * I3Units.m,
        TimeStepsize = 1 * I3Units.ns)

#-------------------------------------------------------------
tray.AddService("I3BasicSeedServiceFactory", "seed1", FirstGuess="linefit", InputReadout="PMTResponse_nonoise")

tray.AddService("MMSLikelihoodFactory", "mmsreco_step1",
                InputPulses=PulsesName,  ExpectNoise=True, ConvolutionWidth=35.0,
                SplineTablePath="/data/p-one/twagiray/trackreco/src_mmsreco/mmsreco/water.fits")

tray.AddModule("I3SimpleFitter", "LLHFit_step1",
        SeedService = "seed1",
        Parametrization = "simpleparam",
        LogLikelihood = "mmsreco_step1",
        Minimizer = "minimizeit",
        StoragePolicy = "OnlyBestFit",
        If = lambda frame: PulsesName in frame and "linefit" in frame,
        OutputName = "LLHFit_step1")

#-------------------------------------------------------------
tray.AddService("I3BasicSeedServiceFactory", "seed2", FirstGuess="LLHFit_step1")

tray.AddService("MMSLikelihoodFactory", "mmsreco_step2",
                InputPulses=PulsesName,  ExpectNoise=True, ConvolutionWidth=20.0,
                SplineTablePath="/data/p-one/twagiray/trackreco/src_mmsreco/mmsreco/water.fits")

tray.AddModule("I3SimpleFitter", "LLHFit_step2",
        SeedService = "seed2",
        Parametrization = "simpleparam",
        LogLikelihood = "mmsreco_step2",
        Minimizer = "minimizeit",
        StoragePolicy = "OnlyBestFit",
        If = lambda frame: PulsesName in frame and "LLHFit_step1" in frame,
        OutputName = "LLHFit_step2")

#-------------------------------------------------------------
tray.AddService("I3BasicSeedServiceFactory", "seed3", FirstGuess="LLHFit_step2")

tray.AddService("MMSLikelihoodFactory", "mmsreco_step3",
                InputPulses=PulsesName,  ExpectNoise=True, ConvolutionWidth=10.0,
                SplineTablePath="/data/p-one/twagiray/trackreco/src_mmsreco/mmsreco/water.fits")

tray.AddModule("I3SimpleFitter", "LLHFit_step3",
        SeedService = "seed3",
        Parametrization = "simpleparam",
        LogLikelihood = "mmsreco_step3",
        Minimizer = "minimizeit",
        StoragePolicy = "OnlyBestFit",
        If = lambda frame: PulsesName in frame and "LLHFit_step2" in frame,
        OutputName = "LLHFit_step3")

#-------------------------------------------------------------
tray.AddService("I3BasicSeedServiceFactory", "seed4", FirstGuess="LLHFit_step3")

tray.AddService("MMSLikelihoodFactory", "mmsreco_step4",
                InputPulses=PulsesName,  ExpectNoise=True, ConvolutionWidth=5.0,
                SplineTablePath="/data/p-one/twagiray/trackreco/src_mmsreco/mmsreco/water.fits")

tray.AddModule("I3SimpleFitter", "LLHFit_step4",
        SeedService = "seed4",
        Parametrization = "simpleparam",
        LogLikelihood = "mmsreco_step4",
        Minimizer = "minimizeit",
        StoragePolicy = "OnlyBestFit",
        If = lambda frame: PulsesName in frame and "LLHFit_step3" in frame,
        OutputName = "LLHFit_step4")
#-------------------------------------------------------------
tray.AddService("I3BasicSeedServiceFactory", "seed5", FirstGuess="LLHFit_step4")

tray.AddService("MMSLikelihoodFactory", "mmsreco_final",
                InputPulses=PulsesName,  ExpectNoise=True, ConvolutionWidth=0.0,
                SplineTablePath="/data/p-one/twagiray/trackreco/src_mmsreco/mmsreco/water.fits")

tray.AddModule("I3SimpleFitter", "LLHFit_mmsreco",
        SeedService = "seed5",
        Parametrization = "simpleparam",
        LogLikelihood = "mmsreco_final",
        Minimizer = "minimizeit",
        StoragePolicy = "OnlyBestFit",
        If = lambda frame: PulsesName in frame and "LLHFit_step4" in frame,
        OutputName = "LLHFit_mmsreco")


tray.Add("I3Writer", Filename = outfile,
        Streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
        DropOrphanStreams=[icetray.I3Frame.Calibration, icetray.I3Frame.DAQ])

tray.Execute()
tray.Finish()