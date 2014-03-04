#
#  SUSY-PAT configuration file adapted for RA2 workflow
#
#  PAT configuration for the SUSY group - 53X series
#  More information here:
#  https://twiki.cern.ch/twiki/bin/view/CMS/SusyPatLayer1DefV12
#

# Starting with a skeleton process which gets imported with the following line
from PhysicsTools.PatAlgos.patTemplate_cfg import *

#runningOnMC = True 
runningOnMC = False

#-- Message Logger ------------------------------------------------------------
process.MessageLogger.categories.append('PATSummaryTables')
process.MessageLogger.cerr.PATSummaryTables = cms.untracked.PSet(
    limit = cms.untracked.int32(10),
    reportEvery = cms.untracked.int32(1)
    )
process.MessageLogger.cerr.FwkReport.reportEvery = 1


#-- Input Source --------------------------------------------------------------
process.maxEvents.input = 100

# Due to problem in production of LM samples: same event number appears multiple times
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

############################# START SUSYPAT specifics ####################################
from PhysicsTools.Configuration.SUSY_pattuple_cff import addDefaultSUSYPAT, getSUSY_pattuple_outputCommands

hltMenu = 'HLT'

theJetColls = ['AK5PF']

jetMetCorr = ['L1FastJet', 'L2Relative', 'L3Absolute']
if runningOnMC == False: jetMetCorr.append('L2L3Residual')  

process.GlobalTag.globaltag = "START53_V11::All"
if runningOnMC == False:
    process.GlobalTag.globaltag = "GR_P_V41_AN2::All"  # for Run2012C PromptReco
    #process.GlobalTag.globaltag = "GR_R_53_V14::All"  # for Run2012A/B ReReco

process.source = cms.Source("PoolSource",
   fileNames = cms.untracked.vstring('/store/mc/Summer12_DR53X/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/FED775BD-B8E1-E111-8ED5-003048C69036.root')
)
if runningOnMC == False:
    process.source = cms.Source("PoolSource",
     fileNames = cms.untracked.vstring('/store/data/Run2012C/HTMHT/AOD/PromptReco-v2/000/198/954/BC722417-6ACF-E111-9B10-002481E0D7C0.root')
    )

# Due to problem in production of LM samples: same event number appears multiple times
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

addDefaultSUSYPAT(process,mcInfo=runningOnMC,HLTMenu=hltMenu,jetMetCorrections=jetMetCorr,mcVersion='',theJetNames=theJetColls, doSusyTopProjection=False)

# Remove the PAT cleaning and filtering sequences
process.patDefaultSequence.remove(process.selectedPatCandidates)
process.patDefaultSequence.remove(process.cleanPatCandidates)
process.patDefaultSequence.remove(process.countPatCandidates)

# Disable embedment so that lepton cleaning method works
process.patJetsAK5PF.embedCaloTowers = False
process.patJetsAK5PF.embedPFCandidates = False
process.patJetsPF.embedCaloTowers = False
process.patJetsPF.embedPFCandidates = False

#-- Adjust collections to use PFNoPU jets -------------------------------------
    
# do not use Z-mass window for PU subtraction
# such that JEC works properly
process.pfPileUpPF.checkClosestZVertex = cms.bool(False)

# do not remove muons and electrons from the jet clustering input
process.pfIsolatedElectronsPF.isolationCut = -1.0
process.pfIsolatedMuonsPF.isolationCut = -1.0

# do not remove taus from the jet collection
process.pfTausPF.discriminators = cms.VPSet()
process.pfUnclusteredTausPF = process.pfTausPF.clone(
    cut = cms.string("pt < 0")
    )
process.pfTauSequencePF.replace(process.pfTausPF, process.pfTausPF+ process.pfUnclusteredTausPF)
process.pfNoTauPF.topCollection = "pfUnclusteredTausPF"

# make loose clones of the original electron collection
process.pfRelaxedElectronsPF = process.pfIsolatedElectronsPF.clone()
process.pfRelaxedElectronsPF.isolationCut = 9999.0
process.pfElectronsFromVertexPF.dzCut = 9999.0
process.pfElectronsFromVertexPF.d0Cut = 9999.0
process.pfSelectedElectronsPF.cut = ""
process.patElectronsPF.pfElectronSource  = "pfRelaxedElectronsPF"
process.pfElectronSequencePF.replace(process.pfIsolatedElectronsPF,
                                     process.pfIsolatedElectronsPF +
                                     process.pfRelaxedElectronsPF)

