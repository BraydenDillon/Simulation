#!/bin/bash
envs=/home/users/twagiray/pone_offline/env-shell_Container.sh
pyfile=/data/p-one/sim/muongun/sim0005/src/GenerateEvents_MuonGun.py
gcd=/data/p-one/sim/muongun/sim0005/gcdfile/PONE_10String_7Cluster_standard.i3.gz
outfile=/data/p-one/sim/muongun/sim0005/muonprop
for i in $(seq 0 1 999)
do
	./submit_job.sh bash $envs python $pyfile -g $gcd -o $outfile/GenerateSingleMuons_$i.i3.gz -n 500 -r $i
done
