process PREPARE_NUCDIFF {
        debug true
        tag "$pair"

        input:
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2)
        
        output: 
        path("ref_query_params.csv"), emit: longest_param_ch
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2), emit: fna_ch

        script:
        """
        python ${params.prep_nucdiff} --version > prep_nucdiff.version
        python ${params.prep_nucdiff} --fasta1 $path1 --fasta2 $path2 
        """

}