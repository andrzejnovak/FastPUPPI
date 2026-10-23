// Flat table for L1 jets carrying NN tag scores (e.g. l1tSC4NGJetProducer:l1tSC4NGJets):
// kinematics plus one "score_<class>" column per tag class.

#include <memory>
#include <sstream>
#include <vector>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "DataFormats/L1TParticleFlow/interface/PFJet.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"

class L1TaggedJetTableProducer : public edm::global::EDProducer<> {
public:
  explicit L1TaggedJetTableProducer(const edm::ParameterSet&);
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  const std::string name_;
  const double minPt_;
  const std::vector<std::string> classes_;
  const edm::EDGetTokenT<l1t::PFJetCollection> jetsToken_;
};

L1TaggedJetTableProducer::L1TaggedJetTableProducer(const edm::ParameterSet& iConfig)
    : name_(iConfig.getParameter<std::string>("name")),
      minPt_(iConfig.getParameter<double>("minPt")),
      classes_(iConfig.getParameter<std::vector<std::string>>("classes")),
      jetsToken_(consumes(iConfig.getParameter<edm::InputTag>("src"))) {
  produces<nanoaod::FlatTable>();
}

void L1TaggedJetTableProducer::produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const {
  const auto& jets = iEvent.get(jetsToken_);
  std::vector<float> pt, eta, phi, mass;
  std::vector<std::vector<float>> scores(classes_.size());
  for (const auto& jet : jets) {
    if (jet.pt() < minPt_)
      continue;
    pt.push_back(jet.pt());
    eta.push_back(jet.eta());
    phi.push_back(jet.phi());
    mass.push_back(jet.mass());
    for (unsigned int i = 0; i < classes_.size(); ++i)
      scores[i].push_back(jet.getTagScore(l1ct::JetTagClass(classes_[i])));
  }
  auto tab = std::make_unique<nanoaod::FlatTable>(pt.size(), name_, false);
  tab->setDoc("L1 jets with NN tag scores");
  tab->addColumn<float>("pt", pt, "pT (tagger-corrected)");
  tab->addColumn<float>("eta", eta, "eta");
  tab->addColumn<float>("phi", phi, "phi");
  tab->addColumn<float>("mass", mass, "mass");
  for (unsigned int i = 0; i < classes_.size(); ++i)
    tab->addColumn<float>("score_" + classes_[i], scores[i], "NN score for class " + classes_[i]);
  iEvent.put(std::move(tab));
}

void L1TaggedJetTableProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<std::string>("name", "L1NGJets");
  desc.add<edm::InputTag>("src", edm::InputTag("l1tSC4NGJetProducer", "l1tSC4NGJets"));
  desc.add<double>("minPt", 0.);
  desc.add<std::vector<std::string>>("classes", {"b", "c", "uds", "g", "tau_p", "tau_n", "mu", "e"});
  descriptions.add("l1TaggedJetTable", desc);
}

DEFINE_FWK_MODULE(L1TaggedJetTableProducer);
