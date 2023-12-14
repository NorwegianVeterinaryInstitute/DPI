// Adds all results to the database (for all pairs)
process JSON_TO_DB{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        debug "$params.debug"
        tag "$sample" 
        label 'process_short'
        
        input:
        path(db)
        tuple val(sample), path(json_path)

        output:
        path("*")
        
        script:
        """
        python $projectDir/bin/json_annot_import.py --json $json_path --database $db --sample_id $sample 
        """
} 

process JSON_TO_DB_VERSION{
        conda (params.enable_conda ? './assets/py_test.yml' : null)
        container 'evezeyl/py_test:latest'
        
        label 'process_short'        

        output:
        file("*") 

        script:
        """
        python $projectDir/bin/json_annot_import.py --version > json_annot_import.version
        """
} 
