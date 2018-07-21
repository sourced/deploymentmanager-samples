#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-network.txt"
if [[ ! -e ${RANDOM_FILE} ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > ${RANDOM_FILE}
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e ${RANDOM_FILE} ]]; then
    export RAND=$(cat ${RANDOM_FILE})
    DEPLOYMENT_NAME="${FAAS_PROJECT_NAME}-network"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/network.yaml > ${CONFIG}
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f ${CONFIG}
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
        rm -f ${RANDOM_FILE}
    fi

    # Per-test teardown steps here
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG} --project ${FAAS_PROJECT_NAME}
}

@test "Verifying resources were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute networks list --filter="name:test-network-${RAND}" --project ${FAAS_PROJECT_NAME}
    [[ "$output" =~ "test-network-${RAND}" ]]
}

@test "Verifying subnets were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute networks subnets list --project ${FAAS_PROJECT_NAME}
    [[ "$output" =~ "test-subnetwork-${RAND}-1" ]]
    [[ "$output" =~ "test-subnetwork-${RAND}-2" ]]
}

@test "Deployment Delete" {
    run gcloud deployment-manager deployments delete ${DEPLOYMENT_NAME} -q --project ${FAAS_PROJECT_NAME}
}

@test "Verifying resources were deleted in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute networks list --filter="name:test-network-${RAND}" --project ${FAAS_PROJECT_NAME}
    [[ ! "$output" =~ "test-network-${RAND}" ]]
}

@test "Verifying subnets were deleted in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute networks subnets list --project ${FAAS_PROJECT_NAME}
    [[ ! "$output" =~ "test-subnetwork-${RAND}-1" ]]
    [[ ! "$output" =~ "test-subnetwork-${RAND}-2" ]]
}
