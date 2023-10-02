include { INPUT; INPUT_VERSION } from "../modules/INPUT.nf"

workflow DPI {
        if (!params.input) {exit 1, "Missing input file"}
        if (!params.baktaDB) {exit 1, "Missing or wrong path for Bakta database"}
        if (!params.training) {exit 1, "missing or wrong path for prodigal training file"}
        if (!params.genus) {exit 1, "Please indicate genus name in parameters"}
        if (!params.species) { exit 1, "Please indicate species name in parameters"}

        // get the pairs file, check and restructure
        input_channel = Channel.fromPath(params.input, checkIfExists: true)

        INPUT(input_channel)

        //INPUT.out.pairs_ch.view()
        //INPUT.out.unique_samples_ch.view()
        
        // creating unique samples list from csv files
        input_samples_ch = INPUT.out.unique_samples_ch
                .splitCsv(header:['sample', 'path'], skip: 1, sep:",", strip:true)
                .map { row -> (sample, path) =  [ row.sample, row.path ]}

        // recreating pairs from sample tags - sorting so its get ordered
        input_unique_pairs_ch = INPUT.out.pairs_ch
                .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
                .map { row -> (pair, sample1, sample2) =  [[row.sample1, row.sample2].sort().join("_"), row.sample1, row.sample2]}
                .view()
        
        //ANNOTATION for all samples individually 
        ANNOTATE(input_samples_ch, params.baktaDB, params.training, params.genus, params.species)

}