
module load nodejs

export PATH=$HOME/.local/node_modules/bids-validator/bin:$PATH

# Verification:
bids-validator --version


# Main call
bids_path=~/projects/def-pascalt-ab/ProjectCLBP_multisite/bids
bids-validator $bids_path --ignoreSubjectConsistency
