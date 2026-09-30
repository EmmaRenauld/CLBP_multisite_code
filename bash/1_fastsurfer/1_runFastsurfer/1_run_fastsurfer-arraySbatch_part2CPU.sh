#!/bin/bash
#SBATCH --mail-user=emmanuelle.renauld.1@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --job-name=fastsurfer
#SBATCH --cpus-per-task=8
#SBATCH --mem=9G
#SBATCH --time=02:30:00
#SBATCH --array=0-6%20
#SBATCH --output=/scratch/renaulde/4_fastsurfer/logs/%A_%a.out




# ---------- Pour tester. SLURM_ARRAY_TASK_ID=0    SLURM_CPUS_PER_TASK=8


# Time. They say ~1h. Adding 2h. For a very small number of sujbects, was not enough.
# Changing to 2:30.

SCAN_LIST="/scratch/renaulde/4_fastsurfer/scan_list_failed_step2.txt"


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
echo "Launching my bash script for subj $subj..."

# ----------- START TASK
bash ~/scratch/4_fastsurfer/code/1_run_FastSurfer.sh $subj --surf_only





