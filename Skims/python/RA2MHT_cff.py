
from SandBox.Skims.mhtProducer_cfi import *

# MHT using PF Jets
mhtPF = mht.clone()
mhtPF.JetCollection = cms.InputTag('patJetsAK5PFPt30')

mhtPFchs = mht.clone()
mhtPFchs.JetCollection = cms.InputTag('patJetsPFchsPt30')

from SandBox.Skims.mhtFilter_cfi import *

# filter on PFJet MHT 
mhtPFFilter = mhtFilter.clone()
mhtPFFilter.MHTSource = cms.InputTag("mhtPF")

mhtPFchsFilter = mhtFilter.clone()
mhtPFchsFilter.MHTSource = cms.InputTag("mhtPFchs")
