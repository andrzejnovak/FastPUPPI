#!/bin/bash
#SBATCH --job-name=l1pix_norm
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --time=03:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/norm_%j.out
# QCD vs minimum-bias normalisation per pT-hat bin and HT bin (norm_check.py)
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived; S=/scratch/submit/cms/novaka/l1pixels
WD=$(mktemp -d /tmp/l1pix_norm.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD MB_TOTAL=1999360 HT_MIN=150
pixi run --manifest-path $A/pixi.toml python $WD/norm_check.py $D/norm_check.json $D/scouting/scouting.json $S/local_qcdpt \
  "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root,$S/local_mbnew/perfNano_MinBiasNew_*.root"
rm -rf $WD
