nextflow.enable.dsl=2
DPIDIR="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI"
SCRIPTDIR="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI/bin/python/src"

params.input= "${DPIDIR}/assets/data/pairsheet_local.csv"
// Annotation options
//baktaDB         = "/run/media/evezeyl/4T/DATABASES/bakta/db" //cliff
//training    = "/run/media/evezeyl/4T/DATABASES/Listeria_monocytogenes.trn" //cliff
params.baktaDB         = "/mnt/blue/DATA/BIOINFO_LOCAL/bakta_database/db" //work
params.training        = "/mnt/blue/DATA/BIOINFO_LOCAL/Listeria_monocytogenes.trn" //work
params.genus           = "Listeria"
params.species         = "monocytogenes"
params.out_dir         = "/home/vi2067/Documents/NOSYNC/NF_TEST"

// temp 
params.prep_nucdiff    = "${SCRIPTDIR}/prep_nucdiff.py" 
params.prep_vcfannot    = "${SCRIPTDIR}/prep_vcf_annotator.py" 


process ANNOTATE {
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/bakta'

        //conda (params.enable_conda ? 'bioconda::chewbbaca=3.1.2' : null)
        // why cannot get full info
        //container 'oschwengers/bakta:v1.7.0'
        //label 'process_local'
        //bakta 1.7.0 add version

        publishDir "${params.out_dir}/ANNOTATE", mode: 'copy'

        input:
        tuple val(sample1), file(path1), val(sample2), file(path2)
        path baktaDB
        path training
        val genus
        val species

        output:
        tuple val(sample1), path("${sample1}.fna"), val(sample2), path("${sample2}.fna"), emit: bakta_fna_ch
        tuple val(sample1), path("${sample1}.gbff"), val(sample2), path("${sample2}.gbff"), emit: bakta_gbff_ch
        //path("*")

        shell:
        """
        bakta --db $baktaDB --verbose --prodigal-tf $training --prefix $sample1 --locus $sample1 \
        --genus $genus --species $species $path1

        bakta --db $baktaDB --verbose --prodigal-tf $training --prefix $sample2 --locus $sample2 \
        --genus $genus --species $species $path2
        """
}

process PREPARE_NUCDIFF {
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //container 'evezeyl/py ??'
        
        // No need to publish
        // publishDir "${params.out_dir}/PREP_NUCDIFF", mode: 'copy'

        input:
        tuple val(sample1), path(path1), val(sample2), path(path2)
        
        output: 
        path("ref_query_params.csv"), emit: longest_param_ch 

        shell:
        """
        python ${params.prep_nucdiff} --fasta1 $path1 --fasta2 $path2 
        """

} 

process RUN_NUCDIFF{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/nucdiff'
        //container ''

        publishDir "${params.out_dir}/NUCDIFF", mode: 'copy'


        input:
        tuple val(ref_query), val(ref), path(ref_bakta_fna), val(query), path(query_bakta_fna)
        // paths
        path ref_bakta_fna
        path query_bakta_fna


        output: 
        tuple val(ref_query), paths("*")
        // all the files we need 


        shell:
        """
        nucdiff  --vcf yes ${ref_bakta_fna} ${query_bakta_fna} . ${ref_query}
        """
}

/* process PREPARE_VCF_ANNOTATOR {
        
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //container 'evezeyl/python ...'

        publishDir "${params.out_dir}/PREP_VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(ref_query), val(ref), path(ref_snp_vcf), path(query_snp_vcf), 
        tuple val(ref), path(ref_gbff), val(query), path(query_gbff) 

        output:
        path("*")
        shell:

        """
        python ${params.prep_vcfannot} --vcf1 ${ref_query}_ref_snps.vcf --vcf2 ${ref_query}_query_snps.vcf --gbff1 ${ref}.gbff --gbff2 ${query}.gbff --outdir . --outdir_script .
        ${ref_query}_ref_snps.vcf  = ref_snp_vcf
        ${ref_query}_query_snps.vcf
        """
} */

/* process RUN_VCF_ANNOTATOR{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/vcf-annotator'
        input:
        // patterns
        val ref_query 
        val ref 
        val query
        // files
        path ref_gbff
        path query_gbff


        output:
        path ref_annotated_vcf
        path query_annotated_vcf

        shell:
        """
        vcf-annotator ${ref_query}_ref_snps_reformated.vcf ${ref_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${ref_query}_query_snps_reformated.vcf ${query_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """
} */


workflow {
        if (!params.input) {
		exit 1, "Missing input file"
		}
	
	assembly_pair_ch = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        .map {row -> tuple(row.sample1, file(row.path1), row.sample2, file(row.path2))}


        ANNOTATE(assembly_pair_ch, params.baktaDB, params.training, params.genus, params.species)
        //ANNOTATE.out.bakta_fna_ch.view()
        //ANNOTATE.out.bakta_gbff_ch.view()

        PREPARE_NUCDIFF(ANNOTATE.out.bakta_fna_ch)

        // Channel where we know which one is ref and which one is query 
        ref_query_ch = PREPARE_NUCDIFF.out.longest_param_ch
                .splitCsv(header:['ref_query', 'ref', 'path_ref', 'query', 'path_query'], skip: 0, sep:",", strip:true)
                .map {row -> tuple(row.ref_query, row.ref, file(row.path_ref), row.query, file(row.path_query))}
                .view()

        //PREPARE_NUCDIFF.out.view()

        }