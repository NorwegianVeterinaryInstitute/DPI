2025-05-31
We need to scale up the pipeline
Setting up system to wrangle the results in postgreDB and export after to duckDB


- [ ] creating a subworkflow for postgre - to allow easier transfer

- Trying to see the config of the nodes to see how to deal with access to database
srun --account=nn9305k --mem-per-cpu=24G --cpus-per-task=1 --qos=devel --time=0:30:00 --pty bash -i
nc -l <port_number>


nc -zv <hostname_of_job1_node> <port_number>
