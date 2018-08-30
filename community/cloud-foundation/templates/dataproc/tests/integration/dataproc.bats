#!/usr/bin/env bats

source tests/helpers.bash

TEST_NAME=$(basename "${BATS_TEST_FILENAME}" | cut -d '.' -f 1)

# Create a random 10-char string and save it in a file.
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-${TEST_NAME}.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on the random string saved in the file.
# envsubst requires all variables used in the example/config to be exported.
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-${TEST_NAME}-${RAND}"
    # Replace underscores with dashes in the deployment name.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

SA_NAME="dataproc-sa-${RAND}"
NETWORK_NAME="test-network-${RAND}"
CLUSTER_NAME="dataproc-cluster-${RAND}"

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < "templates/dataproc/tests/integration/${TEST_NAME}.yaml" > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup; executed once per test file.
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
    fi

    # Per-test setup steps.
}

function teardown() {
    # Global teardown; executed once per test file.
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        rm -f "${RANDOM_FILE}"
        delete_config
    fi

    # Per-test teardown steps.
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

@test "Verifying that ${CLUSTER_NAME} settings are correct" {
     run gcloud dataproc clusters describe "${CLUSTER_NAME}" \
        --format="yaml(config.gceClusterConfig)" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
     [[ "$output" =~ "${NETWORK_NAME}" ]]
     [[ "$output" =~ "${SA_NAME}" ]]
     [[ "$output" =~ "us-central1-a" ]]
     [[ "$output" =~ "test-tag-${RAND}" ]]
}

@test "Verifying that master group settings are correct" {
     run gcloud dataproc clusters describe "${CLUSTER_NAME}" \
        --format="yaml(config.masterConfig)" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
     [[ "$output" =~ "numInstances: 1" ]]
     [[ "$output" =~ "bootDiskSizeGb: 100" ]]
     [[ "$output" =~ "bootDiskType: pd-ssd" ]]
     [[ "$output" =~ "n1-standard-8" ]]
}

@test "Verifying that worker group settings are correct" {
     run gcloud dataproc clusters describe "${CLUSTER_NAME}" \
        --format="yaml(config.workerConfig)" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
     [[ "$output" =~ "numInstances: 2" ]]
     [[ "$output" =~ "n1-standard-4" ]]
     [[ "$output" =~ "bootDiskSizeGb: 500" ]] # Default size
     [[ "$output" =~ "bootDiskType: pd-standard" ]] # Default type
}

@test "Verifying that secondary worker group settings are correct" {
     run gcloud dataproc clusters describe "${CLUSTER_NAME}" \
        --format="yaml(config.secondaryWorkerConfig)" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
     [[ "$output" =~ "numInstances: 1" ]] # Copied from worker node
     [[ "$output" =~ "n1-standard-4" ]] # Copied from worker node
     [[ "$output" =~ "isPreemptible: true" ]]
}

@test "Deleting deployment" {
    run gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}
