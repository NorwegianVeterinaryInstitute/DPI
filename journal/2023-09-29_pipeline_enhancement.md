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
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.1"
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

cd data 
Rscript input_check.R --input $INPOUT
```
So this works this is not the R script Nor the image 


## What needs to be modified 
### Most important 


- annotate per sample - ok 
    - [  ] how to use the tag to recover


### other nice enhancements
- [ ] versions per module to avoid duplicates
    - [ ] change python scripts to be able to output version
    pythonscript --version must output the version to screen -> to a fileversion of 
    eg. python $projectDir/bin/prep_nucdiff.py --version > prep_nucdiff.version
    - [x] change Rscript also for that Rscript $input --version > input_check.version
    - [ ] add optparse / check image 
    - [ ] eventually make the conda version for container R
- [ ] make config for containers and conda parameters ? 
- [ ] adjust what output file we want AND make the documentation with the description of those output files