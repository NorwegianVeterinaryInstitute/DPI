<!-- following håkons wiki ... need to finish then we can put in wiki -->

# Home

Later !

# 1. Pipeline and program description

- [ ] do

# 2. Installation

# 3. Input and usage

## Input

1. Prepare csv input file: full paths are required

   | sample1 | path1       | sample2 | path2      |
   | ------- | ----------- | ------- | ---------- |
   | id1     | /...path... | id2     | ...path... |

2. Ensure that there are no quotes in csv input files: (' or "")

## Usage

### directly from github

- [ ] to test / implement

```bash
nextflow run NorwegianVeterinaryInstitute/DPI -profile test_DPI,<docker/singularity/conda/apptainer> --out_dir  <OUTDIR>
```

### Other

```bash
nextflow run /path/to/DPI/main.nf -c <your_config> --track DPI \
--input "/path/to/input.csv" -profile <docker/singularity/conda/apptainer> \
--out_dir  <OUTDIR> -work-dir <dirname>
```

[]NB: Saga users must look here]()

<!-- planned more track so ...-->

## Parameter description

`-- input`   Input csv file
`--track DPI`
`--baktaDB`         Path to bakta DB (ends with db)
`--training`        Path to prodigal training file for bakta
`--genus`           Genus (eg. "Listeria")
`--species`         Species (eg. "monocytogenes")
`--comment`         Comment that will be added into results database. If spaces format as eg. "'My comment'" 
`--sqlitedb`        Name of the sqlite databse containing your results that will be created (eg."out.sqlite")
`--debugme`         Option to run modules in debug mode (default: false)
`--time_multiplier`    (defaut 1). If increased to 2, doubles the time requested by the system for each process

# 4. Configuration

<!.. see Alppaca ... same !>

# 5. Output files

## Output file descriptions

-todo

# 6. Contributions and support

<!.. see Alppaca ... same !>

# 7. SAGA Users

DPI is located here on SAGA: `/cluster/projects/nn9305k/vi_src/DPI`
The principle of running is the same as for [ALPPACA](https://github.com/NorwegianVeterinaryInstitute/ALPPACA), as the design has been calqued to this pipeline 

To use it you will require: 
1. Loading Java
2. Using an appropriate version of nextflow (tested with version 23.04.1) 
3. Providing the configuration file for saga 
4. The default nextflow config (NFCONFIG). The parameters you can specify with the command line are mentionned in this file.


Example of paths: 
```bash 
NEXTFLOW="/cluster/projects/nn9305k/bin/nextflow_23.04.1"
SAGA_CONFIG="/cluster/projects/nn9305k/nextflow/configs/saga_new.config"
DPI="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI"
NFCONFIG="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI/nextflow.config"

INPUT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/single_test.csv"
OUTDIR="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/TEST_DPI/TEST"
BAKTADB="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/bakta/db"
PRODIGAL="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/databases/Listeria_monocytogenes.trn"

```

```bash
module purge
module load Java/17.0.4
$NEXTFLOW run $DPI/main.nf -c $SAGA_CONFIG --track DPI -profile apptainer  \
--input $INPUT --out_dir $OUTDIR -work-dir $USERWORK/DPI \
--baktaDB $BAKTADB --training $PRODIGAL --genus "Listeria" --species "monocytogenes" --sqlitedb "test.sqlite" -resume


```

Or by defining all the parameters that are definied in the nextflow configuration file manually. Here is an example: 

```bash
module load Java/17.0.4



```


<!--
Testing purpose only

```bash
nextflow run $DPI -c $SAGA_CONFIG --track DPI
-profile apptainer --out_dir  <OUTDIR> -work-dir <dirname>
```

## Profiles

Singularity has been decomissioned. The profile to use is `apptainer`

Make sure that this has been added to your `~/.bashrc` file:

```bash
export NXF_SINGULARITY_CACHEDIR=${USERWORK}/images
export SINGULARITY_CACHEDIR=${USERWORK}/images
export NXF_APPTAINER_CACHEDIR=${USERWORK}/images
export APPTAINER_CACHEDIR=${USERWORK}/images
```

# Relics Eve to do ....

## Enhancement - Solutions to find

Test local
cd /home/evfi/Documents/TEMP_GITS/DPI

nextflow run main.nf --track DPI -profile test_work_local,conda --out_dir NFTEST

nextflow run main.nf -c nextflow.config -profile singularity \
--track DPI \
--input /home/evfi/Documents/TEMP_GITS/DPI/assets/data/singlepair_local.csv \
--baktaDB /run/media/evfi/4T/DATABASES/bakta/db \
--training /run/media/evfi/4T/DATABASES/Listeria_monocytogenes.trn \
--genus Listeria \
--species monocytogenes --out_dir NFTEST

 --resume

- [ ] how to make it take relative paths from input ?
- [ ] avoid doing annotation twice when same sample appear several times. Can also use same procedure for vcf annotator
- [ ] modify nf pipeline bakta (so it need only to be done once for each sample if several pairs contain same sample)
- [ ] see issues (enhancement)
--> 