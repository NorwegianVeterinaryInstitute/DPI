process ANNOTATE {
        debug true
        tag "$pair" 

        label 'process_long'

        input:
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2)
        path baktaDB
        path training
        val genus
        val species

        output:
        tuple val(pair), val(sample1), path("${sample1}.fna"), val(sample2), path("${sample2}.fna"), emit: bakta_fna_ch
        tuple val(pair), val(sample1), path("${sample1}.gbff"), val(sample2), path("${sample2}.gbff"), emit: bakta_gbff_ch
        file("*") 

        script:
        """
        bakta --version > bakta.version

        bakta --db $baktaDB --prodigal-tf $training --prefix $sample1 --locus $sample1 \
        --genus $genus --species $species $path1

        bakta --db $baktaDB --prodigal-tf $training --prefix $sample2 --locus $sample2 \
        --genus $genus --species $species $path2
        """
}