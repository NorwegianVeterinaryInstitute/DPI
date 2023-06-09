# Preparation run

1. Prepare csv input file: full paths are required

   | sample1 | path1       | sample2 | path2      |
   | ------- | ----------- | ------- | ---------- |
   | id1     | /...path... | id2     | ...path... |

2. Ensure that there are no quotes in csv input files: (' or "")

# How to run

### directly from github

- [ ] to implement

```bash
nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,singularity --out_dir nftest

nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,<docker/singularity/conda> --out_dir <OUTDIR>
```

### Locally (current):

> inverted chronology

- [ ] Modularisation pipeline
  - [ ] singularity
  - [ ] base configuration
  - [ ] memory configuration
  - [ ] profiles

```
nextflow run main.nf -profile test_DPI_local,singularity --out_dir nftest
```

- [x] This part is working 2023-05-31

```bash
nextflow run building.nf -with-conda true -w  $HOME/Documents/NF_WORK -resume
```

## Enhancement - Solutions to find

- [ ] how to make it take relative paths from input ?
- [ ] avoid doing annotation twice when same sample appear several times. Can also use same procedure for vcf annotator
- [ ] modify nf pipeline bakta (so it need only to be done once for each sample if several pairs contain same sample)
- [ ] see issues (enhancement)
