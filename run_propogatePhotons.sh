#!/bin/bash
envs=/home/users/bdillon/pone_offline/env-shell_Container.sh
infile=/home/users/bdillon/P-ONE/sim0001/muonprop/*.i3.gz
pyfile=/home/users/bdillon/P-ONE/sim0001/src/PropogatePhotons.py
gcd=/home/users/bdillon/P-ONE/sim0001/gcdfile/PONE_10String_7Cluster_standard.i3.gz
outfile=/home/users/bdillon/P-ONE/sim0001/photonprop
for file in $infile
do
    ./submit_job.sh bash $envs python $pyfile -i $file -g $gcd -o $outfile/$(basename $file .i3.gz)_photonprop.i3.gz
done
