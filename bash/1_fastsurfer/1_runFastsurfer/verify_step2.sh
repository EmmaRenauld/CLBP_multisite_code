# ------------ Verifying what worked.


# Log number from the initial list:
SCAN_LIST="/scratch/renaulde/4_fastsurfer/code/scan_list_allSubjs.txt"


# Or to find which log to look at, run this with the SCAN_LIST that was actually used.
#SCAN_LIST=...


new_scan_list=/scratch/renaulde/4_fastsurfer/code/scan_list_failed_step2.txt

rm $new_scan_list


echo "Reading..."
line_number=0
while read -r p; do
    if [ ! -f "$HOME/scratch/4_fastsurfer/results/1_fastsurfer/${p}_FastS/mri/wmparc.mgz" ]; then
        echo "Missing: $line_number -- $p"
        echo $p >> $new_scan_list
    fi
    ((line_number++))

done < $SCAN_LIST



if [ -f $new_scan_list ]
then
   echo "New scan list: $new_scan_list"
   echo "Number of failed subjects:"
   echo `cat $new_scan_list | wc -l`
else
   echo "No failed subject!"
fi
