# 2023-10-10 Pipeline enhancement
- output and small config enhancement


1. issue 198 - fail to publish files
- config publishdir overwrite:true

2. issue - debug parameter - changed to debug (cleaner)

3. Modifying output paths, so its easier to look at all the files in results in output  (including nucdiff)

4. Modifying nucdiff (mummer) output options

```shell
IMG="/cluster/work/users/evezeyl/images/quay.io-biocontainers-nucdiff-2.0.3--pyh864c0ab_1.img"

#apptainer shell --bind $MYPATH:/data,$MYBIN:/data/bin $IMGS/evezeyl-checkr.img 
apptainer shell $IMG
nucdiff --help
nucdiff --nucmer_opt '-param value' 

# only uses one processes per default !! 
nucdiff  --vcf yes $path1 $path2 $ref_query $ref_query
--proc - Number of processes to be used [1]
 --ref_name_full [{yes,no}]
  --query_name_full [{yes,no}]
```
 hum, there is no really options that I want to change in nucmer ...

```shell
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs/saga_DPI.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/nextflow.config"

# we can use the test data for a start
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/assets/data/saga_test.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/2023-10-10"
# this does not need to be changed
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"

module purge
module load Java/17.0.4

$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer --input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI --baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "20231010.sqlite" --comment "'20231010_test'" -resume
```