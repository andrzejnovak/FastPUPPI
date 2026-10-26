#!/bin/bash
#SBATCH --job-name=l1pix_pucopy
#SBATCH --partition=submit
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=06:00:00
#SBATCH --output=/work/submit/novaka/l1pixels/privgen/logs/pucopy_%a.out
# Copy one MinBias GEN-SIM file (pileup pool for the private production) to /ceph
LFN=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" /work/submit/novaka/l1pixels/privgen/pileup_lfns.txt)
OUT=/scratch/submit/cms/novaka/l1pixels/pileup_gs/$(basename $LFN)
[ -s $OUT ] && exit 0
export X509_USER_PROXY=$HOME/x509up_u248613
source /cvmfs/cms.cern.ch/cmsset_default.sh
for R in root://cmsxrootd.fnal.gov/ root://cms-xrd-global.cern.ch/ root://xrootd-cms.infn.it/; do
  xrdcp -f -s ${R}${LFN} $OUT.part && mv $OUT.part $OUT && echo "DONE $LFN via $R" && exit 0
  echo "failed via $R"
done
rm -f $OUT.part; exit 1
