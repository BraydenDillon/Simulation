#!/bin/bash
envs=/home/users/twagiray/pone_offline/env-shell_Container.sh
infile=/data/p-one/sim/muongun/sim0005/muonprop/*.i3.gz
pyfile=/data/p-one/sim/muongun/sim0005/src/PropogatePhotons.py
gcd=/data/p-one/sim/muongun/sim0005/gcdfile/PONE_10String_7Cluster_standard.i3.gz
outfile=/data/p-one/sim/muongun/sim0005/photonprop
for file in $infile
do
    ./submit_job.sh bash $envs python $pyfile -i $file -g $gcd -o $outfile/$(basename $file .i3.gz)_photonprop.i3.gz
done
