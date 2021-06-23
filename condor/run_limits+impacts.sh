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
MODELS=${2}
DCARD=${3}
EOSTGT=${4}
TARFILE=${5}
NCPUS=10
#NCPUS=4

#NOTE: $DCARD == $SAMPLE.txt

# Get input files
echo ">> Doing sample: $SAMPLE"
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

echo ">> Running impacts..."

# Impacts, with signal [per Nadya]
text2workspace.py $DCARD -m 125
#combineTool.py -M Impacts -m 125 -d ${SAMPLE}.root --doInitialFit --robustFit 1 --expectSignal 1 -t -1 &> ${SAMPLE}_impacts.log
#combineTool.py -M Impacts -m 125 -d ${SAMPLE}.root --robustFit 1 --doFits --parallel $NCPUS --expectSignal 1 -t -1 &>> ${SAMPLE}_impacts.log
#combineTool.py -M Impacts -m 125 -d ${SAMPLE}.root -o impacts_${SAMPLE}.json &>> ${SAMPLE}_impacts.log
combineTool.py -M Impacts -m 125 -d ${DCARD/txt/root} --doInitialFit --robustFit 1 --expectSignal 1 -t -1 &> ${SAMPLE}_impacts.log
combineTool.py -M Impacts -m 125 -d ${DCARD/txt/root} --robustFit 1 --doFits --parallel $NCPUS --expectSignal 1 -t -1 &>> ${SAMPLE}_impacts.log
combineTool.py -M Impacts -m 125 -d ${DCARD/txt/root} -o impacts_${SAMPLE}.json &>> ${SAMPLE}_impacts.log
plotImpacts.py -i impacts_${SAMPLE}.json -o impacts &>> ${SAMPLE}_impacts.log

# Higgs PAG checks: https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsPAGPreapprovalChecks
#combine -M FitDiagnostics $DCARD -t -1 --expectSignal 0
#python HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics.root -g pull.root
#combine -M FitDiagnostics $DCARD -t -1 --expectSignal 1
#python HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics.root -g pull.root

echo ">> Running limits..."
# MAIN
combine -M AsymptoticLimits $DCARD &> ${SAMPLE}.log #--rAbsAcc 5.e-6

echo ">> Making limit plot..."
python get_limits.py -i $DCARD -o . &> ${SAMPLE}_upperlimits.log

#----------------

echo ">> Done processing"
echo ">> Copying files to $EOSTGT"
xrdfs root://cmseos.fnal.gov mkdir -p $EOSTGT

#cp ${_CONDOR_SCRATCH_DIR}/recursiveFileList.py ${_CONDOR_SCRATCH_DIR}/xrdcpRecursive.py .

for f in *.json; do
    xrdmv_with_check $f root://cmseos.fnal.gov/$EOSTGT/
done

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
