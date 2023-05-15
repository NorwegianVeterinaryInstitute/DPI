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
        //file("*") // can add if we want all annotations

        script:
        """
        bakta --db $baktaDB --prodigal-tf $training --prefix $sample1 --locus $sample1 \
        --genus $genus --species $species $path1

        bakta --db $baktaDB --prodigal-tf $training --prefix $sample2 --locus $sample2 \
        --genus $genus --species $species $path2
        """
}
