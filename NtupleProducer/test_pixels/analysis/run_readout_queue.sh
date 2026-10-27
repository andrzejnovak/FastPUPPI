#!/bin/bash
#SBATCH --job-name=l1pix_queue
#SBATCH --partition=tier3
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/analysis/slurm_logs/queue_%j.out
# Request latency with queueing behind normal readout (readout_queue.py) on the QUEUE_DUMP files of chip_readout_merge.py.
A=/work/submit/novaka/l1pixels/analysis; D=/scratch/submit/cms/novaka/l1pixels/derived/chip_readout
WD=$(mktemp -d /tmp/l1pix_queue.XXXX); cp $A/readout_queue.py $WD/
pixi run --manifest-path $A/pixi.toml python $WD/readout_queue.py $D/readout_queue.json \
  "$D/queue_j30n.npz:jets>30 narrow windows" "$D/queue_j15w.npz:jets>15 wide windows" \
  "$D/queue_nojetw.npz:every L1 track (early request)" "$D/queue_j30n_nofix.npz:jets>30 narrow, uncorrected CMSSW payload"
rm -rf $WD
