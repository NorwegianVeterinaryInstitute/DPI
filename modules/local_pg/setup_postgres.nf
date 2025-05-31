// modules/local_pg/setup_postgres.nf
nextflow.enable.dsl=2
 
process SETUP_POSTGRES {
    
    label 'with_postgres'
    tag "Setup PG at ${pg_instance_path} on port ${pg_port}"
    // Move publishDir "${params.outdir}/logs/setup_postgres", mode: 'copy', overwrite: false, saveAs: { pg_instance_path.name + "_logfile.log" }

    input:
    path pg_instance_path  // This will be the PGDATA directory itself e.g., work/pg_temp_data/some_hash/my_pg_data
    val pg_port

    output:
    tuple val(pg_connection_map), emit: connection_params // Emits a map: [host, port, user, dbname, pgdata]
    path "logfile.log", emit: server_log_file          // Emits the path to the server log file

    script:
    // Define connection parameters as Groovy variables
    // These are accessible for the `val()` output and for interpolation in the shell script block
    def pg_user_val = System.getProperty("user.name") ?: "nextflow_user" // Default if system property is not set
    def pg_host_val = "localhost" // Host for client connections from the same node.
                                  // For pg_hba.conf, '0.0.0.0/0' is used for wider network access.
    def pg_dbname_val = pg_user_val // Default database name, often same as user or 'postgres'

    // Construct the map to be emitted.
    // This map is defined in the Groovy scope of the process.
    pg_connection_map = [
        host:   pg_host_val,
        port:   pg_port,             // pg_port is an input val (Integer)
        user:   pg_user_val,
        dbname: pg_dbname_val,
        pgdata: pg_instance_path.toString() // pg_instance_path is an input path
    ]

    
    // For cross-node access, host should be the actual IP/hostname of this node.
    // Getting it robustly within a generic HPC job can be tricky.
    // '*' for listen_addresses makes PG listen on all interfaces.
    // 'hostname --fqdn' or similar might get the node's name|FQDN.
    // For now, we'll assume clients might use this node's name if not on the same node.
    // If all Nextflow tasks for this subworkflow are forced onto the same node, 'localhost' is fine.
    // Let's default to '*' for listen_addresses and clients will need the correct hostname.
    def effective_host_for_clients = "*" // Placeholder, might need to be actual hostname for clients
                                         // For pg_hba.conf, 0.0.0.0/0 covers all IPv4

    script:    
    """
    set -e
    echo "Initializing PostgreSQL instance in: ${pg_instance_path}"
    echo "Using port: ${pg_port}"
    echo "System user (for initdb): ${pg_user_val}"

    # Ensure the directory exists and is empty (or clean it)
    # Be careful with 'rm -rf' in automated scripts.
    if [ -d "${pg_instance_path}" ]; then
      echo "Warning: PGDATA directory ${pg_instance_path} already exists."
      echo "Attempting to stop any existing server and clean up..."
      pg_ctl -D "${pg_instance_path}" -o "-p ${pg_port}" stop || echo "PG already stopped or directory was not a valid PGDATA."
      rm -rf "${pg_instance_path}/*" # Clean inside, not the dir itself if NF manages the parent
    fi
    mkdir -p "${pg_instance_path}"

    initdb --username=${pg_user_val} --pgdata="${pg_instance_path}" --auth=trust --no-locale --encoding=UTF8

    echo "port = ${pg_port}" >> "${pg_instance_path}/postgresql.conf"
    echo "listen_addresses = '*'" >> "${pg_instance_path}/postgresql.conf"
    # For 'trust' authentication with listen_addresses = '*'
    # you might need to adjust pg_hba.conf if initdb doesn't set it wide enough.
    # 'trust' means it won't ask for a password from allowed hosts.
    # This is generally okay for a temporary, isolated server.
    echo "host    all             all             0.0.0.0/0               trust" >> "${pg_instance_path}/pg_hba.conf"
    echo "host    all             all             ::/0                    trust" >> "${pg_instance_path}/pg_hba.conf"


    pg_ctl -D "${pg_instance_path}" -l "${pg_instance_path}/logfile.log" -o "-p ${pg_port}" start

    echo "PostgreSQL server started. Log: ${pg_instance_path}/logfile.log"


    # Kept temporarily for debugging purposes
    echo "${pg_host_val}" > pg_params_host.txt
    echo "${pg_port}" > pg_params_port.txt
    echo "${pg_user_val}" > pg_params_user.txt
    echo "${pg_dbname_val}" > pg_params_dbname.txt
    echo "${pg_instance_path}" > pg_params_pgdata.txt
    # Copy logfile to current workDir for capture by `path "logfile.log"`    
    cp "${pg_instance_path}/logfile.log" "logfile.log" 
    """
}