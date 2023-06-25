#!/usr/bin/env python

from I3Tray import *
from icecube.hdfwriter import I3HDFWriter
from icecube import dataio, phys_services, dataclasses, recclasses
from icecube import millipede
from icecube.icetray import OMKey

import os
from glob import glob

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-i", "--infile", type=str, default="SingleMuon_100.i3.gz",
                    help="input file (.i3 format)")

parser.add_argument("-r", "--runnumber", type=int, default="1",
                    help="used as seed for random generator")

parser.add_argument("--hdf5file", type=str, default="70_string_muon_gun_reco_mctruth_sim0002.hdf5",
                    help="output file (.hdf5 format)")

args = parser.parse_args()

tray = I3Tray()

# Now fire up the random number generator with that seed
randomService = phys_services.I3SPRNGRandomService(
                seed = int(args.runnumber),
               nstreams = int(4e7),
                streamnum = int(args.runnumber))

tray.context['I3RandomService'] = randomService

infile = args.infile +str(args.runnumber)+".i3.gz"

tray.AddModule('I3Reader', 'reader', FilenameList = [infile])

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

def get_angle(frame, key1, key2):
    angular_error = phys_services.I3Calculator.angle(frame[key1], frame[key2])
    frame["angular_error_"+key1] = dataclasses.I3Double(angular_error)
    return True

tray.AddModule(get_angle, 'angular_linefit', key1 = 'linefit', key2 = 'MCMuon')

tray.AddModule(get_angle, 'angular_mmsreco', key1 = 'LLHFit_mmsreco', key2 = 'MCMuon')

def get_energy(frame):
    frame['zenith_angle'] = dataclasses.I3Double(frame['MCMuon'].dir.zenith)
    frame['muon_energy'] = dataclasses.I3Double(frame['MCMuon'].energy)
    frame['track_length'] = dataclasses.I3Double(frame['LLHFit_mmsrecoDirectHitsA'].dir_track_length)
    frame['logl_mmsreco'] = dataclasses.I3Double(frame['LLHFit_mmsrecoFitParams'].logl)
    frame['event_id'] = dataclasses.I3Double(frame['I3EventHeader'].event_id)
    return True

tray.AddModule(get_energy, 'get_energy')

tray.AddSegment(I3HDFWriter, 'hdfwriter',
	Output = args.hdf5file,
	keys = ['angular_error_linefit',
         'angular_error_LLHFit_mmsreco',
         'LLHFit_mmsrecoDirectHitsA',
         'Qtotal', 'track_length',
         'muon_energy', 'numu_energy',
         'logl_mctruth', 'logl_mmsreco',
         'event_id', 'zenith_angle'
         ])
tray.Execute()