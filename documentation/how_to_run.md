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



nextflow run building.nf -with-conda true -w  $HOME/Documents/NF_WORK -resume
nextflow run building.nf -with-conda true -resume
# this part need to fix does not work yet


```

## Preparation run

1. Remove any quotes in csv input files: (' or "")

## Solutions to find

- [ ] how to make it take relative paths from input ?
- [ ]

## Solutions to find for eventual improvement

- [ ] avoid doing annotation twice when same sample appear several times. Can also use same procedure for vcf annotator
-
