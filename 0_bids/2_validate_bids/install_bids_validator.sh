
module load nodejs

node --version
npm --version

npm install --prefix $HOME/.local bids-validator

export PATH=$HOME/.local/node_modules/bids-validator/bin:$PATH
bids-validator --version  # Result: 1.15.0

