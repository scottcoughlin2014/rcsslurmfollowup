#!/bin/bash 

module purge all
module load python/anaconda3.6
source activate /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py38

# Add any new users who we have not tracked before
./manage.py add_users

month_start=$1
month_end=$2
day_start=$3
day_end=$4

for month in `seq $month_start $month_end`; do 
    for day in `seq $day_start $day_end`; do
        nextday=$((day + 1))
        echo "Determining usage stats between $month/$day/21 and $month/$nextday/21"
        ./manage.py assess_slurm_usage --start-time=$month/$day/21 --end-time=$month/$nextday/21
    done
done
