#!/bin/bash
#SBATCH --mail-user=emmanuelle.renauld.1@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --job-name=fastsurfer
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --gpus=a100_2g.10gb:1
#SBATCH --time=00:12:00
#SBATCH --array=0-18%20
#SBATCH --output=/scratch/renaulde/4_fastsurfer/logs/%A_%a.out


# Based on documentation, 1 minute per subject. Giving 10, then 11, then 12.


# ---------- Pour tester. SLURM_ARRAY_TASK_ID=0    SLURM_CPUS_PER_TASK=8

# Change the number in the array to fit the number of scans here:
SCAN_LIST="/scratch/renaulde/4_fastsurfer/scan_list_failed_step1.txt"




# === Get the scan list and select the right line based on the current task ID.
# rm $SCAN_LIST
# for subj in $inputs_dir/*
# do
# 	echo ${subj#inputs_dir} >> $SCAN_LIST
# done
SCAN=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$SCAN_LIST")
if [ -z "$SCAN" ]; then
    echo "ERROR: No scan found for array task $SLURM_ARRAY_TASK_ID"
    exit 1
fi



subj=$SCAN
echo "================="
echo "Launching my bash script for subj $subj..."
echo "================="

bash ~/scratch/4_fastsurfer/code/1_run_FastSurfer.sh $subj --seg_only





