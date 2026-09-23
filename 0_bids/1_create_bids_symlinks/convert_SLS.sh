# --------------------------------------
# Script to convert raw data into BIDS organization
# Creates links as relative paths. Else, it has my username
# in the link and it becomes broken for other users.
#
# Inputs:
#   Source: SubacuteLongitudinalStudy
#
# output: bids/sub-SLS*
#
# author: Emmanuelle Renauld
# 2026
# ---------------------------------------

bids="$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids"

main_folder=CLBP_Databases/SubacuteLongitudinalStudy
source_path="$HOME/projects/def-pascalt-ab/$main_folder"

# One .. to get out of bids, another to get out of our Project.
relative_path="../../$main_folder"

echo "Looking for subjects in : $source_path"

subj_visit1="sub-071 sub-072 sub-073 sub-074 sub-076 sub-077 sub-078 "
subj_visit1+="sub-079 sub-080 sub-081 sub-082 sub-083 sub-084 sub-086 "
subj_visit1+="sub-087 sub-088 sub-089 sub-090 sub-091 sub-092 sub-093 "
subj_visit1+="sub-094 sub-095 sub-096 sub-097 sub-098 sub-099 sub-100 "
subj_visit1+="sub-101 sub-102 sub-103 sub-104 sub-105 sub-106 sub-107 "
subj_visit1+="sub-108 sub-109 sub-110 sub-111 sub-112 sub-113 sub-114 "
subj_visit1+="sub-115 sub-116 sub-118 sub-119 sub-120 sub-121 sub-122 "


subj_visit2="sub-075 sub-085 sub-117"

subj_visit3="sub-007 sub-029 sub-042 sub-052 sub-056"

subj_visit4="sub-003 sub-015 sub-017 sub-022 sub-025 sub-035 sub-043 "
subj_visit4+="sub-044 sub-048 sub-050 sub-054 sub-055 sub-062 sub-065 "
subj_visit4+="sub-066 sub-070"

subj_visit5="sub-008 sub-009 sub-019 sub-023 sub-024 sub-033 sub-036 "
subj_visit5+="sub-037 sub-039 sub-041 sub-049 sub-053 sub-057 sub-059 "
subj_visit5+="sub-060 sub-061 sub-067 sub-068 sub-069"

for visit in 1 2 3 4 5; do
    eval "subjects=\${subj_visit$visit}"

    for old_name in $subjects
    do
        # --- Extracting number only
        number=${old_name#sub-}

        if [ $number -lt 71 ]
        then
            subfolder="Subacutes_001-070"
        elif [ $number -lt 97 ]
        then
            subfolder="Healthy_071-096"
        else
            subfolder="Chronic_097-122"
        fi

        # --- New name
        new_name=sub-SLS$number
        echo "$old_name (in $subfolder), using visit $visit ----> $new_name"

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
        old_anat_name=ses-visit$visit/anat/${old_name}_ses-visit${visit}_T1w.nii.gz
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

        # --- fMRI
        # todo
    done
done


echo "Done. Please verify the symlinks: tree $bids/sub-SLS*"

