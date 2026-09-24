#!/bin/sh
#SBATCH --mail-user=emmanuelle.renauld.1@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=2:00:00
#SBATCH --gpus=a100_2g.10gb:1



subj=$1
option=$2  # ex, --seg_only or --surf_only


# Vérifier SLURM_CPUS_PER_TASK
nb_cpus=1
if [ ! -z $SLURM_CPUS_PER_TASK ]
then
   nb_cpus=$SLURM_CPUS_PER_TASK
fi



# Explanation of options:
# singularity options:
#	--nv : access GPU resources.
#	--no-home: stops mounting your home directory into singularity.
#	-e: clean environment (do not pass variables)
#	-B: mount the file/folder.
# fastsurfer options:
#	--threads: tells FastSurfer to use that many threads in segmentation
#	   and surface reconstruction. max will auto-detect the number of threads
#	   available, i.e. 16 on an 8-core system with hypterthreading. If the
#	   number of threads is greater than 1, FastSurfer will process the left
#	   and right hemispheres in parallel.

inputs=$HOME/projects/def-pascalt-ab/ProjectCLBP_multisite/bids/
outputs=$HOME/scratch/4_fastsurfer/results/1_fastsurfer
license=$HOME/scratch/4_fastsurfer/freesurfer.lic

output_seg=$outputs/${subj}_FastS/mri/aparc.DKTatlas+aseg.deep.mgz
output_surf=$outputs/${subj}_FastS/mri/wmparc.mgz


# --------- Looking for this subject --------

input_path=$inputs/$subj/anat
input_file=$input_path/${subj}_T1w.nii.gz

if [ ! -f $input_file ]
then
        input_file=$input_path/${subj}_T1w.nii
	if [ ! -f $input_file ]
	then
		echo "Error, file not found $input_file"
		exit
	fi
fi


# ----------- Verifying input / output + GPU options --------------

# In general, GPU required
device='cuda'


# But if option --surf_only, CPU.
# Verifying if an option was given.
# Also verifying required input files to run option --surf_only.
# Also verifying that output files do not already exist.
if [ ! -z $option ]
then
   # ---  Segmentation only
   if [ $option = '--seg_only' ]
   then
       echo "Seg only! (Will be using GPU!)"
       if [ -f $output_seg ]
       then
	   echo "Error, file exists. Can't run --seg_only. Delete this first: $output_seg"
	   exit
       fi
   fi

   # ---- Surface only
   if [ $option = '--surf_only' ]
   then
        echo "Surface only! (Will be using CPU!)"
        device='cpu'
        if [ ! -f $output_seg ]
 	then
	    echo "Error, seg file not found, can't launch surf only. Run --seg_only to create: $output_seg"
	    exit
	fi
	if [ -f $output_surf ]
        then
	    echo "Error, file exists. Can't run --surf_only. Delete this first: $output_surf"
            exit
        fi
   fi
fi



# ------ ok, launching ------


module load apptainer/1.4.5


# need to mount the symlink path too. Finding out where it points
link_file=`readlink -f $input_file`
link_path=`dirname $link_file`
echo "Adding mount to $link_path"

singularity exec \
	--nv --no-mount home,cwd -e  \
        -B $outputs:$outputs -B $license:$license -B $link_path:$link_path \
        ./fastsurfer-gpu.sif \
        /fastsurfer/run_fastsurfer.sh \
        	--fs_license $license \
        	--t1 $link_file \
        	--sid ${subj}_FastS --sd $outputs \
                --3T --threads $nb_cpus --vox_size 1 \
		--device $device $option



echo "-----------------"
echo "DONE. end time: $(date)"
echo "-----------------"
