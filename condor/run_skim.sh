#!/bin/bash

echo ">> Opened bash execution script"

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
INLIST=${1}
EOSTGT=${2}

cd ${_CONDOR_SCRATCH_DIR}

# Source CMSSW environment
echo ">> Sourcing CMSSW environment..."
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
eval `scramv1 project CMSSW CMSSW_10_5_0`
cd CMSSW_10_5_0/src/
eval `scramv1 runtime -sh` # cmsenv is not an alias on the workers
echo ">> CMSSW: "${CMSSW_BASE}
cd ${_CONDOR_SCRATCH_DIR}

echo ">> Extracting tarball containing work files..."
mkdir -p CMSSW_10_5_0/src/h2aa
tar -xvf h2aa.tgz -C CMSSW_10_5_0/src/h2aa/
mv $INLIST CMSSW_10_5_0/src/h2aa/ntupleAnalysis/
cd CMSSW_10_5_0/src/h2aa/ntupleAnalysis

echo ">> Starting python script..."
python skim_ntuple.py -i $INLIST

#----------------

echo ">> Done processing"
echo ">> Copying files to $EOSTGT"
xrdfs root://cmseos.fnal.gov mkdir -p $EOSTGT

for dir in */; do
    dir=${dir%*/}
    tgtdir=$EOSTGT/$dir
    echo ">> Copying dir: $dir to $tgtdir"
    xrdfs root://cmseos.fnal.gov mkdir -p $tgtdir
    xrdmv_with_check $dir root://cmseos.fnal.gov/$tgtdir/
done

echo ">> All done!"
set +x

cd -
