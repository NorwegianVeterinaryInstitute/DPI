#! /bin/bash

# To run in tmux to be sure wont disconeect
cd INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/Fagerlund_data/DPI

NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_24.10.5"
SAGA_CONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/conf/saga_DPI.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/nextflow.config"


INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/Fagerlund_data/DPI/input_twentysnps.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/Fagerlund_data/DPI/2025_04-09_test1"
DBOUT=${OUTDIR}/2025-04-09_Fagerlund_DPI.sqlite

# this does not need to be changed
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"


module purge
module load Java/17.0.4

$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer  \
--input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/2025_Fagerlund_DPI \
--baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" \
--sqlitedb $DBOUT --comment "2025_04-09_test1_Fagerlund_max_20_SNPs" -resume 2>&1 | tee 2025_04-09_test1.runlog
