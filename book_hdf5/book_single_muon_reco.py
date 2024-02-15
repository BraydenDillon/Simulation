#!/usr/bin/env python

from I3Tray import *
from icecube.hdfwriter import I3HDFWriter
from icecube import dataio, phys_services, dataclasses, recclasses
from icecube import millipede
from icecube.icetray import OMKey

from optparse import OptionParser
import os
from glob import glob

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--infile", default="/home/users/bdillon/P-ONE/sim0002/reco_spline/selection/SingleMuon_*.i3.gz",
                  dest="infile", help="input file (.i3 format)", type=str)
parser.add_argument("-o", "--hdf5file", default="muongun_booking_test.hdf5", type=str,
                  dest="hdf5file", help="output file (.hdf5 format)")

# parse cmd line args,
args = parser.parse_args()

infiles = sorted(glob(args.infile))

tray = I3Tray()

tray.AddModule('I3Reader', 'reader', FilenameList = infiles)

def get_mcmuon(frame):
    mctree = frame["I3MCTree"]
    primary = mctree.primaries[0]
    muon = mctree.get_daughters(primary)[0]
    frame["MCMuon"] = muon
    return True
tray.AddModule(get_mcmuon, 'get_mcmuon')

def get_nchannels_per_event(frame, pulse_key):
    pulsemap = frame[pulse_key]
    nchannel = {}
    for key, pulses in pulsemap:
        npmt_hits = 0
        for pulse in pulses:
            npmt_hits += 1
        if OMKey(key.string, key.om) in nchannel:
            nchannel[OMKey(key.string, key.om)] += npmt_hits
        else:
            nchannel[OMKey(key.string, key.om)] = npmt_hits
    frame['nchannels'] = dataclasses.I3MapKeyDouble(nchannel)
    frame['nchannels_count'] = dataclasses.I3Double(len(nchannel))
    return True

tray.AddModule(get_nchannels_per_event, 'get_nchannels',
	pulse_key='PMTResponse_nonoise')

def qtotal_nhits_event(frame, pulse_key, key_name):
    qtotal = 0
    nhits = 0
    pulsemap = frame[pulse_key]
    for omkey, pulses in pulsemap:
        for pulse in pulses:
            qtotal += pulse.charge
            nhits  += 1
    frame['qtotal_'+key_name] = dataclasses.I3Double(qtotal)
    frame['nhits_'+key_name] = dataclasses.I3Double(nhits)
    return True

tray.AddModule(qtotal_nhits_event, 'qtotal_nhits_unclean', 
               pulse_key='PMTResponse', key_name='unclean')

tray.AddModule(qtotal_nhits_event, 'qtotal_nhits_clean', 
               pulse_key='PMTResponse_nonoise', key_name='clean')

tray.AddSegment(I3HDFWriter, 'hdfwriter',
	Output = args.hdf5file,
	keys = ['I3EventHeader', 'linefit',
         'MCMuon', 'MuonEffectiveArea',
         'LLHFit_mctruth', 'LLHFit_mctruthFitParams',
         'LLHFit_mctruthDirectHitsA',
         'qtotal_clean', 'qtotal_unclean',
         'nhits_clean', 'nhits_unclean',
         'nchannels_count'] #, SubEventStreams = ['fullevent',]
         )

tray.Execute()