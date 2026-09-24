

module load freesurfer
source $EBROOTFREESURFER/FreeSurferEnv.sh



for subj in results/1_results_NA_manual/*
do
        echo "SUBJ: $subj"

	if [ -f $subj/mri/aparc.DKTatlas+aseg.deep.manedit.mgz ]
	then
		echo "File exists! Delete it manually!"
		# continue
	fi

	cp $subj/mri/aparc.DKTatlas+aseg.deep.mgz $subj/mri/aparc.DKTatlas+aseg.deep.manedit.mgz


	echo "Don't forget to save changes"

	freeview $subj/mri/orig/001.mgz $subj/mri/orig.mgz \
		$subj/mri/aparc.DKTatlas+aseg.deep.manedit.mgz

done
