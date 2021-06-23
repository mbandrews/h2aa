#!/bin/bash

function xrdmv_with_check {
    if [ "${#}" != 2  ]; then
        echo "ERROR: number of arguments passed to \"${FUNCNAME}\": ${#}"
        exit 1
    fi
    #xrdcp -r --verbose --force --path --streams 15 ${1} ${2} 2>&1
    xrdcp -r --force --path --streams 15 ${1} ${2} 2>&1
    #XRDEXIT=${?}
    #if [[ ${XRDEXIT} -ne 0 ]]; then
    #    rm -f *.root
    #    echo "exit code ${XRDEXIT}, failure in xrdcp"
    #    exit ${XRDEXIT}
    #fi
    #rm ${1}
}

export _CONDOR_SCRATCH_DIR=${PWD}
EOSREDIR='root://cmseos.fnal.gov/'
SAMPLE=${1}
INLIST=${2}
EOSTGT=${3}
TARFILE=${4}
PUJSON=${5}
OUTDIR='Templates'

# Get input files
echo $INLIST

cd ${_CONDOR_SCRATCH_DIR}

# Source CMSSW environment
echo "Sourcing CMSSW environment..."
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
eval `scramv1 project CMSSW CMSSW_10_5_0`
cd CMSSW_10_5_0/src/
eval `scramv1 runtime -sh` # cmsenv is not an alias on the workers
echo "CMSSW: "${CMSSW_BASE}
cd ${_CONDOR_SCRATCH_DIR}

echo ">> Extracting tarball containing work files..."
mkdir -p CMSSW_10_5_0/src/h2aa
tar -xvf $TARFILE -C CMSSW_10_5_0/src/h2aa/
mv $INLIST CMSSW_10_5_0/src/h2aa/zeeAnalysis/
mv $PUJSON CMSSW_10_5_0/src/h2aa/zeeAnalysis/
cd CMSSW_10_5_0/src/h2aa/zeeAnalysis
mkdir -p $OUTDIR
# NOTE: pu_json parameter ignored for MC inside select_events.py so safe to always pass it here
python select_events.py -s $SAMPLE --inlist $INLIST -o $OUTDIR --pu_json $PUJSON
#python select_events.py -s $SAMPLE --inlist $INLIST -o $OUTDIR --pu_json $PUJSON -e 100

#----------------

echo ">> Done processing"
echo ">> Copying files to $EOSTGT"
xrdfs root://cmseos.fnal.gov mkdir -p $EOSTGT

cp ${_CONDOR_SCRATCH_DIR}/recursiveFileList.py ${_CONDOR_SCRATCH_DIR}/xrdcpRecursive.py .

for dir in */; do
    dir=${dir%*/}
    tgtdir=$EOSTGT/$dir
    echo ">> Copying dir: $(pwd)/$dir to $tgtdir"
    python xrdcpRecursive.py -s $(pwd)/$dir -t $tgtdir
done

echo "All done!"
set +x

cd -
