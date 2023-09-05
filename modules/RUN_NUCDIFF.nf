// Runs nucdiff with correct sample as reference (longuest)
process RUN_NUCDIFF{
        conda (params.enable_conda ? 'bioconda::nucdiff=2.0.3' : null)
	container 'evezeyl/nucdiff:latest'
        container 'quay.io/biocontainers/nucdiff:2.0.3--pyh864c0ab_1'

        label 'process_high'

        debug "$params.debugme"
        tag "$pair"

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), 
        val(sample1), path(path1), val(sample2), path(path2)

        output: 
        tuple val(pair), val(ref_query), val(ref), val(query), path("results/${ref_query}_ref_snps.vcf"), path("results/${ref_query}_query_snps.vcf"), emit: nucdiff_vcf_ch 
        tuple path ("results/*.gff"), path("results/*.out"), emit: nucdiff_res_ch
        file("*")

        script: 
        if (ref == sample1)
        """
        nucdiff --version > nucdiff.version
        nucdiff  --vcf yes $path1 $path2 . $ref_query
        """
        else if (ref == sample2)
        """
        nucdiff --version > nucdiff.version
        nucdiff  --vcf yes $path2 $path1 . $ref_query
        """
        else
        error "Correct ref-query not found"
}