#!/bin/bash
# https://uscms.org/uscms_at_work/computing/setup/batch_systems.shtml

# voms-proxy-init --valid 192:00 -voms cms
#tar -zcvf h2aa.tgz h2aa/ntupleAnalysis/*py
#tar -zcvf h2aa.tgz ntupleAnalysis/*py
tar -zcvf h2aa.tgz ../ntupleAnalysis/*py

# condor_submit jdls/condor_nom-nom.jdl
# condor_q
# condor_rm -name lpcschedd3.fnal.gov 60000042
