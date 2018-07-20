#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-logsink.txt"
if [[ ! -e ${RANDOM_FILE} ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > ${RANDOM_FILE}
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e ${RANDOM_FILE} ]]; then
    export RAND=$(cat ${RANDOM_FILE})
    DEPLOYMENT_NAME="${FAAS_PROJECT_NAME}-logsink"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < examples/logsink.yaml > ${CONFIG}
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f ${CONFIG}
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        gcloud pubsub topics create topic-${RAND}
        gsutil mb -l us-east1 gs://bucket-${RAND}/ 
        bq mk dataset_${RAND}
    fi

  # Per-test setup as per documentation
}

function teardown() {
    Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gsutil rm -r gs://bucket-${RAND}/
        gcloud pubsub topics delete topic-${RAND}
        bq rm -rf dataset_${RAND}
        delete_config
    fi

  # Per-test teardown as per documentation
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG} --project ${FAAS_PROJECT_NAME}
}
@test "Verifying sinks were created each with a different as the destination in deployment ${DEPLOYMENT_NAME}" {
    run gcloud logging sinks list --project ${FAAS_PROJECT_NAME}
    [[ "$output" =~ "logsink-bq-${RAND}" ]]
    [[ "$output" =~ "logsink-pubsub-${RAND}" ]]
    #[[ "$output" =~ "logsink-storage-${RAND}" ]]
}
@test "Deployment Delete" {
    run gcloud deployment-manager deployments delete ${DEPLOYMENT_NAME} -q --project ${FAAS_PROJECT_NAME}
}
@test "Verifying resources were delete in deployment ${DEPLOYMENT_NAME}" {
    run gcloud logging sinks list --project ${FAAS_PROJECT_NAME}
    [[ ! "$output" =~ "logsink-bq-${RAND}" ]]
    [[ ! "$output" =~ "logsink-pubsub-${RAND}" ]]
    [[ ! "$output" =~ "logsink-storage-${RAND}" ]]
}

