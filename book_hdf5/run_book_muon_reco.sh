#!/bin/bash
envs=/home/users/twagiray/icetray/build/env-shell.sh
pyfile=/home/users/bdillon/P-ONE/sim0002/book_hdf5/book_single_muon_reco.py
./submit_job.sh $envs python $pyfile
echo All done
