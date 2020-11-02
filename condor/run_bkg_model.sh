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

#export _CONDOR_SCRATCH_DIR=${PWD}
#EXPMT='a0nom_a1inv_2020_07_22_floNone_test1'
EXPMT=${1}
EOSDIR='/store/user/lpchaa4g/mandrews/2017/Jobs'

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

echo "Extracting tarball containing work files..."
tar -xvf h2aa.tgz -C CMSSW_10_5_0/src/
cd CMSSW_10_5_0/src/h2aa/ntupleAnalysis
python run_bkg_model_combo.py

#----------------

#cd CMSSW_10_5_0/src/h2aa/ntupleAnalysis
xrdfs root://cmseos.fnal.gov mkdir $EOSDIR/$EXPMT

for dir in */; do
    dir=${dir%*/}
    tgtdir=$EOSDIR/$EXPMT/$dir
    echo $dir
    xrdfs root://cmseos.fnal.gov mkdir $tgtdir
    xrdmv_with_check $dir root://cmseos.fnal.gov/$tgtdir/
    #xrdmv_with_check $dir root://cmseos.fnal.gov//store/user/lpchaa4g/mandrews/2017/Jobs/$dir/
done

echo "All done!"
set +x

cd -
