
# part 2: the chosen subacutes only, from ACPS, different because pre-skullstripped

subjs="1372 1374 1447 1534 1550 1801 1878 1883 1909 1926 1933 1949"

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder=CLBP_Databases/Yale_vs_ACPS_vs_eLife2024/ACPS/Longitudinal_HealthyVisit2_subVisits1-2/Sub
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"


for number in $subjs
do

    old_name=$number

    # --- New name
    new_name=sub-ACPS$number
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
    old_anat_name=visit2/anat/${number}_T1w.nii.gz
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


echo "Done. Please verify the symlinks: tree $bids/sub-ACPS*"
