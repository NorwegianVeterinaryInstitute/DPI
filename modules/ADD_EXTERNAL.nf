// ADD_EXTERMAL.nf allow to add exteernal data to the database

process ADD_EXTERNAL {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'

    debug "${params.debug}"
    label 'process_short'
    maxForks 1

    input:
    path(sqlite_db)
    //path(input_file)

    script:
    output_db = "output_${input_file.getSimpleName()}.sqlite"
    """
    python ${projectDir}/bin/add_external_data.py \\
        --output "${sqlite_db}" \\
        # --database "${output_db}"
    """
}