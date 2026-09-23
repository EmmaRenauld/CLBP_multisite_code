
# --------------------------------------
# Script to convert raw data into BIDS organization
# Creates links as relative paths. Else, it has my username
# in the link and it becomes broken for other users.

# Inputs:
#    Source: ~/projects/def-pascalt-ab/Databases/Yoni
#      All anat files are directly in raw_T1
#      Ex: sub-M80302134_ses-1_T1w.nii
#      We remove "M803"; they all have it.
#
# Output: bids/sub-Ashar*
#
# author: Emmanuelle Renauld
# 2026
# ---------------------------------------

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder="CLBP_Databases/Ashar/raw_T1"
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"

for subj_folder in $source_path/*   # subj_folder is actually the nifti file, but keeping similar to other codes.
do

    # --- Extracting subject name
    old_name=${subj_folder#$source_path/}

    # --- Extracting number only
    number=${old_name#sub-M803}
    number=${number%%_ses-*}

    # --- New name
    new_name=sub-Ashar$number
    echo "$old_name ----> $new_name"

    # --- Folder
    if [ -d $bids/$new_name ]
    then
        echo "WARNING. SUBJECT EXISTED! DELETE FIRST"
        continue
    else
        mkdir $bids/$new_name
    fi

    # --- Anat
    # Relative: Two more .. for the relative path to get out of anat, and then subject.
    old_anat_name=$old_name
    old_anat=$source_path/$old_anat_name
    old_anat_relative=../../$relative_path/$old_anat_name

    new_anat=$bids/$new_name/anat/${new_name}_T1w.nii.gz

    if [ ! -f $old_anat ]
    then
        echo "... anat not found. Skipped. Where is : $old_anat"
    else
        mkdir $bids/$new_name/anat
        ln -s $old_anat_relative $new_anat
    fi

done

echo "Done. Please verify the symlinks: tree $bids/sub-Ashar*"