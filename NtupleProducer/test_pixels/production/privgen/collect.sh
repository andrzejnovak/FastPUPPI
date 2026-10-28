#!/bin/bash
# Move finished OSG QCD4b outputs (out_QCD4b_<idx>/) into the Slurm layout: ntuple + weights to /scratch/.../privgen,
# the generated-count line to logs/genfilter_QCD4b.txt (read by scout4b.py). Idempotent: handled directories go to done/.
O=/work/submit/novaka/l1pixels/privgen/osg4b; P=/work/submit/novaka/l1pixels/privgen; OUT=/scratch/submit/cms/novaka/l1pixels/privgen
mkdir -p $O/done
for d in $O/out_QCD4b_*; do
  [ -d $d ] || continue
  i=${d##*_}; g=$d/genfilter_QCD4b_$i.txt
  [ -s $g ] || continue
  if grep -q "npass=0" $g; then :; elif [ -s $d/perfNano_QCD4b_$i.root ]; then
    cp $d/perfNano_QCD4b_$i.root $d/genw_QCD4b_$i.txt $OUT/
  else continue; fi
  cat $g >> $P/logs/genfilter_QCD4b.txt; mv $d $O/done/
done
echo "collected: $(ls $O/done | wc -l) OSG jobs; $(ls $OUT/perfNano_QCD4b_*.root 2>/dev/null | wc -l) ntuples in total"
