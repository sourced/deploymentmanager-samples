#!/usr/bin/env bats

source tests/helpers.bash

TEST_NAME=$(basename "${BATS_TEST_FILENAME}" | cut -d '.' -f 1)

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-${TEST_NAME}.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${FAAS_PROJECT_ID}-${TEST_NAME}-${RAND}"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi


########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < "tests/fixtures/configs/${TEST_NAME}.yaml" > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        delete_config
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps here
}


########## TESTS ##########

@test "Deploy the project $DEPLOYMENT_NAME" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}"
}

@test "Test project $FAAS_PROJECT_ID was created" {
    run gcloud projects list
    [[ "$output" =~ "${FAAS_PROJECT_ID}-${RAND}" ]]
}

@test "Test activated APIs for project ${FAAS_PROJECT_ID}-${RAND}" {
    run gcloud services list --project "${FAAS_PROJECT_ID}-${RAND}"
    [[ "$output" =~ "compute.googleapis.com" ]]
    [[ "$output" =~ "deploymentmanager.googleapis.com" ]]
    [[ "$output" =~ "pubsub.googleapis.com" ]]

    # ensure storage API is enabled when usageExportBucket is true
    [[ "$output" =~ "storage-component.googleapis.com" ]]
}

@test "Test if usage report export to the bucket was create for project ${FAAS_PROJECT_ID}-${RAND}" {
    run gcloud compute project-info describe --project "${FAAS_PROJECT_ID}-${RAND}" --format="flattened[no-pad](usageExportLocation)"
    [[ "$output" =~ "${FAAS_PROJECT_ID}-${RAND}-usage-export" ]]
}

@test "Test deployment ${DEPLOYMENT_NAME} was deleted" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q

    run gcloud projects list
    [[ ! "$output" =~ "${FAAS_PROJECT_ID}-${RAND}" ]]
}
