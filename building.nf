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
params.comment         = "comments to add to db" 


// temp 
params.out_dir         = "/home/vi2067/Documents/NOSYNC/NF_TEST"
params.prep_nucdiff    = "${SCRIPTDIR}/prep_nucdiff.py" 
params.prep_vcfannot   = "${SCRIPTDIR}/prep_vcf_annotator.py" 
params.results_to_db   = "${SCRIPTDIR}/results_to_db.py" 
params.sqlitedb        = "${params.out_dir}/test.sqlite"

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
        bakta --db $baktaDB --verbose --prodigal-tf $training --prefix $sample1 --locus $sample1 \
        --genus $genus --species $species $path1

        bakta --db $baktaDB --verbose --prodigal-tf $training --prefix $sample2 --locus $sample2 \
        --genus $genus --species $species $path2
        """
}

process PREPARE_NUCDIFF {
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //conda (params.enable_conda ? 'bioconda::chewbbaca=3.1.2' : null) // make install for that
        //container 'evezeyl/py_docker'
        
        // No need to publish execpt for debugging
        // publishDir "${params.out_dir}/PREP_NUCDIFF", mode: 'copy'

        input:
        tuple val(sample1), path(path1), val(sample2), path(path2)
        
        output: 
        path("ref_query_params.csv"), emit: longest_param_ch
        tuple val(sample1), path(path1), val(sample2), path(path2), emit: fna_ch

        script:
        """
        python ${params.prep_nucdiff} --fasta1 $path1 --fasta2 $path2 
        """

} 

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

process PREPARE_VCF_ANNOTATOR {
        
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        //container 'evezeyl/py_docker'

        publishDir "${params.out_dir}/PREP_VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(ref_query), val(ref), val(query)
        tuple path(ref_vcf), path(query_vcf)

        output:
        tuple val(ref_query), val(ref), val(query), emit: ref_query_param_ch
        tuple path("${ref_query}_ref_snps_reformated.vcf"), path("${ref_query}_query_snps_reformated.vcf"), emit: prep_vcf_ch
        
        script:
        """
        python ${params.prep_vcfannot} --vcf ${ref_vcf}
        python ${params.prep_vcfannot} --vcf ${query_vcf}
        """
}

process RUN_VCF_ANNOTATOR{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/vcf-annotator'

        publishDir "${params.out_dir}/VCF_ANNOTATOR", mode: 'copy'

        input:
        tuple val(ref_query), val(ref), val(query)
        tuple path(ref_vcf), path(query_vcf)
        tuple val(sample1), path(path1_gbff), val(sample2), path(path2_gbff)
        
        output:
        tuple val(ref_query), val(ref), val(query), emit: ref_query_param_ch
        tuple path("${ref_query}_ref_snps_annotated.vcf"), path("${ref_query}_query_snps_annotated.vcf"), emit: annotated_vcf_ch

        script:
        if (ref == sample1)
        """
        vcf-annotator ${ref_vcf} ${path1_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${query_vcf} ${path2_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """

        else if (ref == sample2)       
        
        """
        vcf-annotator ${ref_vcf} ${path2_gbff} --output ${ref_query}_ref_snps_annotated.vcf
        vcf-annotator ${query_vcf} ${path1_gbff} --output ${ref_query}_query_snps_annotated.vcf
        """

}
// Here the problem is to make that run for all the results in the same db

process WRANGLING_TO_DB{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        
        input:
        path(db)
        val(comment)
        tuple val(ref_query), val(ref), val(query)
        tuple path("${ref_query}_ref_snps_annotated.vcf"), path("${ref_query}_query_snps_annotated.vcf") //from RUN_VCF_ANNOTATOR.out.annotated_vcf_ch
        tuple path (gff), path(out) // from RUN_NUCDIFF.out.nucdiff_res_ch  
        // so all the files have to be in

        output:
        path(db)
        
        script:
        """
        python ${params.results_to_db} --resdir . --database ${db} --comment ${comment}
        """
}


workflow {
        if (!params.input) {
		exit 1, "Missing input file"
		}
	
	assembly_pair_ch = Channel
        .fromPath(params.input, checkIfExists: true)
        .splitCsv(header:['sample1', 'path1', 'sample2', 'path2'], skip: 1, sep:",", strip:true)
        .map {row -> tuple(row.sample1, file(row.path1), row.sample2, file(row.path2))}


        ANNOTATE(assembly_pair_ch, params.baktaDB, params.training, params.genus, params.species)

        PREPARE_NUCDIFF(ANNOTATE.out.bakta_fna_ch)
        

        // Channel where we know which one is ref and which one is query 
        ref_query_ch = PREPARE_NUCDIFF.out.longest_param_ch
                //.splitCsv(header:['ref_query', 'ref', 'path_ref', 'query', 'path_query'], skip: 0, sep:",", strip:true)
                //.map {row -> tuple(row.ref_query, row.ref, file(row.path_ref), row.query, file(row.path_query))}
                .splitCsv(header:['ref_query', 'ref', 'query'], skip: 0, sep:",", strip:true)
                .map {row -> tuple(row.ref_query, row.ref, row.query)}

        RUN_NUCDIFF(ref_query_ch, PREPARE_NUCDIFF.out.fna_ch)


        PREPARE_VCF_ANNOTATOR(RUN_NUCDIFF.out.ref_query_param_ch, RUN_NUCDIFF.out.nucdiff_vcf_ch)

        ANNOTATE.out.bakta_gbff_ch.view()

        RUN_VCF_ANNOTATOR(
                PREPARE_VCF_ANNOTATOR.out.ref_query_param_ch,
                PREPARE_VCF_ANNOTATOR.out.prep_vcf_ch,
                ANNOTATE.out.bakta_gbff_ch)
        
        db_path=Channel.fromPath(params.sqlitedb, checkIfExists: false)
        comment_ch=Channel.from(params.comment) 


        WRANGLING_TO_DB(db_path, comment_ch, RUN_VCF_ANNOTATOR.out.ref_query_param_ch, RUN_VCF_ANNOTATOR.out.annotated_vcf_ch, RUN_NUCDIFF.out.nucdiff_res_ch)
        }


// need to fix the python script running from db try from: /home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI/work/ed/a8dab97407f16509cc595af27c8176