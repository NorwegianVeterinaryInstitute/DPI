# Pipeline enhancement 
date :: 2023-09-29 

Reason : 
- annotation by pairs creates duplicates at annotation, which is the most heavy step
- this is not effective and impedes running a lot of comparison 

What needs to be done : 
- The annotation module must run alone, and then pairs need to be reconstitued 
- Find a solutions to do so

## Testing command 
Test dataset - running command 

```shell 
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs/saga_DPI.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/nextflow.config"

# we can use the test data for a start
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/saga_test.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/enhancement"

# this does not need to be changed
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"

module purge
module load Java/17.0.4
$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer  \
--input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI-TEST \
--baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "20230929_DPI.sqlite" --comment "20230929_DPI_test" -resume
```

# Testing while modifying 
Testing images directly 
[Aptainer summary](https://hsf-training.github.io/hsf-training-singularity-webpage/07-file-sharing/#:~:text=By%20default%2C%20Apptainer%20binds%3A%201%20The%20user%E2%80%99s%20home,configuration%2C%20it%20may%20vary%20from%20site%20to%20site.)
```shell 
IMGS="/cluster/work/users/evezeyl/images"
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/saga_test.csv"
MYPATH="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data" 
MYBIN="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin"
apptainer shell --bind $MYPATH:/data,$MYBIN:/data/bin $IMGS/evezeyl-checkr.img 

cd /data 
Rscript bin/input_check.R --input $INPOUT
```
So this works this is not the R script Nor the image 
- it can be a problem of bind ? at redirect to path ? 

Testing in one of the pipeline dir 

```bash 

MYPATH=$(pwd)
MYBIN="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin"
IMGS="/cluster/work/users/evezeyl/images"
apptainer shell --bind $MYPATH:/data,$MYBIN:/data/bin $IMGS/evezeyl-checkr-latest.img 

cd /data 
Rscript bin/input_check.R --input saga_test.csv
```
ok, its because of the bind - it cant follow the path 
Needed to add environment variable for .bashrc and testing

Well I added the bind and this still does not work 
trying to see if the exec command is working

```bash 

IMGS="/cluster/work/users/evezeyl/images"
apptainer exec $IMGS/evezeyl-checkr-latest.img Rscript /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/input_check.R --input saga_test.csv
```

This works so WHY ? 

- trying to copy the file so it bypass the mount using in process `  stageInMode 'copy'` that copy the file but still not working
- trying to use latest nf version nextflow_23.04.4 (should not do huge doiff)

ok, was interaction with Rprofiles ... 

--- 2023-10-02 worflow and modules reformated --- last testing to see if works :) 


æ7# Ressources
- nf carpentry https://carpentries-incubator.github.io/workflows-nextflow/08-configuration/index.html 
nextflow config workflow_02.nf -profile test

# Testing now with fagerlund data and says inputfile is missing .... 
but when I echo the path of the file and I launch in the directory this works 
when I test with the small input file this works ... 
but I was in a tmux session ... try tmux session with testdata 
test working with tmux 



checking file format 

```shell
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs/saga_DPI.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/nextflow.config"

# we can use the test data for a start
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/Fagerlund_data/DPI/input_twentysnps.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/Fagerlund_data/DPI/output_20231002"
# this does not need to be changed
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"

module purge
module load Java/17.0.4

$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer --input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI --baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "DPI_commit_351b806_Fagerlund_20231002.sqlite" --comment "'20231002_Fagerlund_max_20_SNPs_DPI;commit_351b806'" -resume
```