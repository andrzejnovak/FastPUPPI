import glob, numpy as np, uproot, awkward as ak
fs = sorted(glob.glob("/ceph/submit/data/user/n/novaka/l1pixels/official151X/perfNano_MinBias_*.root"))
hts, nj = [], []
for f in fs:
    a = uproot.open(f)["Events"].arrays(["L1NGJets_pt", "L1NGJets_eta"])
    pt, eta = a.L1NGJets_pt, a.L1NGJets_eta
    sel = (abs(eta) < 2.4) & (pt > 30)
    hts.append(ak.to_numpy(ak.sum(pt[sel], axis=1))); nj.append(ak.to_numpy(ak.sum(sel, axis=1)))
ht, nj = np.concatenate(hts), np.concatenate(nj)
R = 2760 * 11.245  # kHz
print("events", len(ht))
for h in (100, 140, 150, 200, 250):
    m = ht > h
    print(f"HT>{h}: fraction {m.mean():.4f}  rate {m.mean()*R:8.0f} kHz  mean jets(pT>30) {nj[m].mean():.2f}  mean RoIs(<=4) {np.minimum(nj[m],4).mean():.2f}")
