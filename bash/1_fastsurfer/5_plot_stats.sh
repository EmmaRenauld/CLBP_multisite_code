



# Stage 1 - HC vs CP
group=group
out_dir=Stage1_figures


# Stage 2 - levels of pain
group="Tranche de douleur"
out_dir=Stage2_figures


cd "/mnt/c/Users/Client/Mon disque/Scolaire/4.Post-Doc/PROJET/Step 1 - Freesurfer/essai4 - fastsurfer/stats_apres_refait_les_NA"
demographic_file=../../../databases_mainTable_copy2026-09-30.xlsx


# Volume + aseg + surface area: percentage. Removing BrainSegVolNotVent.
# In aseg file: Some columns are all-zero and make it bug.
#    + certains, il y a left, right, total, j'enlève le total
#    + surfaceHoles: not sure I care
# In aseg file: j'ai renommé EstimatedTotalIntraCranialVol en eTIV
for file in aseg #area_lh area_rh volume_rh volume_lh
do
    full_file=DesikanKilianyTourville_$file*

    clbp_plot_stats $full_file $demographic_file \
        --use_prefix_subjs --ignore_mismatch \
        --percent eTIV --hide_outliers \
        --skip BrainSegVolNotVent BrainSegVol \
              BrainSegVol-to-eTIV MaskVol-to-eTIV MaskVol \
              CortexVol CerebralWhiteMatterVol SurfaceHoles lhSurfaceHoles rhSurfaceHoles \
              Left-vessel Right-vessel 5th-Ventricle \
              Left-WM-hypointensities	Right-WM-hypointensities non-WM-hypointensities	\
              Left-non-WM-hypointensities	Right-non-WM-hypointensities	Optic-Chiasm \
        --out_dir $out_dir --group "$group" \
        --fig_prefix ${file}_percentETIV_ --pvals_file ${file}_pvals.tsv -f
done


# Whole cortex values
# Values in aseg are not the same as in other files but correlate perfectly
clbp_plot_stats DesikanKilianyTourville_aseg.tsv $demographic_file \
        --use_prefix_subjs --ignore_mismatch --hide_outliers \
        --metrics BrainSegVol BrainSegVolNotVent eTIV \
            BrainSegVol-to-eTIV MaskVol-to-eTIV MaskVol \
            CortexVol CerebralWhiteMatterVol \
        --out_dir $out_dir --group "$group" \
        --fig_prefix TotalIntracranialVolume_ --pvals_file TotalIntracranialVolume_pvals.tsv -f


# Other files: raw
for file in meancurv_lh meancurv_rh thickness_lh thickness_rh
do
    full_file=DesikanKilianyTourville_$file*

    clbp_plot_stats $full_file $demographic_file \
        --use_prefix_subjs --ignore_mismatch --hide_outliers \
        --skip BrainSegVolNotVent eTIV \
        --out_dir $out_dir --group "$group" \
        --fig_prefix ${file}_ --pvals_file ${file}_pvals.tsv -f
done


# Demographics: Age. Sex: let's just look at the number.
clbp_plot_stats $demographic_file $demographic_file \
    --use_prefix_subjs --ignore_mismatch --hide_outliers \
    --metrics Age --exclude "T1 QC passed" \
    --out_dir $out_dir --group "$group" \
    --fig_prefix demographics_ -f
