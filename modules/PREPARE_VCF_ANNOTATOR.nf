// corrects fileformat vcf to be able to annotate with vcf-annotator
process PREPARE_VCF_ANNOTATOR {
        
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //container 'evezeyl/py_docker'

        publishDir "${params.out_dir}/PREP_VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(ref_query), val(ref), val(query)
        tuple path(ref_vcf), path(query_vcf)

        output:
        tuple val(ref_query), val(ref), val(query), emit: ref_query_param_ch
        tuple path("${ref_query}_ref_snps_reformated.vcf"), path("${ref_query}_query_snps_reformated.vcf"), emit: prep_vcf_ch
        
        script:
        """
        python ${params.prep_vcfannot} --vcf ${ref_vcf}
        python ${params.prep_vcfannot} --vcf ${query_vcf}
        """
}