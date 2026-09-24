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

root=~/projects/def-pascalt-ab/ProjectCLBP_multisite/derivatives/1_freesurfer_fastsurfer/essai4_fastsurfer/
path_screenshots=$root/results/2_QC_surf/



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

    if [ $subj == 'sub-BPS209' ]
    then
        echo "------------------------ BUG À VOIR SUB 209"
        continue
    fi

    t1=$s/mri/orig.mgz

    # ----------------
    # Surfaces
    # ----------------
    out_file=$path_screenshots/${subj}.png
    if [ -f $out_file ]
    then
        echo "File surfaces for subj $subj exists. Skipped"
    else
        echo "   Creating view of surfaces. Take the time to "
        echo "   scroll through slices (arrow up/down). Then, close."
        echo "   It will save the sagittal view as a png."
        freeview -v $t1 \
                 -f $s/surf/lh.pial.T1:edgecolor=red $s/surf/lh.white:edgecolor=blue \
                    $s/surf/rh.pial.T1:edgecolor=red $s/surf/rh.white:edgecolor=blue \
                 -viewport sagittal -zoom 1.5  -ras -12 0 0 tkreg \
                 --ss $out_file 2 1 -noquit
    fi

    if [ ! -f $out_file ]
    then
        echo "Error in code? Did not write $out_file"
        exit
    fi





done

