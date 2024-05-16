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

class TauNTuplizerDouble : public edm::one::EDAnalyzer<edm::one::SharedResources,edm::one::WatchRuns>  {
    public:
        explicit TauNTuplizerDouble(const edm::ParameterSet&);
        ~TauNTuplizerDouble();

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
        uint32_t run_, lumi_; uint64_t event_; uint64_t eventcount_; float inputs1_[80]; float inputs2_[80];

        struct McVars {
            float pt1, eta1, phi1, dr1;
  	    float pt2, eta2, phi2, dr2;
	    float  id1; float id2;
            void makeBranches(TTree *tree) {
                tree->Branch("gendr1", &dr1, "gendr1/F");
                tree->Branch("genpt1", &pt1, "genpt1/F");
                tree->Branch("geneta1", &eta1, "geneta1/F");
                tree->Branch("genphi1", &phi1, "genphi1/F");
		tree->Branch("genid1" , &id1 , "id1/F");

                tree->Branch("gendr2", &dr2, "gendr2/F");
                tree->Branch("genpt2", &pt2, "genpt2/F");
                tree->Branch("geneta2", &eta2, "geneta2/F");
                tree->Branch("genphi2", &phi2, "genphi2/F");
		tree->Branch("genid2" , &id2 , "id2/F");
            }
            void clear() {
                pt1 = 0; eta1 = 0; phi1 = 0; dr1 = -999; id1 = 0;
                pt2 = 0; eta2 = 0; phi2 = 0; dr2 = -999; id2 = 0; 
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
	    //if(iVec.Pt() > pt1) {
	    if(fabs(iDR) < fabs(dr1)) {
	      dr2  = dr1;
	      pt2  = pt1;
	      eta2 = eta1;
	      phi2 = phi1;
	      id2  = id;

	      dr1  = iDR;
	      pt1  = iVec.Pt(); 
	      eta1 = iVec.Eta(); 
	      phi1 = iVec.Phi();
	      id1  = id;
	    } else {//if(iVec.Pt() > pt2) { 
	      dr2  = iDR;
	      pt2  = iVec.Pt(); 
	      eta2 = iVec.Eta(); 
	      phi2 = iVec.Phi();
	      id2  = id;
	    }
	  }
	  void fill1(TLorentzVector iVec,float iDR, float id) { 
	    //if(iVec.Pt() > pt1) {
	    if(fabs(iDR) < fabs(dr1)) {
	      dr1  = iDR;
	      pt1  = iVec.Pt(); 
	      eta1 = iVec.Eta(); 
	      phi1 = iVec.Phi();
	      id1  = id;
	    } 
	  }
	  void fill2(TLorentzVector iVec,float iDR, float id) { 
	    //if(iVec.Pt() > pt1) {
	    if(fabs(iDR) < fabs(dr2)) {
	      dr2  = iDR;
	      pt2  = iVec.Pt(); 
	      eta2 = iVec.Eta(); 
	      phi2 = iVec.Phi();
	      id2  = id;
	    } 
	  }
        } mc_;

        class RecoVar {
            public:
                RecoVar(const std::string & name, const std::string & expr) : name_(name), expr_(expr,true) {}
                void makeBranch(TTree *tree) {
		  tree->Branch((name_+"1").c_str(), &val1_, (name_+"1/F").c_str());
		  tree->Branch((name_+"2").c_str(), &val2_, (name_+"2/F").c_str());
		  pt1_=0;
		  pt2_=0;
		  val1_=-1.;
		  val2_=-1.;
                }
   	        void clear() {
		  val1_ = 0; 
		  val2_ = 0; 
		  pt1_  = 0; 
		  pt2_  = 0; 
		}
                void fill(const reco::Candidate & c) {
		  if(c.pt() > pt1_) {
		    val2_ = val1_;
		    pt2_  = pt1_;
		    pt1_  = c.pt();
		    val1_ = expr_(c);
		  } else if(c.pt() > pt2_) { 
		    val2_ = expr_(c);
		    pt2_  = c.pt();
		  }
                }
            private:
                std::string name_;
                StringObjectFunction<reco::Candidate> expr_;
                float val1_;
		float val2_;
                float pt1_;
                float pt2_;
        };
        std::vector<RecoVar> reco_;

 
};

TauNTuplizerDouble::TauNTuplizerDouble(const edm::ParameterSet& iConfig) :
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

