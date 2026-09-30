#!/bin/sh



##################
# Use freeview to create a screenshot, in sagittal view, of
# each subject + brainmask and save it as a png file.
# Hint. Learn to use freeview: https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/OutputData_freeview
#       Learn what to check during QC: https://fscph.nru.dk/slides/Allison/freesurfer.failure_modes.pdf
#          (presented here: https://www.youtube.com/watch?v=gf0BC0xs0tM.)
#       From 12 years ago but I don't find anything more up-to-date.
# Usage: bash 4_QC_freesurfer prefix
# Author: Emmanuelle Renauld
# Date: July 2026
##################
prefix=$1  # ex: LnT


module load freesurfer
source $EBROOTFREESURFER/FreeSurferEnv.sh


# My data is still on scratch!
path_fs=~/scratch/4_fastsurfer/results/1_fastsurfer
path_screenshots=~/scratch/4_fastsurfer/results/2_QC_parc/

project=~/projects/def-pascalt-ab/ProjectCLBP_multisite/



mkdir $path_screenshots


for s in $path_fs/*$prefix*
do

    subj=${s#$path_fs/}
    subj=${subj%%_*}

    echo "================="
    echo "Processing $subj"
    echo "================="

    if [ ! -f $s/mri/wmparc.mgz ]
    then
        echo "ERROR: file wmparc not found. The process did not complete?"
        continue
    fi


    t1=$s/mri/orig.mgz
    b=$s/mri/brainmask.mgz
    labels=$s/mri/aparc+aseg.mgz



    # ---
    # Parcellation
    # ---
    out_file=$path_screenshots/${subj}.png
    if [ -f $out_file ]
    then
        echo "File labels for subj $subj exists. Skipped"
    else
        freeview -v $b $labels:colormap=lut:opacity=0.5 \
	         -viewport axial -zoom 1.5 -ras -12 0 15 tkreg \
                 --ss $out_file 2 1 -cc
        echo "File saved"
    fi


    if [ ! -f $out_file ]
    then
        echo "Error in code? Did not write $out_file"
        exit
    fi





done

