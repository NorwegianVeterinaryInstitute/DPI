//ADD_EXTERMAL.nf allow to add exteernal data to the database 
include { INPUT_EXTERNAL_CHECK; INPUT_EXTERNAL_CHECK_VERSION } from "../modules/INPUT_EXTERNAL_CHECK.nf"
include { ADD_EXTERNAL; ANNOTATE_VERSION } from "../modules/ADD_EXTERNAL.nf"

workflow ADD_EXTERMAL {
    // SECTION : input check 
    input_external_ch = Channel.fromPath(params.input, checkIfExists: true)
    INPUT_EXTERNAL_CHECK(input_external_channel)
    // !SECTION

    // SECTION : adding external data to the database 
    ADD_EXTERNAL(INPUT_EXTERNAL_CHECK.out.external_ch)
    // !SECTION

    // SECTION : version check
    ADD_EXTERNAL_VERSION()
    // !SECTION
}

