#!/bin/bash
# Move held OSG minimum-bias jobs (cluster $1) to Slurm: remove them from condor, submit their lines as a Slurm array.
C=${1:-3817172}
cd /work/submit/novaka/l1pixels/osg
L=held_mb_$(date +%s).txt
condor_q $C -af ProcId JobStatus | awk '$2==5{print $1}' | while read p; do sed -n "$((p+1))p" mb_osg_jobs.txt; condor_rm $C.$p >/dev/null 2>&1; done > $L
N=$(wc -l < $L); [ $N -eq 0 ] && { rm $L; echo "nothing held"; exit 0; }
LIST=$PWD/$L sbatch --export=ALL,LIST=$PWD/$L --array=0-$((N-1)) slurm_mb_v2.sh | sed "s/$/ ($N jobs from $L)/"
