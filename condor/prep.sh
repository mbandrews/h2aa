#!/bin/bash
# https://uscms.org/uscms_at_work/computing/setup/batch_systems.shtml

# voms-proxy-init --valid 192:00 -voms cms
#tar -zcvf h2aa.tgz h2aa/ntupleAnalysis/*py

#tar -zcvf h2aa.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa-inv.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-inv.tgz ../ntupleAnalysis/*py

#tar -zcvf h2aa_nom-nom_bdtgtm0p99.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_bdtgtm0p96.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_relChgIsolt0p03.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_relChgIsolt0p07.tgz ../ntupleAnalysis/*py

#tar -zcvf h2aa_nom-nom_bdtgtm0p99_relChgIsolt0p03.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_bdtgtm0p96_relChgIsolt0p07.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_bdtgtm0p97_relChgIsolt0p06.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_bdtgtm0p96_relChgIsolt0p09.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_bdtgtm0p96_relChgIsolt0p08.tgz ../ntupleAnalysis/*py

#tar -zcvf h2aa.tgz ../ntupleAnalysis/*py
#tar -zcvf h2aa_nom-nom_bdtgtm0p96_relChgIsolt0p07.tgz ../ntupleAnalysis/*py
tar -zcvf h2aa_nom-inv_bdtgtm0p96_relChgIsolt0p07.tgz ../ntupleAnalysis/*py

#tar -zcvf h2aa-pi0.tgz ../ntupleAnalysis/*py

# condor_submit jdls/condor_nom-nom.jdl
# condor_q
# condor_rm -name lpcschedd3.fnal.gov 60000042
