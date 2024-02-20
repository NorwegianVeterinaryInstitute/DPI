# Troubleshooting DPI 

## 2022-02-20 
-  some problem with "JSON_TO_DB" process - can be problem with  json_annot_import.py script 

srun --account=nn9305k --mem-per-cpu=16G --cpus-per-task=4 --qos=devel --time=0:59:00 --pty bash -i
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"

apptainer shell $IMG 
cd /cluster/work/users/evezeyl/dpi_test/2a/ed7212ea3a4b51a9f93811cb05811d
python 

> then use test_json_annot_import.py for troubleshooting

