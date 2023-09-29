include { INPUT; INPUT_VERSION } from "../modules/INPUT.nf"
include { ANNOTATE; ANNOTATE_VERSION } from "../modules/ANNOTATE.nf"
include { PREPARE_NUCDIFF; PREPARE_NUCDIFF_VERSION } from "../modules/PREPARE_NUCDIFF.nf"
include { RUN_NUCDIFF; RUN_NUCDIFF_VERSION } from "../modules/RUN_NUCDIFF.nf"
include { PREPARE_VCF_ANNOTATOR; PREPARE_VCF_ANNOTATOR_VERSION } from "../modules/PREPARE_VCF_ANNOTATOR.nf"
include { RUN_VCF_ANNOTATOR; RUN_VCF_ANNOTATOR_VERSION } from "../modules/RUN_VCF_ANNOTATOR.nf"
include { WRANGLING_TO_DB; WRANGLING_TO_DB_VERSION  } from "../modules/WRANGLING_TO_DB.nf"

workflow DPI {
        if (!params.input) {exit 1, "Missing input file"}
        if (!params.baktaDB) {exit 1, "Missing or wrong path for Bakta database"}
        if (!params.training) {exit 1, "missing or wrong path for prodigal training file"}
        if (!params.genus) {exit 1, "Please indicate genus name in parameters"}
        if (!params.species) { exit 1, "Please indicate species name in parameters"}

	//OUPUT VERSIONS THAT MUST BE RUN
        //INPUT_VERSION()
        //ANNOTATE_VERSION()
        //PREPARE_NUCDIF_VERSION()
        //RUN_NUCDIFF_VERSION()
        //PREPARE_VCF_ANNOTATOR_VERSION()
        //RUN_VCF_ANNOTATOR_VERSION()
        //WRANGLING_TO_DB_VERSION()


        // channel: get the sampleID, paths and creates a pair-key (nothing to do with ref used)
	// assembly_pair_ch = Channel
        // .fromPath(params.input, checkIfExists: true)
        // .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        // .map { row -> (pair, sample1, path1, sample2, path2) =  [ 
        //         [row.sample1, row.sample2].sort().join("_"),
        //         row.sample1, row.path1, row.sample2, row.path2 ]}

        // INPUT 
        input_channel = Channel.fromPath(params.input, checkIfExists: true)

        INPUT(input_channel)

        // ANNOTATION for all samples individually 
        // ANNOTATE(INPUT.out.unique_samples_ch, params.baktaDB, params.training, params.genus, params.species)

        // Reconstitution of pairs info      
        assembly_pair_ch =  INPUT.out.pairs_ch
                .splitCsv(header:['sample1', 'path1', 'sample2', 'path2', 'pair'], skip: 1, sep:",", strip:true)
                .map { row -> (pair, sample1, sample2) =  [[row.pair, row.sample1, row.sample2]}

        assembly_pair_ch.view()

        // Reconstitution of pairs of annotated samples 

        /* Pipeline running       
        PREPARE_NUCDIFF(ANNOTATE.out.bakta_fna_ch)

        ref_query_ch = PREPARE_NUCDIFF.out.longest_param_ch
                .splitCsv(header:['ref_query', 'ref', 'query'], skip: 0, sep:",", strip:true)
                .map {row -> (pair, ref_query, ref, query) = [
                        [row.ref, row.query].sort().join("_"), row.ref_query, row.ref, row.query]}
                .combine(PREPARE_NUCDIFF.out.fna_ch, by:0)

        RUN_NUCDIFF(ref_query_ch)
        
        PREPARE_VCF_ANNOTATOR(RUN_NUCDIFF.out.nucdiff_vcf_ch)

       // Combine channels
        vcf_annot_ch = PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)
        
        RUN_VCF_ANNOTATOR(vcf_annot_ch)

        db_path_ch=Channel.value(params.sqlitedb)
        comment_ch=Channel.value(params.comment) 

        WRANGLING_TO_DB(db_path_ch, comment_ch,
        RUN_VCF_ANNOTATOR.out.annotated_vcf_ch.flatten().collect(),
        RUN_NUCDIFF.out.nucdiff_res_ch.flatten().collect()
                )
        */
	
}