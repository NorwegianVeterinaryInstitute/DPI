

# Step 1 - Retesting that the pipeline runs on a minimal test

First debugging - files are not linked anymore to the database 
It might be because I had modified the code - my previous attemps to fix that
The data is not symlinked for the database so it cannot run 

But first I need to check the channel  output 
ok - so I think I need to use the sql function of nextflow is out now. 
I need to update to the correct nextflow version
then I need to update the python script to be able to add the data to the database
it will then be a sql database and not a sqlite database


<!-- was here before modif - could restore specific folders as is 
I need to restor to commit ID  or to take those files from there : 7e50c99
git diff 7e50c99 -- modules

git checkout 7e50c99 -- modules
git checkout 7e50c99 -- workflows
-->


# Step 2 - Step by step modification of modles and resutls - deleted previous results

```shell
# testing pipeline
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI
./2025_test_run.sh
# testing python script
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results

``` 
1. annotating only the samples 
2. check if some results of the samples needed to be added to the database
- json results for samples from annotation need to be added - starting rewriting this

- [x] testing arguments for the script function
```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/02_ANNOTATE

IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"

apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"
ls */*.json
$SCRIPT --result_file SRR11262033/SRR11262033.json --result_type json --id SRR11262033 --database 2025_DPI_test.sqlite --comment test
$SCRIPT --example
$SCRIPT --version
``` 

This sage is now working - commiting the changes before continuing the dev. 
Commit id : 28f779c
 

- [ ] implementing adding json results to the database
Test run 
```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/02_ANNOTATE
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"

$SCRIPT --result_file SRR11262033/SRR11262033.json --result_type json --id SRR11262033 --database 2025_DPI_test.sqlite --comment test
$SCRIPT --example
$SCRIPT --version
```

2025-04-08 ok now I fixed the adding of json results to the database
launched the pipeline to get the rest of the results

- add the gff results to the database
```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"

$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --result_type gff --id SRR11262033 --database 2025_DPI_test.sqlite --comment test
```





