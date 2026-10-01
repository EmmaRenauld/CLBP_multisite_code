

cd "/mnt/c/Users/Client/Mon disque/Scolaire/4.Post-Doc/PROJET/Step 1 - Freesurfer/essai4 - fastsurfer/stats_apres_refait_les_NA"

demographic_file=../../../databases_mainTable_copy2026-09-30.xlsx

# Volume + aseg + surface area: percentage. Removing BrainSegVolNotVent.
# In aseg file: Some columns are all-zero and make it bug.
# In aseg file: j'ai renommé EstimatedTotalIntraCranialVol en eTIV
for file in aseg # area_lh area_rh volume_rh volume_lh
do
    full_file=DesikanKilianyTourville_$file*

    clbp_plot_stats $full_file $demographic_file \
        --use_prefix_subjs --ignore_mismatch \
        --percent eTIV \
        --skip BrainSegVolNotVent  \
              Left-vessel Right-vessel 5th-Ventricle \
              Left-WM-hypointensities	Right-WM-hypointensities non-WM-hypointensities	\
              Left-non-WM-hypointensities	Right-non-WM-hypointensities	Optic-Chiasm \
        --out_dir figures_apres_refait_les_NA \
        --out_prefix ${file}_percent
done


# Using any one file for BrainSegVolNotVent
file=volume_lh
full_file=DesikanKilianyTourville_$file*
clbp_plot_stats $full_file $demographic_file \
        --use_prefix_subjs --ignore_mismatch \
        --metrics BrainSegVolNotVent eTIV \
        --out_dir figures_apres_refait_les_NA \
        --out_prefix TotalIntracranialVolume_


# Other files: raw
for file in meancurv_lh meancurv_rh thickness_lh thickness_rh
do
    full_file=DesikanKilianyTourville_$file*

    clbp_plot_stats $full_file $demographic_file \
        --use_prefix_subjs --ignore_mismatch \
        --skip BrainSegVolNotVent \
        --out_dir figures_apres_refait_les_NA \
        --out_prefix ${file}
done
