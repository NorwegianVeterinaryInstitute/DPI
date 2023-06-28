include { ANNOTATE } from "../modules/ANNOTATE.nf"
include { PREPARE_NUCDIFF } from "../modules/PREPARE_NUCDIFF.nf"
include { RUN_NUCDIFF } from "../modules/RUN_NUCDIFF.nf"
include { PREPARE_VCF_ANNOTATOR } from "../modules/PREPARE_VCF_ANNOTATOR.nf"
include { RUN_VCF_ANNOTATOR } from "../modules/RUN_VCF_ANNOTATOR.nf"
include { WRANGLING_TO_DB  } from "../modules/WRANGLING_TO_DB.nf"


workflow DPI {
        if (!params.input) {
		exit 1, "Missing input file"
		}
        if (!params.baktaDB) {
		exit 1, "Missing or wrong path for Bakta database"
		}
        if (!params.trainingFILE) {
		exit 1, "missing or wrong path for prodigal training file"
		}
        if (!params.genus) {
		exit 1, "Please indicate genus name in parameters"
		}

        if (!params.species) {
		exit 1, "Please indicate species name in parameters"
		}

	
        // channel: get the sampleID, paths and creates a pair-key (nothing to do with ref used)
	assembly_pair_ch = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        .map { row -> (pair, sample1, path1, sample2, path2) =  [ 
                [row.sample1, row.sample2].sort().join("_"),
                row.sample1, row.path1, row.sample2, row.path2 ]}


        ANNOTATE(assembly_pair_ch, params.baktaDB, params.training, params.genus, params.species)

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
	
}