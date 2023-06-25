#!/bin/sh

# creating output directories
mkdir -p npx3-execs npx3-logs npx3-out npx3-error

# creating execution script, do not delete until job has started!
echo "#!/bin/bash" > npx3-execs/npx3-$$.sh
echo "date" >> npx3-execs/npx3-$$.sh
echo "hostname" >> npx3-execs/npx3-$$.sh
echo "cd `pwd`" >> npx3-execs/npx3-$$.sh

# set up new tools
echo "$@" >> npx3-execs/npx3-$$.sh
echo "date" >> npx3-execs/npx3-$$.sh

chmod +x npx3-execs/npx3-$$.sh

# creating condor submission script
echo "Universe  = vanilla" > 2sub.sub
echo "executable = npx3-execs/npx3-$$.sh" >> 2sub.sub

echo "log = npx3-logs/npx3-$$.log" >> 2sub.sub
echo "output = npx3-out/npx3-$$.out" >> 2sub.sub
echo "error = npx3-error/npx3-$$.error" >> 2sub.sub

echo '+SingularityImage = "/data/p-one/icetray_offline_june24_2022.sif"' >> 2sub.sub

echo "request_cpus = 1" >> 2sub.sub
#echo "request_gpus = 1" >> 2sub.sub
echo "request_memory = 4GB" >> 2sub.sub
echo "requirements = HasSingularity" >> 2sub.sub

echo "notification = never" >> 2sub.sub

echo "queue" >> 2sub.sub
condor_submit 2sub.sub
