# Install enviroment
```
module purge
module load mamba/23.1.0
mamba create --prefix=/projects/a9009/sbc538/Projects/OverSubscription/envs/over-subscription-env-py310 -c conda-forge django python=3.10 django-extensions jupyter ipython pandas
```
# Environment on QUEST
```
module purge all
module load mamba/23.1.0
source activate /projects/a9009/sbc538/Projects/OverSubscription/envs/over-subscription-env-py310
```

# Running code
One time initialization of Django database and tables based on the Model definition in `efficiency/models.py`.
```
module purge all
module load mamba/23.1.0
source activate /projects/a9009/sbc538/Projects/OverSubscription/envs/over-subscription-env-py310
./manage.py makemigrations
./manage.py migrate
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
