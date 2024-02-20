# Running command 
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --qos=devel --time=0:59:00 --pty bash -i
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --time=2:00:00 --pty bash -i


# using my aliases
java 

MAIN="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI" 
NF="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
CONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/conf/saga_DPI.config"

## with container and slurm 
$NF run $MAIN -c $CONFIG --out_dir . -work-dir $USERWORK/test  --track coverage --input input.csv  -profile apptainer -resume 


# Debug 
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --qos=devel --time=0:59:00 --pty bash -i
cd ... 

IMG="/cluster/work/users/evezeyl/images/"
apptainer shell $IMG 
