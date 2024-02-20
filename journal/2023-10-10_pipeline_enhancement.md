
# 2023-10-10 Pipeline enhancement part 2
rerun pairs selection alignment to see if we can output output unaligned sequences 

```shell
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.4"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs/saga_DPI.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/nextflow.config"

# we can use the test data for a start
INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/pairs_preselection/DPI/20230914_DPI_samples_unique_pairs.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/pairs_preselection/DPI/output_20231010"
# this does not need to be changed
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"

module purge
module load Java/17.0.4

$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer --input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI --baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "20231010.sqlite" --comment "'20231010_pairs_preselection'" -resume
```


There is some scripts circulating https://www.biostars.org/p/11948/ that could help 
also from https://github.com/garviz/MUMmer/blob/master/docs/dnadiff.README 
https://github.com/mummer4/mummer/issues/80

# 2023-10-10 Pipeline enhancement part 1
- output and small config enhancement


1. issue 198 - fail to publish files
- config publishdir overwrite:true

2. issue - debug parameter - changed to debug (cleaner)

3. Modifying output paths, so its easier to look at all the files in results in output  (including nucdiff)

4. Modifying nucdiff (mummer) output options check ... not modifiable directly - needs postanalysis

```shell
srun --account=nn9305k --mem-per-cpu=8G --cpus-per-task=1 --qos=devel --time=0:30:00 --pty bash -i
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
trying to obtain one alignment out 
 ```shell 
 /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/2023-10-10/results/NUCDIFF/SRR11262179_SRR11262033
 show-aligns SRR11262179_SRR11262033.delta "SRR11262033_7" "SRR11262033_7"

 show-aligns SRR11262179_SRR11262033.delta "SRR11262033_7" "SRR11262033_7"


srun --account=nn9305k --mem-per-cpu=8G --cpus-per-task=1 --qos=devel --time=0:30:00 --pty bash -i
IMG="/cluster/work/users/evezeyl/images/quay.io-biocontainers-nucdiff-2.0.3--pyh864c0ab_1.img"
apptainer shell $IMG
show-aligns SRR11262179_SRR11262033.delta "SRR11262179_5"  "SRR11262033_1"
 ```
- the coordinates of alignments with tags (sample_ID) are in the coords file
- so the path of input files is hardcoded in the delta file ! we need to fix that 
- if the file is in the same directory there is no problem of running show align, and this ouput will be given - so we just remove the path before the sample name with seed  (maybe its the given option but there is no space )


cat SRR11262179_SRR13588387.delta | sed -e "s#.*/SRR11262179.fna#SRR11262179.fna#g" |sed -e "s# .*/SRR13588387.fna# SRR13588387.fna#g"| head
The space is important here in the second otherwise removes all

Not sure though how to export unaligned ... what is the tag. We need a good example for that

> see rerun pipeline for pairs of differences (selected pairs analysis )

2023-10-13 Added json wrangling to pipeline (python script developped the 12) - so now annotations are included in the database - rerun the pipeline

debugging script - no idea why it does not work now ... as it works on pc
 > 'DataFrame' object has no attribute 'map'. Did you mean: 'max'?
 ok I think I need to update the version of pytest new pandas 
 - ok, and then I needed to find a way to add columns


 - now its nf that needs more debugging 
 - [  ] we might need to make chanels work one at the time for the last part ...
  - [ ]  - Failed to publish file: /cluster/work/users/evezeyl/DPI/ef/a204752362a32a71dc2c1c9b12a9c6/VI56264.fna; to: /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/pairs_preselection/DPI/output_20231010/results/PREP_NUCDIFF/VI56264.fna [copy] -- See log file for details
2023-10-14 So I think the db json process should not run in paralell , should not access the db at the same time 
So need to run as single process 

Fagerlund - this one is failing and I do not knwo why ... cannot find anything bad in input files
  vcf-annotator SRR11262063_SRR11262034_ref_snps_reformated.vcf SRR11262063.gbff --output SRR11262063_SRR11262034_ref_snps_annotated.vcf >  SRR11262063".sdout" 2>&1 
  vcf-annotator SRR11262063_SRR11262034_query_snps_reformated.vcf SRR11262034.gbff --output SRR11262063_SRR11262034_query_snps_annotated.vcf > SRR11262034".sdout" 2>&1
SRR11262034_SRR11262063
I do not why it fails repetitively - remove this pair from input tweny spns



  ```shell 
srun --account=nn9305k --mem-per-cpu=8G --cpus-per-task=1 --qos=devel --time=0:30:00 --pty bash -i

IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/json_annot_import.py"
#BIND="/cluster/work/users/evezeyl/DPI/63/13d70d207316a9b8ea751b78cf4ee6"
#apptainer shell --bind $BIND $IMG
apptainer shell --bind $BIND $IMG
python json_annot_import.py --json VI55586.json --database 20231013.sqlite --sample_id  VI55586

json_path = "VI55779.json"
sql_path = "20231013.sqlite" 
args={"json" : json_path, 
      "database" : sql_path, 
      "sample_id" : "VI55779",
      "version" : "version 0.0-1"}

 ```

# testing command 
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

