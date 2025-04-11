# !/usr/bin/env bash
DPI_DIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI"
DPI_BIN_DIR="$DPI_DIR/bin"
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
TEST_OUTPUT_BASE=""$TEST_OUTPUT_BASE"
PYTHON_PATH="$DPI_BIN_DIR"

# NOTE : exporting python path do not work inside container 
# NOTE : for testing the correct way and not directly the in bin we need to add bin to python path 



# --- Helper Function ---
# Usage: run_in_container <module_path> <arg1> <arg2> ...
# Example: run_in_container funktions.gff_to_df --file_path ...
# Example: run_in_container merge_sqlite_databases --output ...
run_in_container() {
    local module_path=$1 # e.g., funktions.gff_to_df or merge_sqlite_databases
    shift # Remove module path from arguments

    # --- Optional Debugging Checks ---
    # echo "--- Debugging Checks Inside Container ---"
    # echo "Running as user:"; apptainer exec "$IMG" id
    # echo "Checking __init__.py:"; apptainer exec "$IMG" ls -l "$DPI_BIN_DIR/funktions/__init__.py"
    # echo "Checking funktions dir:"; apptainer exec "$IMG" ls -ld "$DPI_BIN_DIR/funktions/"
    # echo "Checking Python env:"; APPTAINERENV_PYTHONPATH="$DPI_BIN_DIR" apptainer exec "$IMG" python -c "import sys, os; print(f'---> PYTHONPATH env: {os.environ.get(\"PYTHONPATH\")}\n---> sys.path: {sys.path}')"
    # --- End Optional Debugging ---

    echo "--- Running in container: python -m $module_path $@ ---" # <-- Note the echo change

    # Set PYTHONPATH to the directory *containing* the 'funktions' package
    # and 'merge_sqlite_databases.py'. This is DPI_BIN_DIR.
    APPTAINERENV_PYTHONPATH="$DPI_BIN_DIR" apptainer exec "$IMG" \
        python -m "$module_path" "$@" # <-- Use the -m flag

    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "--- ERROR: Command failed with exit code $exit_code ---"
        # Optionally exit the script on error: exit $exit_code
    fi

    echo "-----------------------------------------------------"
}
# --- End Helper Function ---

# SECTION : USAGE IM;PORTANT 
# when in the module 
# Example for gff_to_df.py:
# run_in_container "funktions.gff_to_df" --file_path SRR11262179_SRR11262033_query_blocks.gff

# when is a script above modile 
# Example for merge_sqlite_databases.py (which is directly in bin):
# run_in_container "merge_sqlite_databases" --output test_merging.sqlite --input file1.sqlite file2.sqlite


# SECTION: 1. Testing creation of tables 
echo "SECTION: 1. Testing creation of tables"

# ANCHOR : GFF tables - OK 
cd "$TEST_OUTPUT_BASE/04_NUCDIFF/SRR11262179_SRR11262033"
run_in_container "funktions.gff_to_df" --file_path SRR11262179_SRR11262033_query_blocks.gff

# ANCHOR : vcf tables - OK 
cd "$TEST_OUTPUT_BASE/04_NUCDIFF/SRR11262179_SRR11262033" 
run_in_container "funktions.vcf_to_df" --file_path SRR11262179_SRR11262033_query_snps.vcf --identifier nucdiff_vcf 

cd "$TEST_OUTPUT_BASE/06_VCF_ANNOTATOR" -OK
run_in_container "funktions.vcf_to_df" --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier vcf_annotator_vcf

# ANCHOR : json files - OK
cd "$TEST_OUTPUT_BASE/02_ANNOTATE/SRR11262033"
run_in_container "funktions.json_to_df" --input_json SRR11262033.json --identifier json_test

# ANCHOR : stats - OK
cd "$TEST_OUTPUT_BASE/04_NUCDIFF/SRR11262179_SRR11262033"
run_in_container "funktions.stats_to_df" --file_path SRR11262179_SRR11262033_stat.out --identifier test
# !SECTION




# SECTION : WRAPPERS 
echo "SECTION: 2. WRAPPERS TESTING" 

# NOTE create table - ALL STEPS - OK
cd "$TEST_OUTPUT_BASE/06_VCF_ANNOTATOR" 
# I need to create the csv file first
run_in_container "funktions.vcf_to_df" --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier SRR11262179_SRR11262033
# Then the sqlite database
run_in_container "funktions.create_table" --input_csv SRR11262179_SRR11262033_vcf.csv --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --db_file create_table.py_vcf.sqlite --table_name  test_SRR11262179_SRR11262033_vcf --identifier SRR11262179_SRR11262033 
# This is working, now should work for all 

# NOTE process file - OK
cd "$TEST_OUTPUT_BASE/06_VCF_ANNOTATOR"
run_in_container "funktions.process_result_file" --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier SRR11262179_SRR11262033 --db_file process_result_file.py.sqlite  --comment test

# NOTE merging databses 
# Need to create 2 files for testing - OK
cd "$TEST_OUTPUT_BASE/06_VCF_ANNOTATOR"
run_in_container "funktions.process_result_file" --file_path SRR11262179_SRR11262033_query_snps_annotated.vcf --identifier SRR11262179_SRR11262033 --db_file process_result_file1.py.sqlite  --comment test
run_in_container "funktions.process_result_file" --file_path SRR11262179_SRR13588387_query_snps_annotated.vcf --identifier SRR11262179_SRR13588387 --db_file process_result_file2.py.sqlite  --comment test

# merge_sqlite_databases.py (which is directly in bin):
run_in_container "merge_sqlite_databases" --output test_merging.sqlite --input file1.sqlite file2.sqlite
# !SECTION 

# rm *{.csv,.sqlite,.log}

