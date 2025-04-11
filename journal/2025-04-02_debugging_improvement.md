date::2025-04-02
date::2025-04-08 

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

date::2025-04-08 
and
date::2025-04-09
ok now I fixed the adding of json results to the database
launched the pipeline to get the rest of the results

- add the gff results to the database
```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"

#$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --result_type gff --id SRR11262033 --database 2025_DPI_test.sqlite --comment test

#$SCRIPT --result_file SRR11262179_SRR11262033_ref_snps.gff  --result_type gff --id SRR11262033 --database 2025_DPI_test.sqlite --comment test

#$SCRIPT --result_file ../SRR11262179_SRR11262033/SRR11262179_SRR11262033_query_blocks.gff  --result_type gff --id SRR11262033 --database 2025_DPI_test.sqlite --comment test

#$SCRIPT --result_file ../SRR11262179_SRR11262033/SRR11262179_SRR11262033_ref_snps.gff  --result_type gff --id SRR11262033 --database 2025_DPI_test.sqlite --comment test

$SCRIPT --result_file ../SRR11262179_SRR11262033/SRR11262179_SRR11262033_query_blocks.gff --id SRR11262179_SRR11262033 --database 2025_DPI_test.sqlite --comment test
$SCRIPT --result_file ../SRR11262179_SRR11262033/SRR11262179_SRR11262033_ref_snps.gff  --id SRR11262179_SRR11262033 --database 2025_DPI_test.sqlite --comment test

$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --id SRR11262179_SRR11262033 --database 2025_DPI_test.sqlite --comment test
$SCRIPT --result_file SRR11262179_SRR11262033_ref_snps.gff  --id SRR11262179_SRR11262033 --database 2025_DPI_test.sqlite --comment test


```
This is working. 

Restructuting the code so I can use modules better.
Retesting 
Ok it seems to be working now - continuing

- Now need to add the vcf annotated results to the database 

```bash

cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/06_VCF_ANNOTATOR
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"

# $SCRIPT --result_file SRR11262179_SRR11262033_query_snps_annotated.vcf  --result_type vcf --id SRR11262033 --database 2025_DPI_test.sqlite --comment test


$SCRIPT --result_file SRR11262179_SRR11262033_query_snps_annotated.vcf  --id SRR11262033 --database 2025_DPI_test.sqlite --comment test
```

This appears tobe working
I want to test if the function test is working

```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/06_VCF_ANNOTATOR
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/vcf_to_df.py"
python $SCRIPT
```

- now I need to add the stats file 

```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"
$SCRIPT --result_file SRR11262179_SRR11262033_stat.out  --result_type stats --id SRR11262033 --database 2025_DPI_test.sqlite --comment test

# modified auto detection result type
$SCRIPT --result_file SRR11262179_SRR11262033_stat.out  --id SRR11262033 --database 2025_DPI_test.sqlite --comment test
```
ok - working


**FIXES that were needed - and now summary and continuing fixes 
- [x] add comment table to the database - can be used for fast ckecking duplicates ...
- [x] automatic detectionof result types (I do not export the function - its an helper)

- [x] reformatting the nf pipeline to allow adding the results to the database
- [x] debugging - the output in table is not the correct tables - need to check python script and lack tables. Vcf and gff are not added to the database. 
- changed ' to "" in python script when passing arguments (I do not think was the problem but making sure)
- ? modules to make the script not loaded - maybe : tested gff vcf and stats - all working - duplicates in database when run so need to check that when rest is fixed
- so the problem is probably in the channels it receives. ok, needed to transform the channel - the maxfork runs once so a bit tricky 
- [x] changed the channels and merging to have all results in one channel (id, resultfile)
- [x] implementing in pipeline for testing on several files
Working but is slow - wont be able to process many isolates 

2025-04-10 
- [x] optimizing pipeline (involves restructuring the scripts and some modules)
Allow each results to be added to a single database, then merge the results of all sqlite databases into a single database.
The checking of already existing data will then be done during the merging process, because only new data for the single database. 
    - [x] rewriting of results_to_db.py (simplification, and reformating to better python) + testing
    - [x] rewriting of process_result_file - simplification (no control of existing data in sqlite) + testing 
    - [x] changing the workflow and adding merging module into a single database 

- [x] small error in prep_sequences_df in json_to_df when table is incomplete. Need to inspect further ?  - fixed 
- [x] ? missing data in features, need to add NaN (None in sqlite) to all other columns - handled for all types of data - fixed 
- [x] launching test script for getting all the single databases. Ot seems to be running without problems. 

2025-04-11 
- [x] nextflow find a way to remove all sqlite files / merging db  from cache - so I do not need to restart all 
- No we change the process and output name - so it will work as filter. is faster

- No we change the process and output name - so it will work as filter. is faster
- [x] added defensive programing to all functions and restesting. Then if some error occur iut will make nextflow process fail when its needed
    - [x] added failure function, read file, general failure, empty tables ...
    - [x] retested all
    - [x] created log functions for homoegenization of message and login to a file 
- [x] fixing the merging script that was started ? yeterday ?
Warning message will be given if data frames are empty (to make checking eaier)
- [x] improved testing way (removed all script previously above, made a script test for testing, otherwise hell, and was difficult to find out how
to test within the container due to scope of python modules. After lots of troubleshooting with gemin  - we got the solution, helped also to understand
scope of package and modules ... though I might forget but  I will have an example to follow.)
- [x] We need to add val to sqlite name, using val - because then it will allow checking which sqlite_output had problems more easily . ... 

- [ ] script for merge to main github from main, update dev from main and then and continue on working with dev (commands - so do not need to search next time)
- [ ] testing the merging of the sqlite databases. We might still have to many paths ... will see, but Will be better for nf debugging / processing errors. Will make retry the processes 

running now test nf in tmux login 5
# TODO 
- [ ] optimization sqlite writing in database - need to have it add data efficiently (at the end because basic functions have to work)
- [ ] automatic script to run unittesting - check if working and improve that  




# Helpers gemini 
Hi, can you make an unittest for this file : xx.py. I want to be able to have the result in a jupyter notebook, your explanations included