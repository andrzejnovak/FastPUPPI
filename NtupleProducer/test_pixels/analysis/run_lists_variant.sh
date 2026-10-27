#!/bin/bash
#SBATCH --job-name=l1pix_listvar
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/listvar_%A_%a.out
# Per-jet list variants (make_l1ext_lists.py) in the pixi env: OUTDIR/files.txt lists "SAMPLE file" per task;
# MODE (pixel | otonly) and SKIP_LIDS (e.g. 1 = no barrel layer 1) are passed through the environment
A=/work/submit/novaka/l1pixels/analysis
read SAMPLE F <<< "$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" $OUTDIR/files.txt)"
OUT=$OUTDIR/${SAMPLE}_$(basename $F .root).npz
[ -f $OUT ] && exit 0
WD=$(mktemp -d /tmp/l1pix_listvar.XXXX); cp $A/*.py $WD/
cd $A; export PYTHONPATH=$WD JET_PTMIN=15
pixi run --manifest-path $A/pixi.toml python $WD/make_l1ext_lists.py $OUT.tmp.npz $SAMPLE $F && mv $OUT.tmp.npz $OUT && echo DONE
rm -rf $WD
