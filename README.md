# Install enviroment
```
conda create --prefix /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py38 -c conda-forge django python=3.8 django-extensions jupyter ipython
```
# Environment on QUEST
```
module purge all
module load python/anaconda3.6
source activate /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py38
```

# Running code
```
./manage.py add_users
./manage.py assess_slurm_usage --start-time=05/01/21 --end-time=05/02/21
./manage.py email_users --start-time 2021-05-01 --end-time 2021-05-02 --memory-efficiency-threshold 0.5 --memory-requested-threshold 10 --cpu-efficiency-threshold 0.5 --cpus-requested-threshold 14
```

# Start notebook
```
./manage.py shell_plus --notebook --no-browser
```
