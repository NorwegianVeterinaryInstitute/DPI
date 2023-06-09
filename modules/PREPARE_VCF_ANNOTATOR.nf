// corrects fileformat vcf to be able to annotate with vcf-annotator
process PREPARE_VCF_ANNOTATOR {
        
        // for testing
        debug true
        tag "$pair"

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), path(ref_vcf), path(query_vcf)

        output:
        tuple val(pair), val(ref_query), val(ref), val(query), 
        path("${ref_query}_ref_snps_reformated.vcf"), 
        path("${ref_query}_query_snps_reformated.vcf"), emit: prep_vcf_ch

        
        script:
        """
        python ${params.prep_vcfannot} --version > prep_vcf_annotator.version
        python ${params.prep_vcfannot} --vcf ${ref_vcf}
        python ${params.prep_vcfannot} --vcf ${query_vcf}
        """
}