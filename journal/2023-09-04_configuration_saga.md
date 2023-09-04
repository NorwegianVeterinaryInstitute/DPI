# Installation pipeline on SAGA
## Organisation
DPI is located here on SAGA: `/cluster/projects/nn9305k/vi_src/DPI`

Configuration file: We use the same configuration that has been done for 
[ALPPACA](https://github.com/NorwegianVeterinaryInstitute/ALPPACA) : `/cluster/projects/nn9305k/nextflow/configs/saga_new.config`


## After discussion with Håkon 
! we might need to install bakta database in the image - this is not done


## Test local SAGA 
- creating config : saga_DPI.config based on saga_new.config
- getting job

```bash
module purge
module load Java/17.0.4
```

- Paths 

```bash 
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.1"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI"
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/single_test.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/TEST"
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/nextflow.config"
```

Testing purpose only
```bash
$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer  \
--input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI \
--baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "test.sqlite" -resume
```

Modifications to do: 
- seems need to update amrfinder database 
    amrfinder_update --force_update --database /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db/amrfinderplus-db 
    -   need to use the same version bakta so try with apptainer <https://apptainer.org/> 
    Running image: 
    hum tried but is trying to create a project ... /cluster/project - which is bad !
    So trying to update via conda  and relaunching. 

- hum something weird with image - changing the image in the annotation process
- adjusted the memory a bit up seemed to bug first because of that 
> ok now its working

Next bug - script to write version of the file - correct in 3 python script - easy

Now adding the test for the 3 pairs
```bash
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/saga_test.csv"
```
and resume 

#### Example to run apptainer
```bash 
srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=1 --qos=devel --time=2:00:00 --pty bash -i
IMAGE="/cluster/work/users/evezeyl/images/oschwengers-bakta-v1.8.1.img"
apptainer shell $IMAGE

```


