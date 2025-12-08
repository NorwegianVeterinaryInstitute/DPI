# Upscaling code to be able to run at large scale

date:: 2025-12-08

# Implement working with postgree database to allow concurent read/write into database

Challenges

- [ ] problem is to be able to run it on HPC system -> means cannot work into nf process but need to be local I think
- [ ] no acess to network / internet from the compute nodes
- [ ] collecting intermediary files -> too many files which creates too many symlinks ... so I need to have a certain size of collecting otherwise nextflow will bug
- [ ] need adding missing columns
- [ ] need to use jsonDB datatype -> will be easier to store the diff files -- so need to chane that in the nf script
- [ ] I need a way to control orders of results that go into the database, are given in the same order, in case I need to resume the job --- maybe use the list of pairs to get the results in order -> collect the results and sort them using the pair ID before batching to output
- [ ] choose an appropriate batch size eg 50 for a starter
- [ ] make output order deterministic 
- [ ] create one table per result type ! -> that will be easier to debug



## Initiation database 

```bash 

```


# Relics 
```bash

apptainer pull postgres.sif docker://postgres:latest
# prepare data directory
mkdir -p $HOME/pg_data
mkdir -p $HOME/pg_run
# Initialize the database (run only once)
apptainer exec \
    -B $HOME/pg_data:/var/lib/postgresql/data \
    -B $HOME/pg_run:/var/run/postgresql \
    postgres.sif \
    initdb -D /var/lib/postgresql/data
# Start the instance
apptainer instance start \
    -B $HOME/pg_data:/var/lib/postgresql/data \
    -B $HOME/pg_run:/var/run/postgresql \
    postgres.sif \
    pg_instance \
    postgres -D /var/lib/postgresql/data -k /var/run/postgresql

# verify and connect
apptainer instance list
# disconnect
apptainer instance stop pg_instance

```

pg_instance: The name you are giving this background instance.
postgres -D ...: The actual command starting the server.
-k /var/run/postgresql: Explicitly tells Postgres to place the unix socket in our writable bind mount (otherwise it tries /tmp or defaults and might miss our bound folder).






```bash
srun --account=nn9305k --mem-per-cpu=4G --cpus-per-task=1 --qos=devel --time=0:30:00 --pty bash -i
```


SELECT avg((data->>'temperature')::numeric)
FROM pipeline_results
WHERE data ? 'temperature'; -- Only rows where this key exists