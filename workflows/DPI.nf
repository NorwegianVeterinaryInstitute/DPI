include { INPUT; INPUT_VERSION } from "../modules/INPUT.nf"
include { ANNOTATE; ANNOTATE_VERSION } from "../modules/ANNOTATE.nf"
include { PREPARE_NUCDIFF; PREPARE_NUCDIFF_VERSION } from "../modules/PREPARE_NUCDIFF.nf"
include { RUN_NUCDIFF; RUN_NUCDIFF_VERSION } from "../modules/RUN_NUCDIFF.nf"
include { PREPARE_VCF_ANNOTATOR; PREPARE_VCF_ANNOTATOR_VERSION } from "../modules/PREPARE_VCF_ANNOTATOR.nf"
include { RUN_VCF_ANNOTATOR; RUN_VCF_ANNOTATOR_VERSION } from "../modules/RUN_VCF_ANNOTATOR.nf"
include { WRANGLING_TO_DB; WRANGLING_TO_DB_VERSION  } from "../modules/WRANGLING_TO_DB.nf"

workflow DPI {
     
/*         // output sofware versions 
        INPUT_VERSION()
        ANNOTATE_VERSION()
        PREPARE_NUCDIFF_VERSION()
        RUN_NUCDIFF_VERSION()
        PREPARE_VCF_ANNOTATOR_VERSION()
        RUN_VCF_ANNOTATOR_VERSION()
        WRANGLING_TO_DB_VERSION()
        JSON_TO_DB_VERSION() */

        // Workflow 
        if (!params.input) {exit 1, "Missing input file"}
        if (!params.baktaDB) {exit 1, "Missing or wrong path for Bakta database"}
        if (!params.training) {exit 1, "missing or wrong path for prodigal training file"}
        if (!params.genus) {exit 1, "Please indicate genus name in parameters"}
        if (!params.species) { exit 1, "Please indicate species name in parameters"}

        // get the pairs file, check and restructure
        input_channel = Channel.fromPath(params.input, checkIfExists: true)

        INPUT(input_channel)

        
        // creating unique samples list from csv files
        input_samples_ch = INPUT.out.unique_samples_ch
                .splitCsv(header:['sample', 'path'], skip: 1, sep:",", strip:true)
                .map { row -> (sample, path) =  [ row.sample, row.path ]}

        // recreating pairs from sample tags - sorting so its get ordered
        input_unique_pairs_ch = INPUT.out.pairs_ch
                .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
                .map { row -> (pair, sample1, sample2) =  [[row.sample1, row.sample2].sort().join("_"), row.sample1, row.sample2]}
   
        //ANNOTATION for all samples individually 
        ANNOTATE(input_samples_ch, params.baktaDB, params.training, params.genus, params.species)

 
         
        // Combining channels to form pairs - by: [0,2] possition does not error but not sure does the right thing
        // need to swap keys so it can belong - problem if no keys in the first line 
        // need to swap keys again - sample 2 - pair - sample 1  
        // now we need order pairs first - pair - sample 2 - sample 1 
        // last (not necessary but better for comprehension)
        fna_pairs_ch = 
                input_unique_pairs_ch
                .map{it.swap(0,1)} 
                .combine(ANNOTATE.out.bakta_fna_ch, by: 0)
                .map{it.swap(0,2)} 
                .combine(ANNOTATE.out.bakta_fna_ch, by: 0)
                .map{it.swap(0,1)} 
                .map{it.swap(1,2)}

        PREPARE_NUCDIFF(fna_pairs_ch)



        //ref is the longuest of the two - prepare tags 
        //pairs always sorted - so can always match them 
        ref_query_ch = 
                PREPARE_NUCDIFF.out.longest_param_ch
                .splitCsv(header:['ref_query', 'ref', 'query'], skip: 0, sep:",", strip:true)
                .map {row -> (pair, ref_query, ref, query) = [
                [row.ref, row.query].sort().join("_"), row.ref_query, row.ref, row.query]}
                .combine(PREPARE_NUCDIFF.out.fna_ch, by:0)


        RUN_NUCDIFF(ref_query_ch)

        PREPARE_VCF_ANNOTATOR(RUN_NUCDIFF.out.nucdiff_vcf_ch)


        // gbff_pairs order must correspond to ref-query (pair - ref_query - ref - query ) //bakta is (sample, path)
        vcf_annot_ch = 
                PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch
                // first the ref swap 
                .map{it.swap(0,2)} 
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
                // back to origin
                .map{it.swap(0,2)} 
                // now query swap 
                .map{it.swap(0,3)} 
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
                // back to origin
                .map{it.swap(0,3)} 
        
        RUN_VCF_ANNOTATOR(vcf_annot_ch)

        // prepare merging of results to database
        db_path_ch = Channel.fromPath(params.sqlitedb, checkIfExists: false) 
        comment_ch=Channel.value(params.comment) 

        // results must be emited one by one but collected from all other modules from which we need to add them
        // results_ch = ANNOTATE.out.result_todb_ch
        // RUN_NUCDIFF.out.result_todb_ch
        //         .flatMap { value, paths -> paths.collect { path -> [value, path]}}
        //         .view()

        // Better but the stat file is lost 
        RUN_NUCDIFF.out.result_todb_ch
                .flatMap { pair_id, gff_stat_files ->
                        gff_stat_files.collect { gff_stat_file ->
                        tuple(groupKey(pair_id, gff_stat_files.size()), gff_stat_file)
                        }}
                .view(v -> "scattered: ${v}" ) 


        // results_ch = merge(
        //         ANNOTATE.out.result_todb_ch, 
        //         RUN_NUCDIFF.out.result_todb_ch.flatten(),
        //         RUN_VCF_ANNOTATOR.out.result_todb_ch.flatten()
        //         )

        // results_ch.view()

        //WRANGLING_TO_DB(db_path_ch, comment_ch, results_ch)


        // This is run only once at the time to avoid many access to same DB which could be a problem
        //FIXME - rewrite JSON_TO_DB(WRANGLING_TO_DB.out.db_path_ch, ANNOTATE.out.bakta_json_ch) 

        // This was the original
        // WRANGLING_TO_DB(
        //         db_path_ch,
        //         comment_ch, 
        //         RUN_VCF_ANNOTATOR.out.annotated_vcf_ch.flatten().collect(),
        //         RUN_NUCDIFF.out.nucdiff_res_ch.flatten().collect()
        //         )


}
