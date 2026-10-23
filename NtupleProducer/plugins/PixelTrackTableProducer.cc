// Flat tables for the HLT pixel tracks, their hits and the pixel vertices.
//
// The SiPixelRecHits persisted with hltPhase2PixelTracks have zeroed local positions (only the
// DetId survives), so hit positions are recomputed from the referenced SiPixelCluster centroid
// and the module topology (no CPE / Lorentz-drift correction, O(10 um) bias). This needs the
// siPixelClusters collection, i.e. it has to run on GEN-SIM-DIGI-RAW (the input-file step).
//
// Tables (same module, distinguished by instance label):
//   <name>Tracks   : one row per track, hits of track i are rows [hitIdx, hitIdx + nHits) of <name>Hits
//   <name>Hits     : one row per hit, with trkIdx pointing back to the track
//   <name>Vertices : one row per pixel vertex; tracks carry vtxIdx (-1 if not used in any vertex)
//
// Based on the pixel-track ntupling explored by Marc Huwiler (mhuwiler/cmssw:devPixelsForL1).

#include <memory>
#include <vector>

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/SiPixelDetId/interface/PixelSubdetector.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"
#include "DataFormats/TrackerRecHit2D/interface/SiPixelRecHit.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "Geometry/CommonDetUnit/interface/PixelGeomDetUnit.h"
#include "Geometry/CommonTopologies/interface/PixelTopology.h"
#include "Geometry/Records/interface/TrackerDigiGeometryRecord.h"
#include "Geometry/Records/interface/TrackerTopologyRcd.h"
#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"

class PixelTrackTableProducer : public edm::global::EDProducer<> {
public:
  explicit PixelTrackTableProducer(const edm::ParameterSet&);
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  const std::string name_;
  const double minPt_;
  const int precision_;
  const edm::EDGetTokenT<std::vector<reco::Track>> tracksToken_;
  const edm::EDGetTokenT<std::vector<reco::Vertex>> verticesToken_;
  const edm::EDGetTokenT<reco::BeamSpot> beamSpotToken_;
  const edm::ESGetToken<TrackerGeometry, TrackerDigiGeometryRecord> geomToken_;
  const edm::ESGetToken<TrackerTopology, TrackerTopologyRcd> topoToken_;
};

PixelTrackTableProducer::PixelTrackTableProducer(const edm::ParameterSet& iConfig)
    : name_(iConfig.getParameter<std::string>("name")),
      minPt_(iConfig.getParameter<double>("minPt")),
      precision_(iConfig.getParameter<int>("precision")),
      tracksToken_(consumes(iConfig.getParameter<edm::InputTag>("tracks"))),
      verticesToken_(consumes(iConfig.getParameter<edm::InputTag>("vertices"))),
      beamSpotToken_(consumes(iConfig.getParameter<edm::InputTag>("beamSpot"))),
      geomToken_(esConsumes()),
      topoToken_(esConsumes()) {
  produces<nanoaod::FlatTable>("tracks");
  produces<nanoaod::FlatTable>("hits");
  produces<nanoaod::FlatTable>("vertices");
}

