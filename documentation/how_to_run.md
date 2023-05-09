# How to run DPI

## Test

nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,<docker/singularity/conda> --out_dir <OUTDIR>

Eve Tests:
```bash
# from github
nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,singularity --out_dir nftest

# local test (from directory where DPI is installed)
cd DPI 
nextflow run main.nf -profile test_DPI_local,singularity --out_dir nftest
```
