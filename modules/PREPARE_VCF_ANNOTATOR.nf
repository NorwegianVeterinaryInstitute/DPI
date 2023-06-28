// corrects fileformat vcf to be able to annotate with vcf-annotator
process PREPARE_VCF_ANNOTATOR {

        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'

        label: 'process_short'
        
        debug "$params.debugme"
        tag "$pair"

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), path(ref_vcf), path(query_vcf)

        output:
        tuple val(pair), val(ref_query), val(ref), val(query), 
        path("${ref_query}_ref_snps_reformated.vcf"), 
        path("${ref_query}_query_snps_reformated.vcf"), emit: prep_vcf_ch

        
        script:
        """
        # version output by default by the script
        python $baseDir/bin/prep_vcf_annotator.py --vcf ${ref_vcf}
        python $baseDir/bin/prep_vcf_annotator.py --vcf ${query_vcf}
        """
}