# Environment on QUEST
```
module purge all
module load python/anaconda3.6
source activate /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py37
```

# Running code
./manage.py add_users
./manage.py assess_slurm_usage
./manage.py email_users