# make loose clones of the original muon collection
process.pfRelaxedMuonsPF = process.pfIsolatedMuonsPF.clone()
process.pfRelaxedMuonsPF.isolationCut = 9999.0
process.pfMuonsFromVertexPF.dzCut = 9999.0
process.pfMuonsFromVertexPF.d0Cut = 9999.0
process.pfSelectedMuonsPF.cut = ""
process.patMuonsPF.pfMuonSource  = "pfRelaxedMuonsPF"
process.pfMuonSequencePF.replace(process.pfIsolatedMuonsPF,
                                 process.pfIsolatedMuonsPF +
                                 process.pfRelaxedMuonsPF)



#------------------------------------------------------------------------------

#SUSY_pattuple_outputCommands = getSUSY_pattuple_outputCommands( process )

# overwrite default output content
from SandBox.Skims.RA2Content_cff import getRA2PATOutput
process.out.outputCommands = getRA2PATOutput(process)
process.out.dropMetaData = cms.untracked.string('DROPPED')
############################## END SUSYPAT specifics ####################################

#-- HLT selection ------------------------------------------------------------
import HLTrigger.HLTfilters.hltHighLevel_cfi as hlt
hltSelection=''
#if options.hltSelection:
if hltSelection:
    process.hltFilter = hlt.hltHighLevel.clone(
        HLTPaths = cms.vstring(hltSelection),
        TriggerResultsTag = cms.InputTag("TriggerResults","",hltMenu),
        throw = False
    )
    process.susyPatDefaultSequence.replace(process.eventCountProducer, process.eventCountProducer * process.hltFilter)


#-- check RA2 recipe here ------------------------------------------------------------
process.prefilterCounter        = cms.EDProducer("EventCountProducer")
process.postStdCleaningCounter  = cms.EDProducer("EventCountProducer")

#-- Output module configuration -----------------------------------------------
process.load('SandBox.Skims.RA2Objects_cff')
process.load('SandBox.Skims.RA2Selection_cff')
process.load('SandBox.Skims.RA2Cleaning_cff')

## please comment this block to remove tagging mode of
##filters and reject events failing any of following filters
process.eeNoiseFilter.taggingMode         = True
process.trackingFailureFilter.taggingMode = True
process.beamHaloFilter.taggingMode        = True
process.ra2NoiseCleaning.remove(process.HBHENoiseFilter)
process.inconsistentMuons.taggingMode     = True
process.greedyMuons.taggingMode           = True
process.ra2EcalTPFilter.taggingMode       = True
process.ra2EcalBEFilter.taggingMode       = True
process.hcalLaserEventFilter.taggingMode  = True
process.eeBadScFilter.taggingMode         = True
process.ecalLaserCorrFilter.taggingMode   = True

process.load("SandBox.Skims.provInfoMuons_cfi")
process.load("SandBox.Skims.provInfoElectrons_cfi")


#HEPTopTagger stuff, added by Chris
process.load("RecoJets.JetProducers.HEPTopTagger_cfi")
from RecoJets.JetProducers.HEPTopTagger_cfi import HEPTopTagJets
from RecoJets.JetProducers.HEPTopTagger_cfi import HEPTopTagInfos

process.HEPTopTag125Jets = HEPTopTagJets.clone(
	rParam = cms.double(1.25)
    )
process.HEPTopTag125Infos = HEPTopTagInfos.clone(
	src = cms.InputTag("HEPTopTag125Jets")
	)


process.HEPTopSelTag125Jets = HEPTopTagJets.clone(
	rParam = cms.double(1.25),
    useSelTag = cms.bool(True)
    )
process.HEPTopSelTag125Infos = HEPTopTagInfos.clone(
	src = cms.InputTag("HEPTopSelTag125Jets")
	)

process.HEPTopTag15Jets = HEPTopTagJets.clone(
    )
