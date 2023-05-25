#!/bin/bash
envs=/home/users/bdillon/pone_offline/env-shell_Container.sh
pyfile=/home/users/bdillon/P-ONE/sim0001/src_sim/GenerateEvents_MuonGun.py
gcd=/home/users/bdillon/P-ONE/sim0001/gcdfile/PONE_10String_7Cluster_standard.i3.gz
outfile=/home/users/bdillon/P-ONE/sim0001/muonprop
for i in $(seq 0 1 999)
do
	./submit_job.sh bash $envs python $pyfile -g $gcd -o $outfile/GenerateSingleMuons_$i.i3.gz -n 100 -r $i
done
