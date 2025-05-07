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

NB seems some saga random errors, diseapeared after relaunch 
```shell
2025-04-12 06:45:19,588 - INFO - Processing SRR11262033_SRR11262179 in SRR11262179_SRR11262033_query_snps_annotated.vcf
2025-04-12 06:45:19,593 - ERROR - An error occurred during processing of SRR11262033_SRR11262179: 'module' object is not callable
2025-04-12 06:45:19,593 - ERROR - Check 20250412_064519_results_to_db.log for more details
```
2025-05-01

Ok - lots of debugging but this is fixed. Hell of a problem with the scopes. It works with the pipeline now, unsure if it will still work for individual testing. I will have to retry.


tmux in login node 5

- [x] testing the merging of the sqlite databases. We might still have to many paths ... will see, but Will be better for nf debugging / processing errors. Will make retry the processes 

relaunching test to see if still errors
```bash
bash 2025_test_run.sh > 2025-05-01_test_nf_log
```


I need to relaunch the Wrangling DB to be sure what is wrong. So I need to remove all directories
```bash
# Run this from the 'work' directory
ls */*/*.sqlite | cut -d '/' -f 1 | sort -u
ls */*/*.sqlite | cut -d '/' -f 0 | sort -u

# Run this from the 'work' directory to get the level 2 
find . -mindepth 3 -maxdepth 3 -name "*.sqlite" -type f -print0 | xargs -0 -I {} dirname {} | sort -u

# ! be carefull can remove also symlinks ! beed to modify pattern then 

myscript="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/utilities/rm_nf_selected_testdir.sh"
bash $myscript *.sqlite

# ok now checking the dbs in results
cp /cluster/work/users/evezeyl/2025_DPI_TEST/*/*/output*.sqlite .
```

Debbuging using the merging script and container running ... script in utilities `container_python_tests.sh`

-[x] seems to have detected a bug in the file names creation with the inversion of ref and query,
appears to occur in gff already -> need to check that
    - I did not find that in the results, so that might just be the output of the file names for the sqlite ? 
    - yes it seems so - let see how to fix ... ; I have simplified the channel - removing id when when know which one is ref_query
    then rewrote all channels and checked modules input and output to take into account those changes. 

- [ ] bug in passing the list of paths --- hell of debugging - to transform the temp file from nextflow
sed does not work well because its a java nf file, that contains a path to a temp file
the temp file contains the paths as a list of paths separated by comma. 
tried to transform it using groovy in script but it does not find the file because there groovy in script of the process uses the
path at launch ... tried soooo many things
Finish to ask gemini to make a python script to read the temp file and transform it correctly. That appears to work.
Soooo many things tried ... 
path now : /cluster/work/users/evezeyl/2025_DPI_TEST/bd/1d536c9c09c2ba7814bf1fa2415311 where it seems to work 


```bash
myscript="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/utilities/rm_nf_selected_testdir.sh"
bash $myscript 2025*.sqlite
``` 
- [x] done script to help github merging: update dev from main after having merged dev to main. (commands - so do not need to search next time)


# Relaunching Fargelund data
```bash
bash 2025_05_02_Fagerlund_max20_run.sh > 2025_05_02_Fagerlund_max20_run.log
```

date :: 2025-05-05 
- running on big dataset bugged
- [x] fixing allowance of empty query_additional gff 
- [x] simplifying print (so it does not print all the time) - just report in each log. 

- [x] relaunch small test
- [x] relaunch full test
- [x] debugging step by step when failing - checking why -> empty files with eg no variants, no differences


date :: 2025-05-06
- [x] created an asset subdirectory for test files -> see bellow descriptions of test files - will be required for further improvement






# TODO 
 
- [ ] improve the error handling - logic and simplification 


# Test files description
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/assets/test_files

| characteristics test file | name test file | 
| :---- | :---- | 
| VCF : no variant detected - header is present | SRR11262118_SRR11262120_query_snps_annotated.vcf | 
| GFF : empty gff query_additional | ERR2522247_SRR13588145_query_additional.gff | 
| GFF : non empty gff query_additional | SRR11262179_SRR13588387_query_additional.gff |



# Helpers gemini 
Hi, can you make an unittest for this file : xx.py. I want to be able to have the result in a jupyter notebook, your explanations included