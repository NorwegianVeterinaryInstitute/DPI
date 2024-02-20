# Running command 
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --qos=devel --time=0:59:00 --pty bash -i
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --time=2:00:00 --pty bash -i



# using my aliases
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/2024-02-20
java 
MAIN="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI" 
NF="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
CONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/conf/saga_DPI.config"
TEST="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/conf/test_DPI.config"
## with container and slurm 
$NF run $MAIN -c $CONFIG -c $TEST --out_dir . -work-dir $USERWORK/dpi_test  --track DPI -profile apptainer -resume 
# OR 
$NF run $MAIN -c $CONFIG --out_dir . -work-dir $USERWORK/dpi_test -profile apptainer,test_DPI -resume 


