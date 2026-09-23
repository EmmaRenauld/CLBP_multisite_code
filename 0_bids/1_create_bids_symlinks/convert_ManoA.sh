# --------------------------------------
# Script to convert raw data into BIDS organization
# Creates links as relative paths. Else, it has my username
# in the link and it becomes broken for other users.
#
# Inputs:
#   Source: Mano-BrainNetworkChange, site 1
#     Names are, for instance: sub_01_control_site_1
#     All subjects are two-digits
#
# Output: bids/sub-ManoA*
#
# author: Emmanuelle Renauld
# 2026
# ---------------------------------------

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder=CLBP_Databases/Mano-BrainNetworkChange/Site1
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"

for subj_folder in $source_path/*
do

    # --- Extracting subject name
    old_name=${subj_folder#$source_path/}

    # --- Extracting number only
    number=${old_name#sub_}
    number=${number:0:2}

    # --- New name
    new_name=sub-ManoA$number
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
    old_anat_name=anat/${old_name}_T1w.nii.gz
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

    # --- fMRI
    # todo
done


echo "Now removing rejected subjects..."

# HC
mv $bids/sub-ManoA08 $bids/rejected_ManoA08_VASnotNull
mv $bids/sub-ManoA35 $bids/rejected_ManoA35_VASnotNull

# CBP
mv $bids/sub-ManoA51 $bids/rejected_ManoA51_VAS0
mv $bids/sub-ManoA56 $bids/rejected_ManoA56_VAS0
mv $bids/sub-ManoA58 $bids/rejected_ManoA58_VAS0
mv $bids/sub-ManoA59 $bids/rejected_ManoA59_VAS0


echo "Done. Please verify the symlinks: tree $bids/*ManoA*"

