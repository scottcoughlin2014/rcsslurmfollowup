# Install enviroment
```
conda create --prefix /projects/a9009/sbc538/improve_slurm_efficiency_project/improve-slurm-eff-env-py38 -c conda-forge django python=3.8 django-extensions jupyter ipython
```
# Environment on QUEST
```
module purge all
module load python-miniconda3/4.12.0
source activate /projects/a9009/sbc538/Projects/improve_slurm_efficiency_project/improve-slurm-eff-env-py38
```

# Running code
```
./manage.py add_users
./manage.py assess_slurm_usage --start-time 2023-11-01 --end-time 2023-11-30 --nsamples 30
./manage.py email_users --start-time 2023-11-01 --end-time 2023-11-30 --memory-efficiency-threshold 0.5 --memory-requested-threshold 10 --cpu-efficiency-threshold 0.5 --cpus-requested-threshold 14
```

# Start notebook
```
./manage.py shell_plus --notebook --no-browser
```
