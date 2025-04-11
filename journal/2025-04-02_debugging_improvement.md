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
- [ ] optimizing pipeline (involves restructuring the scripts and some modules)
Allow each results to be added to a single database, then merge the results of all sqlite databases into a single database.
The checking of already existing data will then be done during the merging process, because only new data for the single database. 
    - [ ] rewriting of results_to_db.py (simplification, and reformating to better python) + testing
    - [ ] rewriting of process_result_file - simplification (no control of existing data in sqlite) + testing 
    - [ ] changing the workflow and adding merging module into a single database 


Testing the new results_to_db.py (before modifying the process_result_file)
```bash
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/results_to_db.py"

$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --id SRR11262179_SRR11262033 --comment test
$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --id SRR11262179_SRR11262033 --comment test
$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --id SRR11262179_SRR11262033 --comment test
$SCRIPT --result_file SRR11262179_SRR11262033_query_blocks.gff --id SRR11262179_SRR11262033 --comment test
```
- The script results_to_db.py is functionning   

Modifying the process_result_file.py - simpyfying and making more effective
Need also to modify the create_table ... -> to make it work
going back to testing from gff_to_df.py (modified to create a csv files also for testing)

```bash 
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/gff_to_df.py"
$SCRIPT --file_path SRR11262179_SRR11262033_query_blocks.gff
```
ok - this is working so we can test the results_to_db.py script

```bash 
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/create_table.py"
$SCRIPT --table_name test_gff --identifier dummy3 --input_csv SRR11262179_SRR11262033_query_blocks.csv --db_file dummy_test2.sqlite --file_name SRR11262179_SRR11262033_query_blocks.gff
rm *{.csv,.sqlite,.log}
```
ok - this is working so we can test the other files
script for json, updated with main for easier testing of the scrip
```bash 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/02_ANNOTATE/SRR11262033
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/json_to_df.py"
$SCRIPT --input_json SRR11262033.json --identifier dummy
rm *{.csv,.sqlite,.log}
```
- [x] small error in prep_sequences_df in json_to_df when table is incomplete. Need to inspect further ?  
using : $SCRIPT --input_json SRR11262033.json --identifier dummy. Gemini fixed that.

Now adding this to the database for testing

```bash 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/02_ANNOTATE/SRR11262033
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/create_table.py"
$SCRIPT --table_name info --identifier json_info --input_csv dummy_info.csv --db_file dummy_info.sqlite --file_name SRR11262033.json
$SCRIPT --table_name features --identifier json_features --input_csv dummy_features.csv --db_file dummy_features.sqlite --file_name SRR11262033.json
$SCRIPT --table_name sequences --identifier json_sequences --input_csv dummy_sequences.csv --db_file dummy_sequences.sqlite --file_name SRR11262033.json
rm *{.csv,.sqlite,.log}
```
- [x] ? missing data in features, need to add NaN (None in sqlite) to all other columns - handled for all types of data
ok - this is working. 
Now testing stats file - making it as main also to make it easier to test (and reusable)

```bash 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/stats_to_df.py"
$SCRIPT --file_path SRR11262179_SRR11262033_stat.out --identifier stat_file
rm *{.csv,.sqlite,.log}
```

Ok, it should not be a problem to add to database as is same process. I wont test here, will be tested when run test pipeline 

Now same process with vcf files treatment
```bash
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/vcf_to_df.py"
$SCRIPT --file_path SRR11262179_SRR11262033_query_snps.vcf --identifier nucdiff_vcf #nucdiff_vcf simple - working

cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/06_VCF_ANNOTATOR
$SCRIPT --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier vcf_annotator_vcf
```

- ok this is functioning. So now we should try the process results file 

