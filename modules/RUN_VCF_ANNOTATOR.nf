// Running vcf annotator with the correct sample as reference
process RUN_VCF_ANNOTATOR{

        conda (params.enable_conda ? 'bioconda::vcf-annotator=0.7' : null)
	container 'quay.io/biocontainers/vcf-annotator:0.7--hdfd78af_0'

        debug "$params.debugme"
        tag "$pair"

        label 'process_short'

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), path(ref_vcf), path(query_vcf),
        val(sample1), path(path1_gbff), val(sample2), path(path2_gbff)
        
        output:
        tuple path("${ref_query}_ref_snps_annotated.vcf"), 
        path("${ref_query}_query_snps_annotated.vcf"), emit: annotated_vcf_ch
        file("*")

        script:
        if (ref == sample1 && query == sample2)
        """
        vcf-annotator ${ref_vcf} ${path1_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${query_vcf} ${path2_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """

        else if (ref == sample2 && query == sample1)       
        """
        vcf-annotator ${ref_vcf} ${path2_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${query_vcf} ${path1_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """
        else
        error "vcf_annotator: correct ref-query not found"

}


process RUN_VCF_ANNOTATOR_VERSION{

        conda (params.enable_conda ? 'bioconda::vcf-annotator=0.7' : null)
	container 'quay.io/biocontainers/vcf-annotator:0.7--hdfd78af_0'

        label 'process_short'
        
        output:
        file("*")

        script:
        """
        vcf-annotator --version > vcf-annotator.version
        """

}


