
# NOTE: No surface-based analysis here. Explanation from chatGPT:
#   The typical workflow is
#	recon-all
#	      ↓
#	aparcstats2table / asegstats2table
#	      ↓
#	R or Python statistics
#   but for surface-based analyses:
#	recon-all
#	      ↓
#	mris_preproc
#	      ↓
#	mri_glmfit
#	      ↓
#	mri_glmfit-sim
# This file: aparcstats2table and asegstats2table




root=~/scratch/4_fastsurfer
fastsurfer=$root/results/1_fastsurfer
stats=$root/results/4_stats


module load freesurfer
source $EBROOTFREESURFER/FreeSurferEnv.sh
SUBJECTS_DIR="$fastsurfer"
export SUBJECTS_DIR





subjs=$(find $fastsurfer -maxdepth 1 -type d -name 'sub-*' -printf '%f ')
#echo "Running command for subjs:"
#echo "$subjs"


echo "----------- DKTK"
for measure in volume area thickness meancurv  # note. il y en a d'autres possibles!
do
        for hemi in rh lh
        do

                echo ""
                echo "Measure $measure in hemisphere $hemi: "
                aparcstats2table --subjects $subjs \
                    --hemi $hemi --meas $measure --parc aparc.DKTatlas.mapped \
                    --tablefile $stats/Destrieux_${measure}_${hemi}.tsv
        done
done









# Subcortical volumes (aseg):
echo ""
echo "Subcortical volumes (aseg): Preparing subject list"
#rm $root/../subjects_for_stats.txt
#for sub in $subjs
#do
#        echo $sub >> $root/code/subjects_for_stats.txt
#done

echo "Preparing result:"
asegstats2table \
    --subjectsfile $root/code/subjects_for_stats.txt \
    --tablefile $stats/aseg.tsv


