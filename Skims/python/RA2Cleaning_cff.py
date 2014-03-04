# $Id: RA2Cleaning_cff.py,v 1.15 2012/10/12 14:43:59 seema Exp $

# Standard Event cleaning 
from SandBox.Skims.noscraping_cfi      import *
from SandBox.Skims.vertex_cfi          import *
from SandBox.Skims.HBHENoiseFilter_cff import *

ra2StdCleaning = cms.Sequence(
                 noscraping    
               * oneGoodVertex
)

# RA2 detector noise cleaning
from RecoMET.METFilters.eeNoiseFilter_cfi         import *
from SandBox.Skims.beamHaloFilter_cfi             import *
from SandBox.Skims.HBHENoiseFilter_cff            import *
from RecoMET.METFilters.hcalLaserEventFilter_cfi  import *
from RecoMET.METFilters.eeBadScFilter_cfi         import *
from RecoMET.METFilters.trackingFailureFilter_cfi import *
hcalLaserEventFilter.vetoByRunEventNumber=cms.untracked.bool(False)
hcalLaserEventFilter.vetoByHBHEOccupancy=cms.untracked.bool(True)
from RecoMET.METFilters.ecalLaserCorrFilter_cfi   import *

ra2NoiseCleaning = cms.Sequence(
                   eeNoiseFilter
                 * trackingFailureFilter 
                 * beamHaloFilter
                 * HBHENoiseFilter     # rejects the event
                 * HBHENoiseFilterRA2  # produced a boolean & stores it
                 * hcalLaserEventFilter 
                 * eeBadScFilter
                 * ecalLaserCorrFilter
)    

## RA2 post reconstruction cleaning
# badly reconstructed muons
from SandBox.Skims.muonPFCandidateProducer_cfi                import *

from RecoMET.METFilters.greedyMuonPFCandidateFilter_cfi       import *
greedyMuons              = greedyMuonPFCandidateFilter.clone()
greedyMuons.PFCandidates = cms.InputTag('muonPFCandidateProducer')

from RecoMET.METFilters.inconsistentMuonPFCandidateFilter_cfi import *
inconsistentMuons              = inconsistentMuonPFCandidateFilter.clone()
inconsistentMuons.PFCandidates = cms.InputTag('muonPFCandidateProducer')

selectGoodPFEventsSequence = cms.Sequence(
                             muonPFCandidateProducer 
                           * inconsistentMuons       
                           * greedyMuons
)

# ECAL dead cell filters
from RecoMET.METFilters.EcalDeadCellTriggerPrimitiveFilter_cfi import *
EcalDeadCellTriggerPrimitiveFilter.tpDigiCollection = cms.InputTag("ecalTPSkimNA")
ra2EcalTPFilter     = EcalDeadCellTriggerPrimitiveFilter.clone()

from RecoMET.METFilters.EcalDeadCellBoundaryEnergyFilter_cfi   import *
ra2EcalBEFilter           = EcalDeadCellBoundaryEnergyFilter.clone()
ra2EcalBEFilter.recHitsEB = "reducedEcalRecHitsEB"
ra2EcalBEFilter.recHitsEE = "reducedEcalRecHitsEE"

ra2EcalPostRecoCleaning = cms.Sequence(  
                          ra2EcalTPFilter
                        * ra2EcalBEFilter
)

# after all MET POG recommeded filters, also check JetID
from  SandBox.Skims.RA2JetIDFailureFilter_cfi import *

ra2PostCleaning = cms.Sequence(
                  ra2NoiseCleaning
                * selectGoodPFEventsSequence 
                * ra2EcalPostRecoCleaning  
                #* ra2PBNR  #(to be jet-by-jet)
)