process.HEPTopTag15Infos = HEPTopTagInfos.clone(
	src = cms.InputTag("HEPTopTag15Jets")
	)


process.HEPTopSelTag15Jets = HEPTopTagJets.clone(
    useSelTag = cms.bool(True)
    )
process.HEPTopSelTag15Infos = HEPTopTagInfos.clone(
	src = cms.InputTag("HEPTopSelTag15Jets")
	)

process.HEPTopTag2Jets = HEPTopTagJets.clone(
	rParam = cms.double(2.0)
    )
process.HEPTopTag2Infos = HEPTopTagInfos.clone(
	src = cms.InputTag("HEPTopTag2Jets")
	)


process.HEPTopSelTag2Jets = HEPTopTagJets.clone(
	rParam = cms.double(2.0),
    useSelTag = cms.bool(True)
    )
process.HEPTopSelTag2Infos = HEPTopTagInfos.clone(
	src = cms.InputTag("HEPTopSelTag2Jets")
	)


from RecoJets.JetProducers.ca4PFJets_cfi import ca4PFJets

process.ca125PFJetsPFlow = ca4PFJets.clone(
	rParam = cms.double(1.25),
	src = cms.InputTag('particleFlow'),
	doAreaFastjet = cms.bool(True),
	doRhoFastjet = cms.bool(True),
	Rho_EtaMax = cms.double(6.0),
	Ghost_EtaMax = cms.double(7.0)
	)


process.ca15PFJetsPFlow = ca4PFJets.clone(
	rParam = cms.double(1.5),
	src = cms.InputTag('particleFlow'),
	doAreaFastjet = cms.bool(True),
	doRhoFastjet = cms.bool(True),
	Rho_EtaMax = cms.double(6.0),
	Ghost_EtaMax = cms.double(7.0)
	)
process.ca2PFJetsPFlow = ca4PFJets.clone(
	rParam = cms.double(2.0),
	src = cms.InputTag('particleFlow'),
	doAreaFastjet = cms.bool(True),
	doRhoFastjet = cms.bool(True),
	Rho_EtaMax = cms.double(6.0),
	Ghost_EtaMax = cms.double(7.0)
	)

##End added by Chris


# an example sequence to create skimmed susypat-tuples
process.cleanpatseq = cms.Sequence(
                      process.susyPatDefaultSequence  *
                      process.prefilterCounter        *
                      process.ra2StdCleaning          *
                      process.postStdCleaningCounter  *
                      process.ra2Objects              * process.provInfoMuons * process.provInfoElectrons *
#Added by Chris
					  process.HEPTopTag125Jets *
					  process.HEPTopTag125Infos *
                      process.HEPTopSelTag125Jets *
					  process.HEPTopSelTag125Infos *
                      process.HEPTopTag15Jets *
					  process.HEPTopTag15Infos *
                      process.HEPTopSelTag15Jets *
					  process.HEPTopSelTag15Infos *
					  process.HEPTopTag2Jets *
					  process.HEPTopTag2Infos *
                      process.HEPTopSelTag2Jets *
					  process.HEPTopSelTag2Infos *
					  process.ca125PFJetsPFlow *
                      process.ca15PFJetsPFlow *
					  process.ca2PFJetsPFlow *
#End added by Chris      
                      process.ra2PostCleaning         
                      #process.ra2FullPFchsSelectionNoMHT 
                      #process.mhtchsPFFilter
                      )

process.ppf = cms.Path(
              process.cleanpatseq
              )

#-- Output module configuration ---------------------------------------
process.out.fileName = cms.untracked.string('susypat.root')

# output for HEPTopTagger added by Chris
process.out.outputCommands.extend(cms.untracked.vstring('keep *_HEPTopTag*_*_*'))
process.out.outputCommands.extend(cms.untracked.vstring('keep *_HEPTopSelTag*_*_*'))
process.out.outputCommands.extend(cms.untracked.vstring('keep *_ca*PFJetsPFlow*_*_*'))
# End added by Chris

process.out.SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('ppf') )
process.outpath = cms.EndPath( process.out )

###-- Dump config ------------------------------------------------------------
##file = open('SusyPAT_RA2414_cfg.py','w')
##file.write(str(process.dumpPython()))
##file.close()
