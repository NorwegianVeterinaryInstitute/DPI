

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
2025_test_run.sh
``` 
1. annotating only the samples 
2. check if some results of the samples needed to be added to the database
- json results for samples from annotation need to be added - starting rewriting this

