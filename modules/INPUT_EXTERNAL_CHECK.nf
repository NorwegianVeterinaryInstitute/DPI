// INPUT_EXTERNAL.nf allows to check if the input file is valid
process INPUT_EXTERNAL_CHECK {
    conda (params.enable_conda ? './assets/py_test.yml' : null)
    container 'evezeyl/py_test:latest'   
    debug "${params.debug}"
    label 'process_short'

    input:
    path(input_file)


    output:
    path(input_file), emit: external_ch
    path("input_external_check.version"), emit: version_ch
    
    script:
    """
    python ${projectDir}/bin/input_external_check.py \\ 
        --input "${input_file}" \\ 
        --output "${input_file.getSimpleName()}.sqlite" \\ 
        --version > input_external_check.version
    """
}



// INPUT_EXTERNAL_CHECK_VERSION {
//     conda (params.enable_conda ? './assets/py_test.yml' : null)
//     container 'evezeyl/py_test:latest'
    
//     label 'process_short'        
    
//     output:
//     file("*") 
    
//     script:
//     """
//     python ${projectDir}/bin/input_external_check.py --version > input_external_check.version
//     """
// }