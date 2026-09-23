
########################
# Simply launch mrinfo on all files
# Usage: bash 3_print_mrinfo.sh prefix
# Author: Emmanuelle Renauld
# Date: July 2026
########################

prefix=$1   # Ex: LnT


module load StdEnv/2023
module load gcc/12.3
module load mrtrix/3.0.8

bids_path=~/projects/def-pascalt-ab/ProjectCLBP_multisite/bids
derivative_path=~/projects/def-pascalt-ab/ProjectCLBP_multisite/derivatives/0_bids_and_QC
output_path=$derivative_path/1_mrinfo/

mkdir -p $output_path

echo "Reading all headers for database: $prefix"

if [ -f $output_path/mrinfo_output_$prefix.txt ]
then
   rm $output_path/mrinfo_output_$prefix.txt
fi
mrinfo $bids_path/*$prefix*/anat/*T1w.nii* >> $output_path/mrinfo_output_$prefix.txt 2>&1

echo "Saved all mrinfo. To read them: cat $output_path/mrinfo_output_$prefix.txt"
