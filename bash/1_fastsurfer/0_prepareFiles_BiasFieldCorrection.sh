
# In preparation for FastSurfer...
# Results are supposedly improved when **BiasFieldCorrection** is run first.
# BiasFieldCorrection requires a skullstripped mask.
# Using **Synthstrip** for the mask. See documentation here: https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/
# It also requires a rescaled version of the T1.


# Note:
# Time requirement:
#     ~ ? per subject for Synthstrip
#     ~ 20 secs per subject for the BiasFieldCorrection
#     Total: <2 minutes per subjects
# Memory requirement: Tried with 3G memory. Synthstrip was killed.


# NOTE
# ANT'S ImageMath sometimes changes the affine!!. Fixed when using my own code.
# But we had issues inside BiasFieldCorrection; bug in their code, where they change
# the affine again. So we rescale as first step, before even synstrip.



database=$1

project=$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite
inputs=$project/bids/
outputs=$HOME/scratch/REALRUN
mkdir $outputs


# Loading modules
module load ants/2.6.5          # Using ANT's biasFieldCorrection
module load freesurfer/8.2.0-1  # Synthstrip is included in Freesurfer.
source "$EBROOTFREESURFER/FreeSurferEnv.sh"



for s in $inputs/sub-$database*
do

        subj=${s#$inputs/}
         
        echo ""
        echo "-------------------------------------------"
        echo "Subject: $subj"
        echo "-------------------------------------------"

        input_file=$inputs/$subj/anat/${subj}_T1w.nii.gz

        if [ ! -f $input_file ]
        then
                input_file=$inputs/$subj/anat/${subj}_T1w.nii
                if [ ! -f $input_file ]
                then
                        echo "No anat!"
                        continue
                fi
        fi

        output_path=$outputs/$subj/
        if [ -d $output_path ]
        then
                echo "OUTPUT FOLDER EXISTS. SKIPPED."
                continue
        fi

        mkdir $output_path

        # ---
        # Rescale first
        # ---
        # If we don't; ANTS displays a warning that we should rescale and
        # suggests [10, 100]
        echo "-----------------> Rescaling [10-100]"
        ImageMath 3 $output_path/T1_rescaled.nii.gz RescaleImage $input_file 10 100

        # ---
        # SkullStrip
        # ---
        # Other options: -b 1 [default]: border to keep?/remove? in mm.
        #                -t number of threads.
        #                -g : use GPU.
        #                --no-csf
        # Do we remove the CSF???
        # I think that for usage in FreeSurfer, maybe not. But here we use it for the
        # BiasFieldCorrection, probably smoother if the mask is also smoother (with the CSF)
        echo "-----------------> Skullstripping with Synthstrip"
        mri_synthstrip -i $output_path/T1_rescaled.nii.gz \
                        -o $output_path/T1_stripped.nii.gz \
                        -m $output_path/T1_brainmask.nii.gz \
                        -f 0   # Background fill value.

        # Stopping if no output. Careful. When mask not found, biasfieldcorrection still runs!!
        if [ ! -f $output_path/T1_stripped.nii.gz ]; then
              echo "Error?? Output file not found. Stopping here."
              continue
        fi

        # ---
        # Rescale after?
        # ---
        # If we want to rescale after synthstrip, with my own code:
        # source ~/envs/scilpy-env/bin/activate  # Has what my code needs.
        # python ~/my_code/rescale_volume.py $input_file $output_path/T1_rescaled.nii.gz 10 100

        # ---
        # Bias Field Correction
        # ---
        # d: dimension
        # v: verbose
        # x: binary mask
        # other: for now, default options
        echo "-----------------> N4 Bias Field Correction"
        N4BiasFieldCorrection -d 3 -i $output_path/T1_rescaled.nii.gz \
                -o [ $output_path/T1_N4corrected.nii.gz, $output_path/T1_N4_BiasField.nii.gz ] \
                -x $output_path/T1_brainmask.nii.gz
done
