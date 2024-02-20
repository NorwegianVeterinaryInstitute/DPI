process ANNOTATE {
        conda (params.enable_conda ? 'bioconda::bakta=1.8.2' : null)
        container 'oschwengers/bakta:v1.8.2'

        label 'process_high_memory'

        debug "${params.debug}"
        tag "${sample}" 

        input:
        tuple val(sample), path(pathx)
        path(baktaDB)
        path(training)
        val(genus)
        val(species)

        output:
        tuple val(sample), path("${sample}/${sample}.fna"), emit: bakta_fna_ch
        tuple val(sample), path("${sample}/${sample}.gbff"), emit: bakta_gbff_ch
        tuple val(sample), path("${sample}/${sample}.json"), emit: bakta_json_ch
        file("*") 

        script:
        """
        mkdir ${sample}
        bakta --db ${baktaDB} --prodigal-tf ${training} --prefix ${sample} --force \
        --locus ${sample} --genus ${genus} --species ${species} ${pathx} > ${sample}/${sample}.sdout 2>&1 
        mv *.* ${sample}
        """
}


process ANNOTATE_VERSION {
        conda (params.enable_conda ? 'bioconda::bakta=1.8.2' : null)
        container 'oschwengers/bakta:v1.8.2'

        label 'process_short'

        output:
        file("*") 

        script:
        
        """
        bakta --version > bakta.version
        """
}