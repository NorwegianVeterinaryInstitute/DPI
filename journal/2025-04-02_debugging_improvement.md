

# Step 1 - Retesting that the pipeline runs on a minimal test

```shell
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs/saga_DPI.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/nextflow.config"

# we can use the test data for a start
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/assets/data/three_test.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI"

# this does not need to be changed
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"


$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer --input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI --baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "2025-04-02-Test.sqlite" --comment "'testing for debugging'" -resume
```

First debugging - files are not linked anymore to the database 
It might be because I had modified the code - my previous attemps to fix that
The data is not symlinked for the database so it cannot run 
I need to restor to commit ID : 7e50c99



# Step 2 - 