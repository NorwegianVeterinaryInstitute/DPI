// Adds all results to the database (for all pairs)
process WRANGLING_TO_DB{
        debug true
        label: 'process_long'
        
        input:
        val(db)
        val(comment)
        path("*")
        path("*") 
        

        output:
        path("*")
        script:
        """
        python ${params.results_to_db} --version > results_to_db.version
        python ${params.results_to_db} --database ${db} --comment ${comment}
        """
} 