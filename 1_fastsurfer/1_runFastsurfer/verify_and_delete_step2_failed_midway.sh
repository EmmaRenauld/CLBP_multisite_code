# ------------ Verifying what worked.


# If step 2 failed mid-way, when running again it failes with error saying that some files
# exist and would be overwritten.
# Could delete manually all files from step 2, but there are a lot!
# Deleting the subject instead. Then we can start over.


# Log number from the initial list:
SCAN_LIST="/scratch/renaulde/4_fastsurfer/scan_list_allSubjs.txt"
outputs="$HOME/scratch/4_fastsurfer/results/1_fastsurfer"

new_scan_list="/scratch/renaulde/4_fastsurfer/scan_list_toStartOver.txt"

rm $new_scan_list

echo "Reading..."
line_number=-1
while read -r p; do
    ((line_number++))

    # Subjects whose --surf_only got stopped mid-way
    if [[ ! -f "$outputs/${p}_FastS/mri/wmparc.mgz" && -d "$outputs/${p}_FastS/label" ]]
    then
        echo "To start over: $line_number -- $p"
        echo $p >> $new_scan_list
        # rm -r "$HOME/scratch/4_fastsurfer/results/1_fastsurfer/${p}_FastS"
    fi

    # Subjects who get the error that the corpus callosum segmentation is not there
    # Not sure why!
    if [ ! -f  "$outputs//${p}_FastS/mri/aseg.auto.mgz" ]
    then
        echo "To start over: $line_number -- $p"
        echo $p >> $new_scan_list
        # rm -r "$outputs/${p}_FastS"
    fi


done < $SCAN_LIST
echo "Done"


if [ -f $new_scan_list ]
then
   echo "New scan list: $new_scan_list"
   echo "Number of failed subjects:"
   echo `cat $new_scan_list | wc -l`
else
   echo "No failed subject!"
fi
