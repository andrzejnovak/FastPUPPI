// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/View.h"

#include "DataFormats/L1TParticleFlow/interface/PFTau.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "DataFormats/Math/interface/deltaR.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include "L1Trigger/Phase2L1ParticleFlow/interface/L1TPFUtils.h"
//#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/StringObjectFunction.h"

#include <cstdint>
#include <TTree.h>
#include <TLorentzVector.h>

class TauNTuplizer : public edm::one::EDAnalyzer<edm::one::SharedResources,edm::one::WatchRuns>  {
    public:
        explicit TauNTuplizer(const edm::ParameterSet&);
        ~TauNTuplizer();

    private:
        virtual void beginJob() override;
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
        virtual void beginRun(edm::Run const&, edm::EventSetup const& iSetup) override {}
        virtual void endRun(edm::Run const&, edm::EventSetup const& iSetup) override { } // framework wants this to be implemented
        TLorentzVector visible(const reco::Candidate *d);
        int decay(const reco::Candidate *d);  
        float decayId(float id, int iPdgId);

        edm::EDGetTokenT<std::vector<l1t::PFTau>> L1PFTaus_;
        edm::EDGetTokenT<std::vector<reco::GenParticle>> genparticles_;
        float dr2Max_, minPtRatio_;
        TTree *tree_;
        uint32_t run_, lumi_; uint64_t event_; uint64_t eventcount_; float inputs_[80];

        struct McVars {
  	    float pt1, eta1, phi1, dr1; float id1;
            void makeBranches(TTree *tree) {
                tree->Branch("gendr1", &dr1, "gendr1/F");
                tree->Branch("genpt1", &pt1, "genpt1/F");
                tree->Branch("geneta1", &eta1, "geneta1/F");
                tree->Branch("genphi1", &phi1, "genphi1/F");
		tree->Branch("genid1" , &id1 , "id1/F");
            }
            void clear() {
                pt1 = 0; eta1 = 0; phi1 = 0; dr1 = -999; id1 = 0;
            }
	  void fill(const reco::GenParticle &c) { 
            TLorentzVector lVec; 
	    lVec.SetPtEtaPhiM(pt1,eta1,phi1,0);
	    TLorentzVector lNewVec;
	    lNewVec.SetPtEtaPhiM(c.pt(),c.eta(),c.phi(),0);
	    lVec += lNewVec;
	    id1 = decayId(id1,c.pdgId());
	    pt1  = lVec.Pt(); 
	    eta1 = lVec.Eta(); 
	    phi1 = lVec.Phi();
	  }
	  float decayId(float id, int iPdgId) {
	    if((abs(iPdgId) == 22  || abs(iPdgId) == 130 || abs(iPdgId) == 310 || abs(iPdgId) == 111))  id = 2;
	    if(id == 1 && (abs(iPdgId) == 211 || abs(iPdgId) == 321)) id = 3;
	    if(id == 0 && (abs(iPdgId) == 211 || abs(iPdgId) == 321 )) id = 1;
	    if(id == 0 && abs(iPdgId) == 11)  id = 11;
	    if(id == 0 && abs(iPdgId) == 13)  id = 13; 
	    return id;
	  }
	  void fill(TLorentzVector iVec,float iDR, float id) { 
	    dr1  = iDR;
	    pt1  = iVec.Pt(); 
	    eta1 = iVec.Eta(); 
	    phi1 = iVec.Phi();
	    id1  = id;
	  }
        } mc_;

        class RecoVar {
            public:
                RecoVar(const std::string & name, const std::string & expr) : name_(name), expr_(expr,true) {}
                void makeBranch(TTree *tree) {
                    tree->Branch(name_.c_str(), &val_, (name_+"/F").c_str());
                }
                void fill(const reco::Candidate & c) {
                    val_ = expr_(c);
                }
            private:
                std::string name_;
                StringObjectFunction<reco::Candidate> expr_;
                float val_;
        };
        std::vector<RecoVar> reco_;

 
};

