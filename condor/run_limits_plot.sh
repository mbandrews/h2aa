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
#SAMPLE=${1}
MODELS=${1}
DCARD=${2}
EOSTGT=${3}
TARFILE=${4}
#NCPUS=1

# Get input files
#echo ">> Doing sample: $SAMPLE"
echo ".. Datacard: $DCARD"

cd ${_CONDOR_SCRATCH_DIR}

# Source CMSSW environment
echo ">> Sourcing CMSSW environment..."
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
CMSSW_REL=CMSSW_10_2_13
eval `scramv1 project CMSSW $CMSSW_REL`
cd ${CMSSW_REL}/src/
eval `scramv1 runtime -sh` # cmsenv is not an alias on the workers
echo "CMSSW: "${CMSSW_BASE}
cd ${_CONDOR_SCRATCH_DIR}

echo ">> Extracting tarball containing work files..."
tar -xvf $TARFILE -C ${CMSSW_REL}/src/

echo ">> Copying work files..."
mv $MODELS $DCARD ${CMSSW_REL}/src/

echo ">> Compiling combine tools..."
cd ${CMSSW_REL}/src/
eval `scramv1 build` #

# MAIN
echo ">> Making limit plot..."
python get_limits.py -i $DCARD -o . &> upperlimits.log

echo ">> Done processing"
echo ">> Copying files to $EOSTGT"
xrdfs root://cmseos.fnal.gov mkdir -p $EOSTGT

#cp ${_CONDOR_SCRATCH_DIR}/recursiveFileList.py ${_CONDOR_SCRATCH_DIR}/xrdcpRecursive.py .

for f in *.log; do
    xrdmv_with_check $f root://cmseos.fnal.gov/$EOSTGT/
done

for f in *.txt; do
    xrdmv_with_check $f root://cmseos.fnal.gov/$EOSTGT/
done

for f in *.root; do
    xrdmv_with_check $f root://cmseos.fnal.gov/$EOSTGT/
done

for f in *.pdf; do
    xrdmv_with_check $f root://cmseos.fnal.gov/$EOSTGT/
done

echo ">> All done!"
set +x

cd -
