#!/bin/bash
# https://uscms.org/uscms_at_work/computing/setup/batch_systems.shtml

# voms-proxy-init --valid 192:00 -voms cms

WORKDIR=$(pwd)
COMBINEDIR=~/nobackup/h2aa/CMSSW_10_2_13/src
#cd $COMBINEDIR && tar -zcvf $WORKDIR/combineTool.tgz HiggsAnalysis && cd $WORKDIR
#cd $COMBINEDIR && tar -zcvf $WORKDIR/combineTool.tgz HiggsAnalysis CombineHarvester && cd $WORKDIR
cd $COMBINEDIR && tar -zcvf $WORKDIR/combineTool.tgz get_limits.py HiggsAnalysis CombineHarvester && cd $WORKDIR

# condor_submit jdls/condor_nom-nom.jdl
# condor_q
# condor_rm -name lpcschedd3.fnal.gov 60000042