TauNTuplizer::TauNTuplizer(const edm::ParameterSet& iConfig) :
  L1PFTaus_    (consumes<std::vector<l1t::PFTau>>(iConfig.getParameter<edm::InputTag>("src"))),
  genparticles_(consumes<std::vector<reco::GenParticle>>(iConfig.getParameter<edm::InputTag>("genParticles"))),
  dr2Max_(std::pow(iConfig.getParameter<double>("drMax"), 2)),
  minPtRatio_(float(iConfig.getParameter<double>("minRecoPtOverGenPt"))) {
 
    usesResource("TFileService");
    edm::Service<TFileService> fs;
    tree_ = fs->make<TTree>("tree","tree");
    tree_->Branch("run",  &run_,  "run/i");
    tree_->Branch("lumi", &lumi_, "lumi/i");
    tree_->Branch("event", &event_, "event/l");
    tree_->Branch("event2", &eventcount_, "eventcount/l");

    edm::ParameterSet vars = iConfig.getParameter<edm::ParameterSet>("variables");
    auto reconames = vars.getParameterNamesForType<std::string>();
    for (const std::string & name : reconames) {
        reco_.emplace_back(name, vars.getParameter<std::string>(name));
    }
}

TauNTuplizer::~TauNTuplizer() { }
void  TauNTuplizer::beginJob() {
    mc_.makeBranches(tree_);
    for (auto & v : reco_) v.makeBranch(tree_);
    tree_->Branch("m_inputs",&inputs_,"ml_inputs[80]/F");
    eventcount_=0;
}
void TauNTuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
    run_  = iEvent.id().run();
    lumi_ = iEvent.id().luminosityBlock();
    event_ = iEvent.id().event();
    eventcount_++;
    
    edm::Handle<std::vector<reco::GenParticle>> genparticles;
    iEvent.getByToken(genparticles_, genparticles);

    edm::Handle<  l1t::PFTauCollection > l1PFTaus;
    try { 
      iEvent.getByToken( L1PFTaus_, l1PFTaus);
    } catch(...) { 
      return;
    }
    l1t::PFTau dummy;
    std::vector<int> matchedGen;
    std::vector<int> matchedTau;
    std::vector<TLorentzVector> taus;
    std::vector<float> tauid;
    std::vector<const reco::GenParticle*> yigentaus;
    std::vector<TLorentzVector> yitaus;
    bool LeptonicDecay = false;
    for (const reco::GenParticle &gen : *genparticles) {
      if(fabs(gen.pdgId()) != 15) continue;
      if(fabs(gen.status()) > 10) continue;
      yigentaus.push_back(&gen);
    } 
    for(unsigned  i0 = 0; i0 < yigentaus.size(); i0++) {
      int n = yigentaus[i0]->numberOfDaughters();
      TLorentzVector lVec;
      lVec.SetPtEtaPhiM(0,0,0,0);
      float lDecayId = 0;
      for(unsigned i1 = 0; i1 < unsigned(n); i1++) {
	const reco::Candidate * d = yigentaus[i0]->daughter( i1 );
	if(fabs(d->pdgId()) == 12 ||  fabs(d->pdgId()) == 14 || fabs(d->pdgId()) == 16) continue;
	TLorentzVector pVec = visible(d);
	int lId  = decay(d);
	if(fabs(lId) == 11 ||  fabs(lId) == 13) LeptonicDecay = true;
	
	lVec += pVec;
	lDecayId = decayId(lDecayId,lId);
      }
      if(!LeptonicDecay) {taus.push_back(lVec); tauid.push_back(lDecayId);}
    }
    for (unsigned int i = 0, n = l1PFTaus->size(); i < n; ++i) {
        const auto & c = (*l1PFTaus)[i];
	float dr2best = dr2Max_; 
	mc_.clear();
	int pIndex=-1;
	for(unsigned i0 = 0; i0 < taus.size(); i0++) { 
	  bool pXMatch = false;
	  for(unsigned i1 = 0; i1 < matchedTau.size(); i1++) if(int(i0) == matchedTau[i1]) pXMatch = true;
	  if(pXMatch) continue;
	  float dr2 = deltaR2(taus[i0].Eta(), taus[i0].Phi(), c.eta(), c.phi());
    // std::cout << "XXXX:" << c << std::endl;
	  if(dr2 < dr2best) {
	    dr2best = dr2;
	    mc_.fill(taus[i0],std::sqrt(dr2),tauid[i0]);
	    pIndex = i0;
	  }
	}
	for (auto & v : reco_) v.fill(c);
  l1gt::Tau gtTau = c.getHWTauGT();
  std::cout << "pt:" << gtTau.v3.pt  << std::endl;
  std::cout << "iso:" << gtTau.isolation/1024.  << std::endl;
	const float *nnVals = c.NNValues();
	for(int i0 = 0; i0 < 80; i0++) inputs_[i0] = nnVals[i0]; 
	matchedTau.push_back(pIndex);
	tree_->Fill();
	mc_.clear();
    }
    //if(l1PFTaus->size() == 0) {
    for(int i0 = 0; i0 < int(taus.size()); i0++) { 
      bool pMatch = false;
      for(unsigned i1 = 0; i1 < matchedTau.size(); i1++) if(int(i0) == matchedTau[i1]) pMatch = true;
      if(pMatch) continue;
      float dr2 = 99;
      mc_.fill(taus[i0],-1.*std::sqrt(dr2),tauid[i0]);
      //pIndex = i0;
      //pMatch++;
      //}
      for (auto & v : reco_) v.fill(dummy);
      tree_->Fill();
      mc_.clear();
    }
}
TLorentzVector TauNTuplizer::visible(const reco::Candidate *d) { 
      TLorentzVector lVec;
      lVec.SetPtEtaPhiM(0,0,0,0);
      if (d->numberOfDaughters() == 0) { 
        //std::cout << " Base Daughter --> " << d->pt() << " --" << d->pdgId() << " -- " << d->eta() << " -- " << d->status() << std::endl;
        lVec.SetPtEtaPhiM(d->pt(),d->eta(),d->phi(),0);
              return lVec;
      } 
      for(unsigned  i0 = 0; i0 < d->numberOfDaughters(); i0++) { 
	const reco::Candidate * pD = d->daughter(i0);
	if(fabs(d->pdgId()) == 12 ||  fabs(d->pdgId()) == 14 || fabs(d->pdgId()) == 16) continue;
	TLorentzVector pVec = visible(pD);
	lVec += pVec; 
      }
      return lVec;
}
int TauNTuplizer::decay(const reco::Candidate *d) { 
  if(d->numberOfDaughters() == 0) { 
	int lId = d->pdgId();
        return lId;
  } 
  for(unsigned i0 = 0; i0 < d->numberOfDaughters(); i0++) { 
    const reco::Candidate * pD = d->daughter(i0);
    if(fabs(d->pdgId()) == 12 ||  fabs(d->pdgId()) == 14 || fabs(d->pdgId()) == 16) continue;
    int lId = pD->pdgId();
    return lId;
  }
  return -1;
}
float TauNTuplizer::decayId(float id, int iPdgId) { 
  if((abs(iPdgId) == 22  || abs(iPdgId) == 130 || abs(iPdgId) == 310 || abs(iPdgId) == 111))  id = 2;
  if(id == 1 && (abs(iPdgId) == 211 || abs(iPdgId) == 321)) id = 3;
  if(id == 0 && (abs(iPdgId) == 211 || abs(iPdgId) == 321 )) id = 1;
  if(id == 0 && abs(iPdgId) == 11)  id = 11;
  if(id == 0 && abs(iPdgId) == 13)  id = 13;
  return id;
}

//define this as a plug-in
#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(TauNTuplizer);
