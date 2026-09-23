#!/bin/bash


##################
# Use freeview to create a screenshot, in sagittal view, of
# each subject, and save it as a png file.
# Usage: bash 4_QCwithFreeview.sh prefix
# Author: Emmanuelle Renauld
# Date: July 2026
##################
prefix=$1  # ex: LnT


module load freesurfer
source $EBROOTFREESURFER/FreeSurferEnv.sh

bids_path=~/projects/def-pascalt-ab/ProjectCLBP_multisite/bids
derivative_path=~/projects/def-pascalt-ab/ProjectCLBP_multisite/derivatives/0_bids_and_QC/
screenshots_path=$derivative_path/results/outputs_screenshots


mkdir $screenshots_path

for f in $bids_path/*$prefix*
do

    subj=${f#$bids_path/}
    subj=${subj%%_*}

    t1=$bids_path/$subj/anat/*T1w.nii*
    out_png=$screenshot_path/${subj}.png

    if [ -f $out_png ]
    then
        echo "Subj $subj already exists. Delete first."
    else
        if [ -f $t1 ]
        then
            echo "Processing $subj"
            freeview -v $t1 -ss $out_png
        else
            echo "Subj $subj : no anat"
        fi
    fi
done

