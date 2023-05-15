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
	
	// input file: pair of isolate, fasta file paths
	assembly_pair_ch = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        .map {row -> tuple(row.sample1, file(row.path1), row.sample2, file(row.path2))}

	// Annotation with Bakta
    ANNOTATE(assembly_pair_ch, params.baktaDB, params.training, params.genus, params.species)

    // Chose longest as ref - using bakta fna (consistency labelling contigs) - output csv
	PREPARE_NUCDIFF(ANNOTATE.out.bakta_fna_ch)
        

    // Now: channel where we know which one is ref and which one is query 
    ref_query_ch = PREPARE_NUCDIFF.out.longest_param_ch
        .splitCsv(header:['ref_query', 'ref', 'query'], skip: 0, sep:",", strip:true)
        .map {row -> tuple(row.ref_query, row.ref, row.query)}

	// runs nucdiff using longuest assembly as ref
    RUN_NUCDIFF(ref_query_ch, PREPARE_NUCDIFF.out.fna_ch)

	// corrects vcf format for annotation
    PREPARE_VCF_ANNOTATOR(RUN_NUCDIFF.out.ref_query_param_ch, RUN_NUCDIFF.out.nucdiff_vcf_ch)

	// Annotation of vcf files (from nucdiff)
    RUN_VCF_ANNOTATOR(
        PREPARE_VCF_ANNOTATOR.out.ref_query_param_ch,
        PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch,
        ANNOTATE.out.bakta_gbff_ch)
        
    // SQLITe Database file/name for wrangling results
	db_path_ch=Channel.fromPath(params.sqlitedb, checkIfExists: false)

	// PASTE rest when working

	// Comment field to add to database
	comment_ch=Channel.value(params.comment) 
    
	
}