// -*- C++ -*-
//
// Package:    Photons
// Class:      Photons
// 
/**\class Photons AddPhotonUserData.h SandBox/Skims/plugins/AddPhotonUserData.h

Description: [one line class summary]

Implementation:
[Notes on implementation]
*/
//
// Original Author:  Jared Sturdy
//         Created:  Wed Apr 18 16:06:24 CDT 2012
// $Id: AddPhotonUserData.h,v 1.1 2012/09/22 15:52:57 sturdy Exp $
//
//


// system include files
#include <vector>
#include <string>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <map>
#include <set>
#include <math.h>
#include <utility>

//ROOT includes
#include <TH1.h>
#include <TH2.h>

// Framework include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Run.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "DataFormats/PatCandidates/interface/UserData.h"
#include "PhysicsTools/PatAlgos/interface/PATUserDataHelper.h"
#include "CommonTools/Utils/interface/EtComparator.h"

#include "EGamma/EGammaAnalysisTools/interface/PFIsolationEstimator.h"

//Used data formats
#include "DataFormats/PatCandidates/interface/Photon.h"


//
// class declaration
//

class AddPhotonUserData : public edm::EDProducer {
public:
  explicit AddPhotonUserData(const edm::ParameterSet&);
  ~AddPhotonUserData();
  
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  
private:
  virtual void beginJob() ;
  virtual void produce(edm::Event&, const edm::EventSetup&);
  virtual void endJob() ;
  
  // ----------member data ---------------------------
private:
  GreaterByEt<pat::Photon> eTComparator_;

  bool debug_;
  std::string debugString_;
  edm::InputTag photonLabel_ ;
  std::vector<edm::InputTag> floatLabels_ ;
  std::vector<std::string>   floatNames_ ;
  bool useUserData_;

  //only for adding conversion stuff
  bool addConversions_;
  edm::InputTag gsfElecLabel_ ;
  edm::InputTag conversionsLabel_ ;
  edm::InputTag beamspotLabel_ ;

  //only for adding alternate isolations
  PFIsolationEstimator isolator;
  bool useAlternateIsolations_;
  edm::InputTag candidateLabel_ ;
  edm::InputTag vertexLabel_ ;
  double vetoConeSize_;

  pat::PATUserDataHelper<pat::Photon>      userDataHelper_;
};

