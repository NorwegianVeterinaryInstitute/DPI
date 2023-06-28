// Adds all results to the database (for all pairs)
process WRANGLING_TO_DB{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        debug "$params.debugme"
        label: 'process_high'
        
        input:
        val(db)
        val(comment)
        path("*")
        path("*") 
        

        output:
        path("*")
        script:
        """
        # version output by default by the script
        python $baseDir/bin/results_to_db.py --database ${db} --comment ${comment}
        """
} 