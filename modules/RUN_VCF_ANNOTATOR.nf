// Running vcf annotator with the correct sample as reference
process RUN_VCF_ANNOTATOR{

        conda (params.enable_conda ? 'bioconda::vcf-annotator=0.7' : null)
	container 'quay.io/biocontainers/vcf-annotator:0.7--hdfd78af_0'

        debug "$params.debug"
        tag "$pair"

        label 'process_short'

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), path(ref_vcf), path(query_vcf),
        path(ref_gbff), path(query_gbff)
        
        output:
        tuple path("${ref_query}_ref_snps_annotated.vcf"), 
        path("${ref_query}_query_snps_annotated.vcf"), emit: annotated_vcf_ch
        //file("*")

        script:
        """
        vcf-annotator ${ref_vcf} ${ref_gbff} --output ${ref_query}_ref_snps_annotated.vcf >  $ref".sdout" 2>&1 
        vcf-annotator ${query_vcf} ${query_gbff} --output ${ref_query}_query_snps_annotated.vcf > $query".sdout" 2>&1 
        """
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


