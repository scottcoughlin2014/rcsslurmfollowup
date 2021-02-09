# Environment on QUEST
```
module purge all
module load python/anaconda3.6
source activate /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py37
```

# Running code
./manage.py add_users
./manage.py assess_slurm_usage --start-time=01/01/21 --end-time=01/02/21
./manage.py email_users --google-api-token token.pickle --start-time 2021-01-01 --end-time 2021-01-02 --memory-efficiency-threshold 0.5 --memory-requested-threshold 10 --cpu-efficiency-threshold 0.5 --cpus-requested-threshold 14
