#!/bin/bash

export _CONDOR_SCRATCH_DIR=${PWD}
EOSREDIR='root://cmseos.fnal.gov/'
SAMPLE=${1}
INLIST=${2}
INPUDATA=${3}
EOSTGT=${4}
INPHOIDSYST=${5}
TARFILE=${6}
DOTRGSF=${7}

# Get input files
echo ">> Getting input files..."
echo $INLIST

cd ${_CONDOR_SCRATCH_DIR}

# Source CMSSW environment
echo ">> Sourcing CMSSW environment..."
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
eval `scramv1 project CMSSW CMSSW_10_5_0`
cd CMSSW_10_5_0/src/
eval `scramv1 runtime -sh` # cmsenv is not an alias on the workers
echo "CMSSW: "${CMSSW_BASE}
cd ${_CONDOR_SCRATCH_DIR}

echo ">> Extracting tarball containing work files..."
mkdir -p CMSSW_10_5_0/src/h2aa
#tar -xvf h2aa.tgz -C CMSSW_10_5_0/src/h2aa/
tar -xvf $TARFILE -C CMSSW_10_5_0/src/h2aa/

echo ">> Running signal selection..."
if [ $INPHOIDSYST == "NONE" ]; then
    echo "   .. running without pho ID systs"
    mv $INLIST $INPUDATA CMSSW_10_5_0/src/h2aa/ntupleAnalysis/
    cd CMSSW_10_5_0/src/h2aa/ntupleAnalysis
    if [ $DOTRGSF == "TRUE" ]; then
        echo "   .. will apply trg SFs"
        python run_sg_selection.py -s $SAMPLE --inlist $INLIST --pu_data $INPUDATA --do_systTrgSF
    else
        echo "   .. will NOT apply trg SFs"
        python run_sg_selection.py -s $SAMPLE --inlist $INLIST --pu_data $INPUDATA
    fi
else
    echo "   .. running with pho ID systs"
    mv $INLIST $INPUDATA $INPHOIDSYST CMSSW_10_5_0/src/h2aa/ntupleAnalysis/
    cd CMSSW_10_5_0/src/h2aa/ntupleAnalysis
    if [ $DOTRGSF == "TRUE" ]; then
        echo "   .. will apply trg SFs"
        python run_sg_selection.py -s $SAMPLE --inlist $INLIST --pu_data $INPUDATA --systPhoIdFile $INPHOIDSYST --do_systTrgSF
    else
        echo "   .. will NOT apply trg SFs"
        python run_sg_selection.py -s $SAMPLE --inlist $INLIST --pu_data $INPUDATA --systPhoIdFile $INPHOIDSYST
    fi
fi

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

echo ">> All done!"
set +x

cd -
