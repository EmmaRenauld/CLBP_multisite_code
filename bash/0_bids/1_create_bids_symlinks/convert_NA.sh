# --------------------------------------
# Script to convert raw data into BIDS organization
# Creates links as relative paths. Else, it has my username
# in the link and it becomes broken for other users.
#
# Inputs:
#    Source: NucleusAccumbens
#       Names are, for instance: cbp001 or healthy001
#
# Output: bids/sub-NAc or bids/sub-NAh, because healthy controls and CLBP have overlapping numbers.
#
# author: Emmanuelle Renauld
# ---------------------------------------

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder=CLBP_Databases/NucleusAccumbens/subjects
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"

for subj_folder in $source_path/*
do

    # --- Extracting subject name
    old_name=${subj_folder#$source_path/}

    # --- Extracting number only
    number=${old_name#cbp}
    if [ $number == $old_name ]
    then
        suffix=h
        number=${old_name#healthy}
    else
        suffix=c
    fi

    # --- New name
    new_name=sub-NA$suffix$number
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
    old_anat_name=t1/highres001_full_normfilter.nii.gz
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


echo "Done. Please verify the symlinks: tree $bids/sub-NA*"

