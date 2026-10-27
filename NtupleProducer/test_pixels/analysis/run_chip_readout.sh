#!/bin/bash
#SBATCH --job-name=l1pix_chipro
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=03:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/chip_readout_%A_%a.out
# Full-chip readout volume of the regional pixel request (chip_geom.py, chip_readout.py, chip_readout_merge.py).
#   sbatch run_chip_readout.sh geom                  # module / chip geometry from HLT pixel-track hits
#   sbatch --array=0-40 run_chip_readout.sh readout  # 4 minimum-bias files per task
#   sbatch run_chip_readout.sh merge                 # calibration with the emulated chip bitstreams, JSON, figure
# Runs private copies of the scripts (copied to the job's scratch directory at start).
set -e
STAGE=$1
A=/work/submit/novaka/l1pixels/analysis
S=/scratch/submit/cms/novaka/l1pixels
D=$S/derived/chip_readout
mkdir -p $D/parts
WD=$(mktemp -d /tmp/chipro_${SLURM_JOB_ID:-x}_${SLURM_ARRAY_TASK_ID:-0}.XXXX)
for f in chipgeo.py chip_geom.py chip_readout.py chip_readout_merge.py l1ext.py make_jets.py; do
  [ -f $A/$f ] && cp $A/$f $WD/
done
cd $WD
export PYTHONPATH=$WD
PY="pixi run --manifest-path $A/pixi.toml python"
case $STAGE in
  geom)
    $PY $WD/chip_geom.py $D/chip_geom.npz $D/chip_geom_val.json "$S/local_mbnew/perfNano_MinBiasNew_*.root" \
      "$S/local_mbsel_ext/perfNano_MinBiasSel_*.root" 40 ;;
  readout)
    T=${SLURM_ARRAY_TASK_ID:-0}
    FILES=$(ls $S/local_mbsel_ext/perfNano_MinBiasSel_*.root | sort -V | sed -n "$((4 * T + 1)),$((4 * T + 4))p")
    $PY $WD/chip_readout.py $D/chip_geom.npz $D/parts/part_$T.npz $FILES ;;
  merge)
    $PY $WD/chip_readout_merge.py $D/chip_geom.npz "$D/parts/part_*.npz" /work/submit/novaka/l1pixels/itlinks \
      $D/chip_readout.json $A/plots_page/readout_volume.png ;;
esac
cd /; rm -rf $WD
