// Flat tables of L1 tracks (TTTracks from the Outer Tracker track finder) and of the L1 vertices,
// for studies that extend L1 tracks into the pixel layers (track-seeded pixel hit association).
//
// Tables (same module, distinguished by instance label):
//   <name>       : one row per L1 track: pT, eta, phi, z0, d0 (extended tracks), charge, fit quality, stubs
//   <name>Vtx    : one row per L1 vertex (optional): z0, pT sum, number of tracks

#include <memory>
#include <vector>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "DataFormats/L1TrackTrigger/interface/TTTypes.h"
#include "DataFormats/L1Trigger/interface/Vertex.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"

class L1TrackTableProducer : public edm::global::EDProducer<> {
public:
  explicit L1TrackTableProducer(const edm::ParameterSet&);
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  const std::string name_;
  const double minPt_;
  const int precision_;
  const edm::EDGetTokenT<std::vector<TTTrack<Ref_Phase2TrackerDigi_>>> tracksToken_;
  const bool storeVertices_;
  edm::EDGetTokenT<l1t::VertexCollection> verticesToken_;
};

L1TrackTableProducer::L1TrackTableProducer(const edm::ParameterSet& iConfig)
    : name_(iConfig.getParameter<std::string>("name")),
      minPt_(iConfig.getParameter<double>("minPt")),
      precision_(iConfig.getParameter<int>("precision")),
      tracksToken_(consumes(iConfig.getParameter<edm::InputTag>("tracks"))),
      storeVertices_(iConfig.getParameter<bool>("storeVertices")) {
  produces<nanoaod::FlatTable>("tracks");
  if (storeVertices_) {
    verticesToken_ = consumes(iConfig.getParameter<edm::InputTag>("vertices"));
    produces<nanoaod::FlatTable>("vertices");
  }
}

void L1TrackTableProducer::produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup&) const {
  const auto& tracks = iEvent.get(tracksToken_);
  std::vector<float> pt, eta, phi, z0, d0, rInv, chi2XY, chi2Z, bendChi2;
  std::vector<int> charge, nStubs, nPar;
  for (const auto& trk : tracks) {
    const auto mom = trk.momentum();
    if (mom.perp() < minPt_)
      continue;
    pt.push_back(mom.perp());
    eta.push_back(mom.eta());
    phi.push_back(mom.phi());
    z0.push_back(trk.z0());
    d0.push_back(trk.nFitPars() >= 5 ? trk.d0() : 0.f);
    rInv.push_back(trk.rInv());
    charge.push_back(trk.rInv() > 0 ? 1 : -1);
    chi2XY.push_back(trk.chi2XY());
    chi2Z.push_back(trk.chi2Z());
    bendChi2.push_back(trk.chi2BendRed());
    nStubs.push_back(trk.getStubRefs().size());
    nPar.push_back(trk.nFitPars());
  }
  auto tab = std::make_unique<nanoaod::FlatTable>(pt.size(), name_, false);
  tab->setDoc("L1 tracks (Outer Tracker track finder)");
  tab->addColumn<float>("pt", pt, "pT [GeV]", precision_);
  tab->addColumn<float>("eta", eta, "eta", precision_);
  tab->addColumn<float>("phi", phi, "phi at the point of closest approach", precision_);
  tab->addColumn<float>("z0", z0, "z0 [cm]", precision_);
  tab->addColumn<float>("d0", d0, "d0 [cm] (5-parameter fit only, else 0)", precision_);
  tab->addColumn<float>("rInv", rInv, "curvature 1/R [1/cm]", precision_);
  tab->addColumn<int>("charge", charge, "charge from the curvature sign");
  tab->addColumn<float>("chi2XY", chi2XY, "r-phi fit chi2", precision_);
  tab->addColumn<float>("chi2Z", chi2Z, "r-z fit chi2", precision_);
  tab->addColumn<float>("bendChi2", bendChi2, "reduced bend chi2", precision_);
  tab->addColumn<int>("nStubs", nStubs, "number of stubs");
  tab->addColumn<int>("nPar", nPar, "number of fit parameters (4 or 5)");
  iEvent.put(std::move(tab), "tracks");

  if (storeVertices_) {
    const auto& vertices = iEvent.get(verticesToken_);
    std::vector<float> vz, vpt;
    std::vector<int> vntrk;
    for (const auto& v : vertices) {
      vz.push_back(v.z0());
      vpt.push_back(v.pt());
      vntrk.push_back(v.tracks().size());
    }
    auto vtab = std::make_unique<nanoaod::FlatTable>(vz.size(), name_ + "Vtx", false);
    vtab->setDoc("L1 vertices");
    vtab->addColumn<float>("z0", vz, "z0 [cm]", precision_);
    vtab->addColumn<float>("pt", vpt, "sum of track pT [GeV]", precision_);
    vtab->addColumn<int>("nTracks", vntrk, "number of tracks");
    iEvent.put(std::move(vtab), "vertices");
  }
}

void L1TrackTableProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<std::string>("name", "L1Tracks");
  desc.add<edm::InputTag>("tracks", edm::InputTag("l1tTTTracksFromTrackletEmulation", "Level1TTTracks"));
  desc.add<double>("minPt", 0.)->setComment("drop tracks below this pT");
  desc.add<int>("precision", -1)->setComment("mantissa bits for float columns (-1 = full float)");
  desc.add<bool>("storeVertices", true);
  desc.add<edm::InputTag>("vertices", edm::InputTag("l1tVertexFinder", "L1Vertices"));
  descriptions.add("l1TrackTable", desc);
}

DEFINE_FWK_MODULE(L1TrackTableProducer);
