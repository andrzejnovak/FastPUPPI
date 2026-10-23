# Pixel tracks for L1 b-tagging

HLT pixel tracks, their hits and the pixel vertices are written as flat tables in the input
step, and carried through to `perfNano.root`. The L1 SC4NG tagger jets are written with all
class scores as the baseline.

## Setup

```
cmsrel CMSSW_17_0_0_pre2
cd CMSSW_17_0_0_pre2/src
cmsenv
git cms-init
git cms-addpkg DataFormats/L1TParticleFlow DataFormats/L1TCorrelator L1Trigger/Phase2L1ParticleFlow L1Trigger/TrackTrigger SimTracker/TrackTriggerAssociation
# L1PF_17_0_X + SC4NG tagger v2_0_0 backported from CMSSW_17_0_0_pre7
git cms-checkout-topic -u andrzejnovak:L1PF_17_0_X_NGJetModel_v2
scram setup L1Trigger/Phase2L1ParticleFlow/test/l1tsc4ngjetmodel_2.1.0.xml
git clone git@github.com:andrzejnovak/FastPUPPI.git -b 17_0_X_pixelTracks
scram b -j8
```

Without the tagger backport, `L1PF_17_0_X` runs `L1TSC4NGJetModel_v0`, which performs poorly
on Phase2Spring24 samples (b-vs-light AUC ~0.6, large mu/e scores for b jets).

## Running

- `step1_cfg.py`: input step (`runInputs151X.py` + `addPixelTracks()`), on GEN-SIM-DIGI-RAW.
  `pixels=False` gives the standard inputs.
- `step2_cfg.py`: ntuple step (`runPerformanceNTuple.py` + gen-jet flavour, seeded-cone jets,
  `addNGJetTags()`).
- `run_local.sh`: both steps for one RAW file (used on subMIT, max 3 in parallel because of the
  12 GB per-user memory limit). `run_job_osg.sh` / `jobs_osg.sub` do the same on the OSPool in
  the `cmssw/el9` image; they work, but remote reads of the HH->4b RAW files are very slow.

## Tables

- `PixelTracks`: pt, eta, phi, charge, dxy/dz (origin and beam spot) with errors, chi2, ndof,
  nHits, hitIdx (first hit in `PixelHits`), vtxIdx (pixel vertex, -1 if none).
- `PixelHits`: trkIdx, global x/y/z from the cluster centroid (the persisted RecHits have zeroed
  local positions), detId, subdet, layer, cluster sizeX/sizeY/adc.
- `PixelVertices`: x, y, z, chi2, ndof, nTracks, sumPt2. The stored sumPt2 is dominated by
  badly measured high-pT pixel tracks; recompute it with capped track pT to pick the leading
  vertex (see `analysis/make_jets.py`).
- `L1NGJets`: SC4NG jets with `score_<class>` for b, c, uds, g, tau_p, tau_n, mu, e.

## Analysis

```
python3 analysis/make_jets.py jets_hh4b.npz HH4b perfNano_HH4b_*.root
python3 analysis/make_jets.py jets_qcd.npz QCDFlat perfNano_QCDFlat_*.root
python3 analysis/plots.py report jets_hh4b.npz jets_qcd.npz perfNano_HH4b_0.root
python3 analysis/make_report.py report report/index.html
```