TauNTuplizerDouble::~TauNTuplizerDouble() { }
void  TauNTuplizerDouble::beginJob() {
    mc_.makeBranches(tree_);
    for (auto & v : reco_) v.makeBranch(tree_);
    tree_->Branch("m1_inputs",&inputs1_,"ml1_inputs[80]/F");
    tree_->Branch("m2_inputs",&inputs2_,"ml2_inputs[80]/F");
    eventcount_=0;
}
void TauNTuplizerDouble::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
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
	for (unsigned int j = 0; j < i; ++j) {
	  mc_.clear();
	  unsigned int pFillId = 1000000;
	  float pDRMin = 99999;
	  for(unsigned i0 = 0; i0 < taus.size(); i0++) { 
	    float dr2 = deltaR2(taus[i0].Eta(), taus[i0].Phi(), c.eta(), c.phi());
	    mc_.fill1(taus[i0],std::sqrt(dr2),tauid[i0]);
	    if(dr2 < pDRMin) {pFillId = i0; pDRMin = dr2;}
 	  }
	  for (auto & v : reco_) v.fill(c);
	  const float *nnVals = c.NNValues();
	  for(int i0 = 0; i0 < 80; i0++) inputs1_[i0] = nnVals[i0]; 

	  const auto & c1 = (*l1PFTaus)[j];
	  //if(fabs(c1.fullIso()-c.fullIso()) > 1.0) continue;
	  if(deltaR2(c.eta(), c.phi(), c1.eta(), c1.phi()) < 0.4*0.4) continue;
	  //unsigned pIndex = -1;
	  for(unsigned i0 = 0; i0 < taus.size(); i0++) { 
	    if(i0 == pFillId) continue;
	    float dr2 = deltaR2(taus[i0].Eta(), taus[i0].Phi(), c1.eta(), c1.phi());
	    mc_.fill2(taus[i0],std::sqrt(dr2),tauid[i0]);
	    //pIndex = i0;
	  }
	  //if(pIndex != -1) matchedTau.push_back(pIndex);
	  for (auto & v : reco_) v.fill(c);
	  for (auto & v : reco_) v.fill(c1);
	  const float *nnVals1  = c.NNValues();
	  const float *nnVals2 = c1.NNValues();
	  for(int i0 = 0; i0 < 80; i0++) {
	    if(c.pt() > c1.pt()) { 
	      inputs1_[i0] = nnVals1[i0]; 
	      inputs2_[i0] = nnVals2[i0]; 
	    } else { 
	      inputs2_[i0] = nnVals1[i0]; 
	      inputs1_[i0] = nnVals2[i0]; 
	    }
	  }
	  tree_->Fill();
	  for (auto & v : reco_) v.clear();
	}
    }
    mc_.clear();
	
    if(l1PFTaus->size() == 1) {
      for(int i0 = 0; i0 < int(taus.size()); i0++) { 
	//bool pMatch = false;
	//for(unsigned i1 = 0; i1 < matchedTau.size(); i1++) if(int(i0) == matchedTau[i1]) pMatch = true;
	//if(pMatch) continue;
	float dr2 = 99;
	mc_.fill(taus[i0],-1.*std::sqrt(dr2),tauid[i0]);
	//pIndex = i0;
	//pMatch++;
	//}
	for (auto & v : reco_) v.fill(dummy);
      }
      tree_->Fill();
      for (auto & v : reco_) v.clear();
      mc_.clear();
    }
    if(l1PFTaus->size() == 0) {
      for(int i0 = 0; i0 < int(taus.size()); i0++) { 
	//bool pMatch = false;
	//for(unsigned i1 = 0; i1 < matchedTau.size(); i1++) if(int(i0) == matchedTau[i1]) pMatch = true;
	//if(pMatch) continue;
	float dr2 = 99;
	mc_.fill(taus[i0],-1.*std::sqrt(dr2),tauid[i0]);
	//pIndex = i0;
	//pMatch++;
	//}
	for (auto & v : reco_) v.fill(dummy);
      }
      tree_->Fill();
      for (auto & v : reco_) v.clear();
      mc_.clear();
    }
}
TLorentzVector TauNTuplizerDouble::visible(const reco::Candidate *d) { 
      TLorentzVector lVec;
      lVec.SetPtEtaPhiM(0,0,0,0);
      if(d->numberOfDaughters() == 0) { 
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
int TauNTuplizerDouble::decay(const reco::Candidate *d) { 
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
float TauNTuplizerDouble::decayId(float id, int iPdgId) { 
  if((abs(iPdgId) == 22  || abs(iPdgId) == 130 || abs(iPdgId) == 310 || abs(iPdgId) == 111))  id = 2;
  if(id == 1 && (abs(iPdgId) == 211 || abs(iPdgId) == 321)) id = 3;
  if(id == 0 && (abs(iPdgId) == 211 || abs(iPdgId) == 321 )) id = 1;
  if(id == 0 && abs(iPdgId) == 11)  id = 11;
  if(id == 0 && abs(iPdgId) == 13)  id = 13;
  return id;
}
//define this as a plug-in
#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(TauNTuplizerDouble);
