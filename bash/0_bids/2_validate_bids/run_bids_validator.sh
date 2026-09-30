
module load nodejs
export PATH=$HOME/.local/node_modules/bids-validator/bin:$PATH

bids_path=~/projects/def-pascalt-ab/ProjectCLBP_multisite/bids


# Verification:
bids-validator --version


# Create a description file
description_file=$bids_path/dataset_description.json
rm $description_file
cat >> "$description_file" <<EOF
{
  "Name": "ProjectCLBP_multisite",
  "BIDSVersion": "1.15.0",
  "Authors": ["Emmanuelle Renauld", "Pascal Tétreault"]
}
EOF

readme_file=$bids_path/README
echo "ProjectCLBP_multisite" >> $readme_file

# Main call
bids-validator $bids_path --ignoreSubjectConsistency