```bash
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/process_result_file.py"
$SCRIPT --help
$SCRIPT --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier SRR11262179_SRR11262033 --db_file process_result_test  --comment test

# this is bugging so testing one level down 
# I need to create the csv file first
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/vcf_to_df.py"
$SCRIPT --help
$SCRIPT --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier SRR11262179_SRR11262033
# OK 

# now I can create the sqlite file
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/create_table.py"
$SCRIPT --help
$SCRIPT --input_csv SRR11262179_SRR11262033_vcf.csv --file_name SRR11262179_SRR11262033_ref_snps_annotated.vcf --db_file create_table.py_vcf.sqlite --table_name  test_SRR11262179_SRR11262033_vcf --identifier SRR11262179_SRR11262033 
# OK so now I can test the process_result_file.py

SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/process_result_file.py"
$SCRIPT --help
$SCRIPT --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier SRR11262179_SRR11262033 --db_file process_result_file.py.sqlite  --comment test
``` 

ok, this worked, do not know why did not modify anything I think. 
- [x] launching test script for getting all the single databases. Ot seems to be running without problems. 


Some few errors, do not appear really systematic unless vcf fies
retrying . keep otherwise this one and try to adapt script
```text
/cluster/work/users/evezeyl/2025_DPI_TEST/e5/fcdf030c333727ab84ca6e6e5444d1/output_37.sqlite
2025-04-10 18:25:33,123 - INFO - Processing SRR11262033_SRR11262179 in SRR11262179_SRR11262033_query_snps_annotated.vcf
Processing file: SRR11262179_SRR11262033_query_snps_annotated.vcf for SRR11262033_SRR11262179
22
vcf_to_df as run for SRR11262179_SRR11262033_query_snps_annotated.vcf
Error processing SRR11262179_SRR11262033_query_snps_annotated.vcf for identifier SRR11262033_SRR11262179: expected str, bytes or os.PathLike object, not Connection
create_or_append_table function has run for SRR11262033_SRR11262179 and filename SRR11262179_SRR11262033_query_snps_annotated.vcf.
Error processing SRR11262179_SRR11262033_query_snps_annotated.vcf for identifier SRR11262033_SRR11262179: expected str, bytes or os.PathLike object, not Connection
create_or_append_table function has run for SRR11262033_SRR11262179 and filename SRR11262179_SRR11262033_query_snps_annotated.vcf.
Processed and inserted: SRR11262179_SRR11262033_query_snps_annotated.vcf for identifier SRR11262033_SRR11262179

```

ok, relaunched and is completed (my guess something buggy with saga, already sometimes did not find previous runs ,,,)

2025-04-11 
- [ ] testing the merging of the sqlite databases. We might still have to many paths ... will see

- first testing if script is working
```bash
# need to get some results and simlink to make it convenient
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/results/test_dir_sqlite
ln -s $USERWORK/2025_DPI_TEST/**/**/output_*.sqlite .

# testing script on those files
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/merge_sqlite_databases.py"
$SCRIPT --help
$SCRIPT --output merging_test.sqlite --input output*.sqlite > merging_test.log 2>&1

srun --account=nn9305k --mem-per-cpu=8G --cpus-per-task=1 --qos=devel --time=1:00:00 --pty bash -i
srun --account=nn9305k --mem-per-cpu=4G --cpus-per-task=4 --time=3:00:00 --pty bash -i

```
- output 17, 33 are empty - so no filename (so why adding does not work as should). In merged table there is only 25 out of 38 where comments are added so this is the ones that really worked and are different
- [x] nextflow find a way to remove all sqlite files / merging db  from cache - so I do not need to restart all 
- No we change the process and output name - so it will work as filter. is faster
- [ ] so we need to add a defencive programming that the sqlite addition make the process exit error status as failed if db is empty - then can find out what is wrong there
    - [x] Added to create table 
    - [ ] Testing that it still work


    - [ ] adding also failure output at the creation of the different df 

Will be better for nf debugging / processing errors. Will make retry the processes 

- [ ] We need to add val to sqlite name, using val - because then it will allow checking which sqlite_output had problems more easily . ... 
```bash
```

# TODO 

- [ ] automatic script to run unittesting 
- [ ] check if the unittest are working and improve them
- [ ] optimization sqlite writing in database - need to have it add data efficiently (at the end because basic functions have to work)
- [ ] check and adjust the log file for the scripts - so its is easy to detect errors and where 

# Helpers gemini 
Hi, can you make an unittest for this file : xx.py. I want to be able to have the result in a jupyter notebook, your explanations included