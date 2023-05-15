// adds all the results to database
process WRANGLING_TO_DB{
        // for testing
        debug true
        conda '/home/vi2067/.conda/envs/py_test'
        
        input:
        path(db)
        val(comment)
        tuple val(ref_query), val(ref), val(query)
        tuple path("${ref_query}_ref_snps_annotated.vcf"), path("${ref_query}_query_snps_annotated.vcf") 
        tuple path (gff), path(out) 

        output:
        path(db)
        
        script:
        """
        python ${params.results_to_db} --database "${db}" --comment "${comment}"
        """
}