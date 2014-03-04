
#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
//#include "DataFormats/Common/interface/View.h"
//#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectronFwd.h"
#include "DataFormats/EgammaCandidates/interface/Conversion.h"
#include "DataFormats/GsfTrackReco/interface/GsfTrack.h"
#include "DataFormats/RecoCandidate/interface/IsoDeposit.h"
#include "EGamma/EGammaAnalysisTools/interface/EGammaCutBasedEleId.h"


class GoodElectronSelector : public edm::EDFilter {

  public:

    explicit GoodElectronSelector(const edm::ParameterSet & iConfig);
    ~GoodElectronSelector();

  private:

    virtual bool filter(edm::Event & iEvent, const edm::EventSetup & iSetup);

    edm::InputTag electronSrc_;
    edm::InputTag conversionsSrc_;
    edm::InputTag vtxSrc_;
    edm::InputTag beamSpotSrc_;
    edm::InputTag rhoIsoSrc_;
    std::vector<edm::InputTag>  isoValsSrc_;
    bool   doEleVeto_;
    double minElePt_, maxEleEta_;
    bool debug_;

};


typedef std::vector< edm::Handle< edm::ValueMap<reco::IsoDeposit> > >   IsoDepositMaps;
typedef std::vector< edm::Handle< edm::ValueMap<double> > >             IsoDepositVals;


GoodElectronSelector::GoodElectronSelector(const edm::ParameterSet & iConfig) {
  electronSrc_   = iConfig.getParameter<edm::InputTag>("ElectronSource");
  conversionsSrc_= iConfig.getParameter<edm::InputTag>("ConversionsSource");
  vtxSrc_        = iConfig.getParameter<edm::InputTag>("VertexSource");
  beamSpotSrc_   = iConfig.getParameter<edm::InputTag>("BeamSpotSource");
  rhoIsoSrc_     = iConfig.getParameter<edm::InputTag>("RhoIsoSource");
  isoValsSrc_    = iConfig.getParameter<std::vector<edm::InputTag> >("IsoValInputTags");
  minElePt_      = iConfig.getParameter<double>("MinElePt");
  maxEleEta_     = iConfig.getParameter<double>("MaxEleEta");
  doEleVeto_     = iConfig.getParameter<bool>("DoElectronVeto");
  debug_         = iConfig.getParameter<bool>("Debug");

  produces<std::vector<reco::GsfElectron> >("");
}


GoodElectronSelector::~GoodElectronSelector() {
}


bool GoodElectronSelector::filter(edm::Event& iEvent, const edm::EventSetup& iSetup) {

  // electrons
  edm::Handle< std::vector<reco::GsfElectron> > electrons;   
  iEvent.getByLabel(electronSrc_, electrons);

  // conversions
  edm::Handle< std::vector<reco::Conversion> > conversions;
  iEvent.getByLabel(conversionsSrc_, conversions);

  // iso deposits
  IsoDepositVals isoVals(isoValsSrc_.size());
  for (size_t j = 0; j < isoValsSrc_.size(); ++j) {
    iEvent.getByLabel(isoValsSrc_[j], isoVals[j]);
  }
  
  // beam spot
  edm::Handle<reco::BeamSpot> beamspot;
  iEvent.getByLabel(beamSpotSrc_, beamspot);
  const reco::BeamSpot &beamSpot = *(beamspot.product());
  
  // vertices
  edm::Handle< std::vector<reco::Vertex> > vertices;
  iEvent.getByLabel(vtxSrc_, vertices);

  // rho for isolation                                                                                                
  edm::Handle<double> rhoIsoH;
  iEvent.getByLabel(rhoIsoSrc_, rhoIsoH);
  double rhoIso = *(rhoIsoH.product());
  

  // check which ones to keep
  std::auto_ptr<std::vector<reco::GsfElectron> > prod(new std::vector<reco::GsfElectron>());

  // loop on electrons
  for(unsigned int i = 0; i < electrons->size(); ++i) {

    // get reference to electron
    reco::GsfElectronRef ele(electrons, i);

    if (ele->pt() < minElePt_) continue;

    // get particle flow isolation
    double iso_ch = (*(isoVals)[0])[ele];
    double iso_em = (*(isoVals)[1])[ele];
    double iso_nh = (*(isoVals)[2])[ele];
    
    // working points
    bool veto       = EgammaCutBasedEleId::PassWP(EgammaCutBasedEleId::VETO, ele, conversions, beamSpot, vertices, iso_ch, iso_em, iso_nh, rhoIso);

    if(debug_) {
      reco::VertexRef vtx(vertices, 0);
      std::cout << "iEle " << i << ": "
		<< " (pt,eta,phi) "<<ele->pt()<<", "<<ele->eta()<<", "<<ele->phi() << " "
		<< ", isEB " << ele->isEB() << ", isEE " << ele->isEE() << "\n"
		<< ", dEtaIn " << ele->deltaEtaSuperClusterTrackAtVtx()
		<< ", dPhiIn " << ele->deltaPhiSuperClusterTrackAtVtx()
		<< ", sigmaIEtaIEta "<< ele->sigmaIetaIeta()
		<< ", hoe " << ele->hadronicOverEm()
		<< ", d0vtx " << ele->gsfTrack()->dxy(vtx->position())
		<< ", dzvtx " << ele->gsfTrack()->dz(vtx->position())
		<< ", passSelection " << veto
		<< std::endl;
    }

    // electron is ID'd and isolated! - only accept if vertex present
    if (vertices->size()>0 && veto) prod->push_back(reco::GsfElectron(*ele));
  }


  // determine result before losing ownership of the pointer
  bool result = (doEleVeto_ ? (prod->size() == 0) : true);
  // store in the event
  iEvent.put(prod);
  return result;
}


#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(GoodElectronSelector);
