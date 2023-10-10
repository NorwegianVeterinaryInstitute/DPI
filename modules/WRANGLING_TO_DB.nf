// Adds all results to the database (for all pairs)
process WRANGLING_TO_DB{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        debug "$params.debug"
        label 'process_high'
        
        input:
        val(db)
        val(comment)
        path("*")
        path("*") 
        

        output:
        path("*")
        script:
        """
        python $projectDir/bin/results_to_db.py --database ${db} --comment ${comment}
        """
} 

process WRANGLING_TO_DB_VERSION{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        label 'process_short'        

        output:
        file("*") 

        script:
        """
        python $projectDir/bin/results_to_db.py --version > results_to_db.version
        """
} 
