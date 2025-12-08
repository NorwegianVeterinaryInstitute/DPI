// TODO
process DB_SETUP {
    executor 'local'
    cache false // Always run this check to ensure DB is up

    // Bind the run directory so we can see the socket
    containerOptions "-B ${HOME}/pg_run:/var/run/postgresql -B ${HOME}/pg_data:/var/lib/postgresql/data"
    container 'postgres.sif'

    output:
    val true, emit: ready // A signal that downstream processes can wait for

    script:
    """
    # 1. Start the Apptainer instance if it's not already running
    if ! apptainer instance list | grep -q "pg_instance"; then
        echo "Starting PostgreSQL instance..."
        apptainer instance start \
            -B ${HOME}/pg_data:/var/lib/postgresql/data \
            -B ${HOME}/pg_run:/var/run/postgresql \
            postgres.sif \
            pg_instance \
            postgres -D /var/lib/postgresql/data -k /var/run/postgresql
    else
        echo "PostgreSQL instance is already running."
    fi

    # 2. Wait for the DB to actually be ready (socket availability)
    echo "Waiting for PostgreSQL socket..."
    for i in {1..30}; do
        if pg_isready -h /var/run/postgresql; then
            echo "Database is ready."
            break
        fi
        sleep 1
    done

    # 3. Create the Schema (Idempotent: "IF NOT EXISTS")
    # We use the JSONB column 'data' to handle your variable fields
    psql -h /var/run/postgresql -U postgres -d postgres -c "
        CREATE TABLE IF NOT EXISTS pipeline_results (
            id SERIAL PRIMARY KEY,
            sample_id TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT NOW(),
            data JSONB
        );
        
        -- Create an index on the JSON data for fast querying later
        CREATE INDEX IF NOT EXISTS idx_pipeline_results_data ON pipeline_results USING gin (data);
    "
    """
}


// CREATE TABLE pipeline_results (
//     id SERIAL PRIMARY KEY,
//     sample_id TEXT NOT NULL,
//     processed_at TIMESTAMP DEFAULT NOW(),
//     -- The Magic Column: Stores any fields/structure you throw at it
//     data JSONB 
// );

// -- Create an index so you can query the internal JSON fields fast later
// CREATE INDEX idx_data_content ON pipeline_results USING gin (data);