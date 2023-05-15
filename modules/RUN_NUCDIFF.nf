// Runs nucdiff with correct sample as reference (longuest)
process RUN_NUCDIFF{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/nucdiff'
        //container ''

        publishDir "${params.out_dir}/NUCDIFF", mode: 'copy'

        input:
        tuple val(ref_query), val(ref), val(query)
        tuple val(sample1), path(path1), val(sample2), path(path2)

        output: 
        tuple val(ref_query), val(ref), val(query), emit: ref_query_param_ch
        tuple path("results/${ref_query}_ref_snps.vcf"), path("results/${ref_query}_query_snps.vcf"), emit: nucdiff_vcf_ch 
        tuple path ("results/*.gff"), path("results/*.out"), emit: nucdiff_res_ch
        //file("*")

        script: 
        if (ref == sample1)
        """
        nucdiff  --vcf yes ${path1} ${path2} . ${ref_query}
        """
        else if (ref == sample2)
        """
        nucdiff  --vcf yes ${path2} ${path1} . ${ref_query}
        """
}