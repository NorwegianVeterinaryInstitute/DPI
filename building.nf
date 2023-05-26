nextflow.enable.dsl=2
DPIDIR="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI"
SCRIPTDIR="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI/bin/python/src"

params.input= "${DPIDIR}/assets/data/pairsheet_local.csv"
// Annotation options
//baktaDB         = "/run/media/evezeyl/4T/DATABASES/bakta/db" //cliff
//training    = "/run/media/evezeyl/4T/DATABASES/Listeria_monocytogenes.trn" //cliff
params.baktaDB         = "/mnt/blue/DATA/BIOINFO_LOCAL/bakta_database/db" //work
params.training        = "/mnt/blue/DATA/BIOINFO_LOCAL/Listeria_monocytogenes.trn" //work
params.genus           = "Listeria"
params.species         = "monocytogenes"
params.comment         = "'comments to add to db'" //  


// temp 
params.out_dir         = "/home/vi2067/Documents/NOSYNC/NF_TEST"
params.prep_nucdiff    = "${SCRIPTDIR}/prep_nucdiff.py" 
params.prep_vcfannot   = "${SCRIPTDIR}/prep_vcf_annotator.py" 
params.results_to_db   = "${SCRIPTDIR}/results_to_db.py" 
params.sqlitedb        = "test3.sqlite"

process ANNOTATE {
        debug true
        tag "$pair"
        conda '/home/vi2067/.conda/envs/bakta'

        publishDir "${params.out_dir}/results/ANNOTATE", mode: 'copy'

        input:
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2)
        path baktaDB
        path training
        val genus
        val species

        output:
        tuple val(pair), val(sample1), path("${sample1}.fna"), val(sample2), path("${sample2}.fna"), emit: bakta_fna_ch
        tuple val(pair), val(sample1), path("${sample1}.gbff"), val(sample2), path("${sample2}.gbff"), emit: bakta_gbff_ch
        // file("*") // can add if we want all annotations

        script:
        """
        bakta --db $baktaDB --prodigal-tf $training --prefix $sample1 --locus $sample1 \
        --genus $genus --species $species $path1

        bakta --db $baktaDB --prodigal-tf $training --prefix $sample2 --locus $sample2 \
        --genus $genus --species $species $path2
        """
}

process PREPARE_NUCDIFF {
        debug true
        tag "$pair"
        
        conda '/home/vi2067/.conda/envs/py_test'
        //conda (params.enable_conda ? 'bioconda::chewbbaca=3.1.2' : null) // make install for that
        //container 'evezeyl/py_docker'
        
        // No need to publish execpt for debugging
        publishDir "${params.out_dir}/results/PREP_NUCDIFF", mode: 'copy'

        input:
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2)
        
        output: 
        path("ref_query_params.csv"), emit: longest_param_ch
        tuple val(pair), val(sample1), path(path1), val(sample2), path(path2), emit: fna_ch

        script:
        """
        python ${params.prep_nucdiff} --fasta1 $path1 --fasta2 $path2 
        """

}

process RUN_NUCDIFF{
        // for testing
        debug true
        tag "$pair"
        conda '/home/vi2067/.conda/envs/nucdiff'
        //container ''

        publishDir "${params.out_dir}/results/NUCDIFF", mode: 'copy'

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), 
        val(sample1), path(path1), val(sample2), path(path2)

        output: 
        tuple val(pair), val(ref_query), val(ref), val(query), path("results/${ref_query}_ref_snps.vcf"), path("results/${ref_query}_query_snps.vcf"), emit: nucdiff_vcf_ch 
        tuple path ("results/*.gff"), path("results/*.out"), emit: nucdiff_res_ch

        // we only need the files here 
        //tuple val(pair), val(ref_query), val(ref), val(query), path ("results/*.gff"), path("results/*.out"), emit: nucdiff_res_ch
        //file("*")

        script: 
        if (ref == sample1)
        """
        nucdiff  --vcf yes $path1 $path2 . $ref_query
        """
        else if (ref == sample2)
        """
        nucdiff  --vcf yes $path2 $path1 . $ref_query
        """
        else
        error "Correct ref-query not found"
}

process PREPARE_VCF_ANNOTATOR {
        
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //container 'evezeyl/py_docker'
        tag "$pair"

        publishDir "${params.out_dir}/results/PREP_VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), path(ref_vcf), path(query_vcf)

        output:
        tuple val(pair), val(ref_query), val(ref), val(query), 
        path("${ref_query}_ref_snps_reformated.vcf"), 
        path("${ref_query}_query_snps_reformated.vcf"), emit: prep_vcf_ch

        
        script:
        """
        python ${params.prep_vcfannot} --vcf ${ref_vcf}
        python ${params.prep_vcfannot} --vcf ${query_vcf}
        """
}

