# How to run DPI

## Test

nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,<docker/singularity/conda> --out_dir <OUTDIR>

Eve Tests:
```bash
nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,singularity --out_dir nftest
```
