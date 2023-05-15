// Running vcf annotator with the correct sample as reference
process RUN_VCF_ANNOTATOR{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/vcf-annotator'

        publishDir "${params.out_dir}/VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(ref_query), val(ref), val(query)
        tuple path(ref_vcf), path(query_vcf)
        tuple val(sample1), path(path1_gbff), val(sample2), path(path2_gbff)
        
        output:
        tuple val(ref_query), val(ref), val(query), emit: ref_query_param_ch
        tuple path("${ref_query}_ref_snps_annotated.vcf"), path("${ref_query}_query_snps_annotated.vcf"), emit: annotated_vcf_ch

        script:
        if (ref == sample1)
        """
        vcf-annotator ${ref_vcf} ${path1_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${query_vcf} ${path2_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """

        else if (ref == sample2)       
        
        """
        vcf-annotator ${ref_vcf} ${path2_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${query_vcf} ${path1_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """

}