void PixelTrackTableProducer::produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup& iSetup) const {
  const auto& tracks = iEvent.get(tracksToken_);
  const auto& vertices = iEvent.get(verticesToken_);
  const auto& beamSpot = iEvent.get(beamSpotToken_);
  const auto& geom = iSetup.getData(geomToken_);
  const auto& topo = iSetup.getData(topoToken_);

  // track index -> vertex index (tracks are referenced by the pixel vertices)
  std::vector<int> trkToVtx(tracks.size(), -1);
  std::vector<float> vx, vy, vz, vchi2, vndof, vsumPt2;
  std::vector<int> vntrk;
  for (unsigned int iv = 0, nv = vertices.size(); iv < nv; ++iv) {
    const auto& v = vertices[iv];
    float sumPt2 = 0;
    for (auto it = v.tracks_begin(); it != v.tracks_end(); ++it) {
      if (it->key() < trkToVtx.size())
        trkToVtx[it->key()] = iv;
      sumPt2 += (*it)->pt() * (*it)->pt();
    }
    vx.push_back(v.x());
    vy.push_back(v.y());
    vz.push_back(v.z());
    vchi2.push_back(v.chi2());
    vndof.push_back(v.ndof());
    vntrk.push_back(v.tracksSize());
    vsumPt2.push_back(sumPt2);
  }

  std::vector<float> pt, eta, phi, dxy, dz, dxyBS, dzBS, dxyErr, dzErr, chi2, ndof;
  std::vector<int> charge, nHits, hitIdx, vtxIdx;
  std::vector<float> hx, hy, hz;
  std::vector<int> hTrk, hDetId, hSubdet, hLayer, hSizeX, hSizeY, hCharge;

  const math::XYZPoint bs(beamSpot.x0(), beamSpot.y0(), beamSpot.z0());
  for (unsigned int it = 0, nt = tracks.size(); it < nt; ++it) {
    const auto& trk = tracks[it];
    if (trk.pt() < minPt_)
      continue;
    const int iTrk = pt.size();
    pt.push_back(trk.pt());
    eta.push_back(trk.eta());
    phi.push_back(trk.phi());
    charge.push_back(trk.charge());
    dxy.push_back(trk.dxy());
    dz.push_back(trk.dz());
    dxyBS.push_back(trk.dxy(bs));
    dzBS.push_back(trk.dz(bs));
    dxyErr.push_back(trk.dxyError());
    dzErr.push_back(trk.dzError());
    chi2.push_back(trk.chi2());
    ndof.push_back(trk.ndof());
    vtxIdx.push_back(trkToVtx[it]);
    hitIdx.push_back(hx.size());

    int nh = 0;
    for (auto ih = trk.recHitsBegin(); ih != trk.recHitsEnd(); ++ih) {
      const auto* hit = dynamic_cast<const SiPixelRecHit*>(*ih);
      if (hit == nullptr || !hit->isValid())
        continue;
      const DetId id = hit->geographicalId();
      const auto* det = dynamic_cast<const PixelGeomDetUnit*>(geom.idToDetUnit(id));
      GlobalPoint gp(-999.f, -999.f, -999.f);
      int sizeX = -1, sizeY = -1, adc = -1;
      if (det != nullptr) {
        const auto& clRef = hit->cluster();
        if (clRef.isNonnull() && clRef.isAvailable()) {
          const auto& cl = *clRef;
          gp = det->surface().toGlobal(det->specificTopology().localPosition(MeasurementPoint(cl.x(), cl.y())));
          sizeX = cl.sizeX();
          sizeY = cl.sizeY();
          adc = cl.charge();
        } else {
          gp = det->surface().toGlobal(hit->localPosition());
        }
      }
      hx.push_back(gp.x());
      hy.push_back(gp.y());
      hz.push_back(gp.z());
      hTrk.push_back(iTrk);
      hDetId.push_back(id.rawId());
      hSubdet.push_back(id.subdetId());
      hLayer.push_back(topo.layer(id));
      hSizeX.push_back(sizeX);
      hSizeY.push_back(sizeY);
      hCharge.push_back(adc);
      ++nh;
    }
    nHits.push_back(nh);
  }

  auto trkTab = std::make_unique<nanoaod::FlatTable>(pt.size(), name_ + "Tracks", false);
  trkTab->setDoc("HLT pixel tracks");
  trkTab->addColumn<float>("pt", pt, "pT", precision_);
  trkTab->addColumn<float>("eta", eta, "eta", precision_);
  trkTab->addColumn<float>("phi", phi, "phi", precision_);
  trkTab->addColumn<int>("charge", charge, "charge");
  trkTab->addColumn<float>("dxy", dxy, "dxy w.r.t. (0,0,0) [cm]", precision_);
  trkTab->addColumn<float>("dz", dz, "dz w.r.t. (0,0,0) [cm]", precision_);
  trkTab->addColumn<float>("dxyBS", dxyBS, "dxy w.r.t. the beam spot [cm]", precision_);
  trkTab->addColumn<float>("dzBS", dzBS, "dz w.r.t. the beam spot [cm]", precision_);
  trkTab->addColumn<float>("dxyErr", dxyErr, "dxy uncertainty [cm]", precision_);
  trkTab->addColumn<float>("dzErr", dzErr, "dz uncertainty [cm]", precision_);
  trkTab->addColumn<float>("chi2", chi2, "fit chi2", precision_);
  trkTab->addColumn<float>("ndof", ndof, "fit ndof", precision_);
  trkTab->addColumn<int>("nHits", nHits, "number of pixel hits");
  trkTab->addColumn<int>("hitIdx", hitIdx, "index of the first hit in the hits table");
  trkTab->addColumn<int>("vtxIdx", vtxIdx, "index of the pixel vertex using this track (-1 if none)");

  auto hitTab = std::make_unique<nanoaod::FlatTable>(hx.size(), name_ + "Hits", false);
  hitTab->setDoc("hits of the HLT pixel tracks, positions from the cluster centroid");
  hitTab->addColumn<int>("trkIdx", hTrk, "index of the track in the tracks table");
  hitTab->addColumn<float>("x", hx, "global x [cm]", precision_);
  hitTab->addColumn<float>("y", hy, "global y [cm]", precision_);
  hitTab->addColumn<float>("z", hz, "global z [cm]", precision_);
  hitTab->addColumn<int>("detId", hDetId, "raw DetId");
  hitTab->addColumn<int>("subdet", hSubdet, "1 = barrel (PXB), 2 = endcap (PXF)");
  hitTab->addColumn<int>("layer", hLayer, "barrel layer or endcap disk");
  hitTab->addColumn<int>("sizeX", hSizeX, "cluster size along x (rows)");
  hitTab->addColumn<int>("sizeY", hSizeY, "cluster size along y (columns)");
  hitTab->addColumn<int>("adc", hCharge, "cluster charge");

  auto vtxTab = std::make_unique<nanoaod::FlatTable>(vx.size(), name_ + "Vertices", false);
  vtxTab->setDoc("HLT pixel vertices");
  vtxTab->addColumn<float>("x", vx, "x [cm]", precision_);
  vtxTab->addColumn<float>("y", vy, "y [cm]", precision_);
  vtxTab->addColumn<float>("z", vz, "z [cm]", precision_);
  vtxTab->addColumn<float>("chi2", vchi2, "fit chi2", precision_);
  vtxTab->addColumn<float>("ndof", vndof, "fit ndof", precision_);
  vtxTab->addColumn<int>("nTracks", vntrk, "number of tracks");
  vtxTab->addColumn<float>("sumPt2", vsumPt2, "sum of track pT^2", precision_);

  iEvent.put(std::move(trkTab), "tracks");
  iEvent.put(std::move(hitTab), "hits");
  iEvent.put(std::move(vtxTab), "vertices");
}

void PixelTrackTableProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<std::string>("name", "Pixel");
  desc.add<edm::InputTag>("tracks", edm::InputTag("hltPhase2PixelTracks"));
  desc.add<edm::InputTag>("vertices", edm::InputTag("hltPhase2PixelVertices"));
  desc.add<edm::InputTag>("beamSpot", edm::InputTag("offlineBeamSpot"));
  desc.add<double>("minPt", 0.)->setComment("drop tracks below this pT");
  desc.add<int>("precision", -1)->setComment("mantissa bits for float columns (-1 = full float)");
  descriptions.add("pixelTrackTable", desc);
}

DEFINE_FWK_MODULE(PixelTrackTableProducer);
