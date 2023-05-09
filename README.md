# DPI

A Nextflow pipeline that detects and reports the "Differences between Pairs of Isolates"

Development for the "Ost er ikke Ost Project"

1. Takes a pair of assemblies and annotates assemblies with [bakta](https://github.com/oschwengers/bakta)
2. Choses the longuest assembly in a pair and uses it as a reference (python script)
3. Runs [nucdiff](https://github.com/uio-cels/NucDiff), (based on MUMmer3) to determine the differences between pairs of isolates
4. Wrangles and transform file format
5. Annotates the variants between the pair with [vcf-annotator](https://github.com/rpetit3/vcf-annotator)
6. Wrangles and add all the results in a sqlite database

Minimal functionning.

Under development. Can still require adjustments.

![Current_pipeline](./documentation/development_modular_OEIO.svg)