// problem here needs to be linked to the proper gff channel using a tag ... to put the correct channels together 

process RUN_VCF_ANNOTATOR{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/vcf-annotator'
        tag "$pair"

        publishDir "${params.out_dir}/results/VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(pair), val(ref_query), val(ref), val(query), path(ref_vcf), path(query_vcf),
        val(sample1), path(path1_gbff), val(sample2), path(path2_gbff)
        
        output:
        tuple path("${ref_query}_ref_snps_annotated.vcf"), 
        path("${ref_query}_query_snps_annotated.vcf"), emit: annotated_vcf_ch

        // we only need the files
        //tuple val(pair), val(ref_query), val(ref), val(query), 
        //path("${ref_query}_ref_snps_annotated.vcf"), 
        //path("${ref_query}_query_snps_annotated.vcf"), emit: annotated_vcf_ch

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

/* process foo {
        debug true
        conda '/home/vi2067/.conda/envs/py_test'

        input:
        val(db)
        val(comment)
        path("*")
        path("*") 

        '''
        echo true
        '''
} */


// working for one sample 
// We need to find a way it works for all pairs 
process WRANGLING_TO_DB{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'

        publishDir "${params.out_dir}/results/DB", mode: 'copy'
        
        input:
        val(db)
        val(comment)
        //path(files, stageAs: "*")
        path("*")
        path("*") 
        
        
        
        //path("${ref_query}_ref_snps_annotated.vcf"), 
        //path("${ref_query}_query_snps_annotated.vcf"),
        //path (gff), path(out) 

        output:
        path("*")
        script:
        """
        python ${params.results_to_db} --database ${db} --comment ${comment}
        """
} 

// for testing for all 

workflow {
        if (!params.input) {
		exit 1, "Missing input file"
		}
	
        // channel: get the sampleID, paths and creates a pair-key (nothing to do with ref used)
	assembly_pair_ch = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        .map { row -> (pair, sample1, path1, sample2, path2) =  [ 
                [row.sample1, row.sample2].sort().join("_"),
                row.sample1, row.path1, row.sample2, row.path2 ]}

        //assembly_pair_ch.view()

        ANNOTATE(assembly_pair_ch, params.baktaDB, params.training, params.genus, params.species)

        //ANNOTATE.out.bakta_fna_ch.view()
        //ANNOTATE.out.bakta_gbff_ch.view()

        PREPARE_NUCDIFF(ANNOTATE.out.bakta_fna_ch)
        

        // recreate the pair tag here, and tags for ref and query:
        // reassociate channel by pair tag 

        ref_query_ch = PREPARE_NUCDIFF.out.longest_param_ch
                .splitCsv(header:['ref_query', 'ref', 'query'], skip: 0, sep:",", strip:true)
                .map {row -> (pair, ref_query, ref, query) = [
                        [row.ref, row.query].sort().join("_"), row.ref_query, row.ref, row.query]}
                .combine(PREPARE_NUCDIFF.out.fna_ch, by:0)

        //ref_query_ch.view()

        RUN_NUCDIFF(ref_query_ch)

        //RUN_NUCDIFF.out.nucdiff_vcf_ch.view()
        //RUN_NUCDIFF.out.nucdiff_res_ch.view()
        
        PREPARE_VCF_ANNOTATOR(RUN_NUCDIFF.out.nucdiff_vcf_ch)

        //PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch.view()       
        //ANNOTATE.out.bakta_gbff_ch.view() 


       // Combine channels
        vcf_annot_ch = PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch
                .combine(ANNOTATE.out.bakta_gbff_ch, by: 0)

        //vcf_annot_ch.view()
        
        RUN_VCF_ANNOTATOR(vcf_annot_ch)

        //RUN_VCF_ANNOTATOR.out.annotated_vcf_ch.view() 
        //RUN_NUCDIFF.out.nucdiff_res_ch.view()


        db_path_ch=Channel.value(params.sqlitedb)
        comment_ch=Channel.value(params.comment) 


/*         foo(db_path_ch, comment_ch,
        RUN_VCF_ANNOTATOR.out.annotated_vcf_ch.flatten().collect(),
        RUN_NUCDIFF.out.nucdiff_res_ch.flatten().collect()
                ) */
        
        WRANGLING_TO_DB(db_path_ch, comment_ch,
        RUN_VCF_ANNOTATOR.out.annotated_vcf_ch.flatten().collect(),
        RUN_NUCDIFF.out.nucdiff_res_ch.flatten().collect()
                )

}

