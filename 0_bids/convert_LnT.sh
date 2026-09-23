# --------------------------------------
# Script to convert raw data into BIDS organization
# Creates links as relative paths. Else, it has my username
# in the link and it becomes broken for other users.
#
# Inputs:
#     Source: Longitudinal_no_treatment_TPIL
#        Names are, for instance: sub-002

# Output: bids/sub-LnT*
#
# author: Emmanuelle Renauld
# 2026
# ---------------------------------------

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder=CLBP_Databases/Longitudinal_no_treatment_TPIL/complete_dataset_raw/
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"

for subj_folder in $source_path/sub-*
do

    # --- Extracting subject name
    old_name=${subj_folder#$source_path/}

    # --- Extracting number only
    number=${old_name#sub-}

    # --- New name
    new_name=sub-LnT$number

    # For most subjects, we choose visit one, but not all
    visit=1
    if [ $number = "031" ] || [ $number = "035" ]
    then
        visit=2
    fi
    if [ $number = "004" ]
    then
        visit=3
    fi

    echo "$old_name (visit $visit) ----> $new_name"


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
    old_anat_name=ses-v$visit/anat/${old_name}_ses-v${visit}_T1w.nii.gz
    old_anat=$source_path/$old_name/$old_anat_name
    old_anat_relative=../../$relative_path/$old_name/$old_anat_name

    new_anat=$bids/$new_name/anat/${new_name}_T1w.nii.gz


    if [ ! -f $old_anat ]
    then
        echo "... anat not found. Skipped. Where is $old_anat?"
    else
        mkdir $bids/$new_name/anat
        ln -s $old_anat_relative $new_anat
    fi


done


echo "Done. Please verify the symlinks: tree $bids/sub-LnT*"


