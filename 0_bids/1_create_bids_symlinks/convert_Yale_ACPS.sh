
# --------------------------------------
# Script to convert raw data into BIDS organization
# Creates links as relative paths. Else, it has my username
# in the link and it becomes broken for other users.
#
# Inputs:
#   Source: Yale-ACPS/Yale
#
# Output: bids/sub-Yale*
#
# Note: Found twice the same data. "ACPS" is pre-skullstripped,
#       so we prefer using "Yale". But we have access to more
#       data in ACPS: we have the subacute subjects, and visit 2.
#
# author: Emmanuelle Renauld
# 2026
# ---------------------------------------

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder=CLBP_Databases/Yale_vs_ACPS_vs_eLife2024/Yale
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"

for subj_folder in $source_path/*/*
do

    # --- Extracting subject name
    old_name=${subj_folder#$source_path/}
    subfolder=${old_name%%/*}
    old_name=${old_name#CBP_noOp/}
    old_name=${old_name#HC/}

    # --- Extracting number only
    number=${old_name#sub-}

    # --- New name
    new_name=sub-Yale$number
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
    old_anat_name=anat/${old_name}_ses-bsl_T1w_defaced.nii.gz
    old_anat=$source_path/$subfolder/$old_name/$old_anat_name
    old_anat_relative=../../$relative_path/$subfolder/$old_name/$old_anat_name

    new_anat=$bids/$new_name/anat/${new_name}_T1w.nii.gz

    if [ ! -f $old_anat ]
    then
        echo "... anat not found. Skipped. Where is $old_anat?"
    else
        mkdir $bids/$new_name/anat
        ln -s $old_anat_relative $new_anat
    fi

done


echo "Done. Please verify the symlinks: tree $bids/sub-Yale*"

