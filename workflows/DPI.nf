include { INPUT; INPUT_VERSION } from "../modules/INPUT.nf"
include { ANNOTATE; ANNOTATE_VERSION } from "../modules/ANNOTATE.nf"
include { PREPARE_NUCDIFF; PREPARE_NUCDIFF_VERSION } from "../modules/PREPARE_NUCDIFF.nf"
include { RUN_NUCDIFF; RUN_NUCDIFF_VERSION } from "../modules/RUN_NUCDIFF.nf"
include { PREPARE_VCF_ANNOTATOR; PREPARE_VCF_ANNOTATOR_VERSION } from "../modules/PREPARE_VCF_ANNOTATOR.nf"
include { RUN_VCF_ANNOTATOR; RUN_VCF_ANNOTATOR_VERSION } from "../modules/RUN_VCF_ANNOTATOR.nf"
include { WRANGLING_TO_DB; WRANGLING_TO_DB_VERSION  } from "../modules/WRANGLING_TO_DB.nf"
include { MERGE_DBS; MERGE_DBS_VERSION } from "../modules/MERGE_DBS.nf"


workflow DPI {
        // SECTION Input parameters check 
        if (!params.input) {exit 1, "Missing input file"}
        if (!params.baktaDB) {exit 1, "Missing or wrong path for Bakta database"}
        if (!params.training) {exit 1, "missing or wrong path for prodigal training file"}
        if (!params.genus) {exit 1, "Please indicate genus name in parameters"}
        if (!params.species) { exit 1, "Please indicate species name in parameters"}
        // !SECTION

        // SECTION : input check 
        input_channel = Channel.fromPath(params.input, checkIfExists: true)
        INPUT(input_channel)
        // !SECTION

        // SECTION : reformating input for annotation and annotation
        // creating unique samples list from csv files
        input_samples_ch = INPUT.out.unique_samples_ch
                .splitCsv(header:['sample', 'path'], skip: 1, sep:",", strip:true)
                .map { row -> (sample, path) =  [ row.sample, row.path ]}

        // recreating pairs from sample tags - sorting so its get ordered
        input_unique_pairs_ch = INPUT.out.pairs_ch
                .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
                .map { row -> (pair, sample1, sample2) =  [[row.sample1, row.sample2].sort().join("_"), row.sample1, row.sample2]}
   
        
        ANNOTATE(input_samples_ch, params.baktaDB, params.training, params.genus, params.species)
        // !SECTION

 
        // SECTION: reforming pairs for pairwise analysis
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
        // !SECTION

        // SECTION : nucdiff for detecting differences
        PREPARE_NUCDIFF(fna_pairs_ch)

        // ref is the longuest of the two - prepare tags 
        // pairs always sorted - so can always match them 
        ref_query_long_ch = 
                PREPARE_NUCDIFF.out.longest_param_ch
                .splitCsv(header:['ref_query', 'ref', 'query'], skip: 0, sep:",", strip:true)
                .map {row -> (pair, ref_query, ref, query) = [
                [row.ref, row.query].sort().join("_"), row.ref_query, row.ref, row.query]}
                .combine(PREPARE_NUCDIFF.out.fna_ch, by:0)
        
        // ref_query_long_ch.view(v -> "ref_query_long: ${v}" )

                
        ref_query_ch = 
                ref_query_long_ch
                .map{it -> (ref_query, ref, query, sample1, path1, sample2, path2 ) = [it[1], it[2], it[3], it[4], it[5], it[6], it[7]]}


        // ref_query_ch.view(v -> "ref_query: ${v}" )
      
        RUN_NUCDIFF(ref_query_ch)
        // RUN_NUCDIFF.out.nucdiff_vcf_ch.view(v -> "nucdiff_vcf: ${v}" )
       
        // !SECTION 
  
        // SECTION: adding annotations to vcf files 
        PREPARE_VCF_ANNOTATOR(RUN_NUCDIFF.out.nucdiff_vcf_ch)
        // PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch.view(v -> "prep_vcf: ${v}" )
   
        
        // gbff_pairs order must correspond to ref-query (ref_query - ref - query ) //bakta is (sample, path)
        vcf_annot_ch = 
                PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch
                // first the ref swap              
                .map{it.swap(0,1)} 
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
                // back to origin
                .map{it.swap(0,1)} 
                // now query swap 
                .map{it.swap(0,2)} 
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
                // back to origin
                .map{it.swap(0,2)} 
        // vcf_annot_ch.view(v -> "vcf_annot: ${v}" )
        
        RUN_VCF_ANNOTATOR(vcf_annot_ch)
        // RUN_VCF_ANNOTATOR.out.result_todb_ch.view(v -> "vcf_annot: ${v}" )
        // !SECTION
        
        // SECTION : wrangle results in sqlite databases 
        comment_ch=Channel.value(params.comment) 

        // results must be emited one by one but collected from all other modules from which we need to add them
        nucdiff_out_ch = RUN_NUCDIFF.out.result_todb_ch
                .flatMap { ref_query, gff_stat_files ->
                        gff_stat_files.collect { gff_stat_file ->
                        tuple(groupKey(ref_query, gff_stat_files.size()), gff_stat_file)
                        }}
        
        // nucdiff_out_ch.view(v -> "scattered: ${v}" ) 
        
        vcf_annot_out_ch = RUN_VCF_ANNOTATOR.out.result_todb_ch
                        .flatMap { ref_query, vcfs ->
                                vcfs.collect { vcf ->
                                tuple(groupKey(ref_query, vcfs.size()), vcf)
                                }}

        // vcf_annot_out_ch.view(v -> "scattered: ${v}" )
        
        // combining all results into one chanel [db_path, comment, id, file] to be inserted into DB (one by one)
        // id can be sample id of the annotated file OR ref_query pair id
        // We need to add index to the channel - to avoid eventual colisions during merging afterwards
        atomicInteger = new java.util.concurrent.atomic.AtomicInteger(0)

        results_ch = 
                comment_ch.combine(
                        ANNOTATE.out.result_todb_ch
                                .concat(nucdiff_out_ch)
                                .concat(vcf_annot_out_ch)
                                )
                .distinct()
                // to make this deterministic (gemini solution )
                .toSortedList { a, b ->
                    // Defensive checks: Ensure a and b are lists/tuples with at least 3 elements
                    // Return 0 (equal) if structure is unexpected to avoid crashing, though ideally the source should be fixed.
                    // cant be because of the structure of the pipeline (would have to find other solution then)
                    if (!(a instanceof List) || a.size() < 3 || !(b instanceof List) || b.size() < 3) return 0

                    // Extract elements safely, converting to String and handling nulls
                    def id_a = a[1]?.toString() ?: ""
                    def id_b = b[1]?.toString() ?: ""
                    def file_a = a[2]?.toString() ?: ""
                    def file_b = b[2]?.toString() ?: ""

                    // Compare IDs first, then file paths if IDs are equal
                    return id_a <=> id_b ?: file_a <=> file_b
                }
                .flatMap() 
                .map { item ->
                def index = atomicInteger.incrementAndGet()
                return tuple(index, item[0], item[1], item[2])
                }
        // results_ch.view(v -> "results: ${v}" )
        // seems that because index are not in the same order then it makes the Wrangling rerun
        // SO: Sort the distinct results to ensure deterministic order before indexing

                

        WRANGLING_TO_DB(results_ch)
    
        // // SECTION : prepare chanel for merging of results to a single database
        db_path_ch = Channel.fromPath(params.sqlitedb, checkIfExists: false) 

        // We need to collect to ensure that all the results are ready to merge
        // Neeed balance ressouces : how many processes will run sequencially 
        // memory and risks to restart in case of failiure. 
        // symlink optimisation : chunks sizes can try between 100-500 

        // Defensive programing?  compute expected number of results and do not start the process if some errors 
        // aqua if some data is missing? because otherwise the whole process of merging ? because then it will 
        // need to try to merge everything so will run for everything again to add only the missing data ... 
        // question of efficency 

        chunked_dbs_ch = WRANGLING_TO_DB.out.individual_sqlite_ch
                .collect() 
                .buffer (size : 50, remainder: true)
      
        // chunked_dbs_ch.view()      
        MERGE_DBS(db_path_ch, chunked_dbs_ch)

        // !SECTION

        // SECTION : output software versions
        INPUT_VERSION()
        ANNOTATE_VERSION()
        PREPARE_NUCDIFF_VERSION()
        RUN_NUCDIFF_VERSION()
        PREPARE_VCF_ANNOTATOR_VERSION()
        RUN_VCF_ANNOTATOR_VERSION()
        WRANGLING_TO_DB_VERSION()
        MERGE_DBS_VERSION()
        // !SECTION
}


