#!/bin/bash

# Creating output directories
basedir=/home/users/bdillon/P-ONE/sim0002/book_hdf5

mkdir -p $basedir/npx3-execs $basedir/npx3-logs $basedir/npx3-out $basedir/npx3-error

# Creating execution script, do not delete until job has started!
echo "#!/bin/bash" > $basedir/npx3-execs/npx3-$$.sh

#Set up new tools

echo "eval \`/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/setup.sh\`" >> $basedir/npx3-execs/npx3-$$.sh

echo "$@" >> $basedir/npx3-execs/npx3-$$.sh

chmod +x npx3-execs/npx3-$$.sh

# Creating condor submission script (ClassAd)
echo "Universe  = vanilla" > 2sub.sub
echo "Notification = NEVER" >> 2sub.sub
echo "request_memory = 2GB" >> 2sub.sub
echo "request_cpus = 1" >> 2sub.sub

echo "Executable = $basedir/npx3-execs/npx3-$$.sh" >> 2sub.sub
echo "Log =  $basedir/npx3-logs/npx3-$$.log" >> 2sub.sub
echo "Output = $basedir/npx3-out/npx3-$$.out" >> 2sub.sub
echo "Error = $basedir/npx3-error/npx3-$$.error" >> 2sub.sub

echo "Queue" >> 2sub.sub
condor_submit 2sub.sub
