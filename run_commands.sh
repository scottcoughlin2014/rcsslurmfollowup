#!/bin/bash 

module purge all
module load python/anaconda3.6
source activate /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py38

# Add any new users who we have not tracked before
./manage.py add_users

# please enter dates as MM/DD/YY
echo "Determining usage stats between $1 and $2"
./manage.py assess_slurm_usage --start-time=$1 --end-time=$2
