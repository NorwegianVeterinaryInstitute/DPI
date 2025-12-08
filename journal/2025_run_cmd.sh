# Running command 
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --qos=devel --time=0:59:00 --pty bash -i
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --time=2:00:00 --pty bash -i



tmux
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025-12_TEST_DPI


module purge
module load Java/21.0.2 
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
MAIN="${DPI}/main.nf" 
NF="/cluster/projects/nn9305k/bin/nextflow_25.04.7"
NFCONFIG="${DPI}/nextflow.config"
CONFIG="${DPI}/conf/saga_DPI.config"
INPUT="${DPI}/tmp_dev/input_tryssembly.csv"
WORKDIR="/cluster/work/users/evezeyl/DPI_TEST"
# test config 
TEST="${DPI}/conf/test_DPI.config"


## with container and slurm 
$NF run $MAIN -c $CONFIG -c $TEST --out_dir . -work-dir $WORKDIR  --track DPI -profile apptainer -resume 
# OR 
$NF run $MAIN -c $CONFIG --out_dir . -work-dir $WORKDIR -profile apptainer,test_DPI -resume 


