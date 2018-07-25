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
        gcloud compute networks create network-test-${RAND} \
            --project "${FAAS_PROJECT_ID}" \
            --description "integration test ${RAND}" \
            --subnet-mode custom
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        delete_config
        gcloud compute networks delete network-test-${RAND} --project "${FAAS_PROJECT_ID}" -q
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps here
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}" --project "${FAAS_PROJECT_ID}"
}

@test "Verifying resources were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute firewall-rules list --project "${FAAS_PROJECT_ID}"
    [[ "$output" =~ "allow-proxy-from-inside" ]]
    [[ "$output" =~ "allow-dns-from-inside" ]]
}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q --project "${FAAS_PROJECT_ID}"

    run gcloud compute firewall-rules list --project "${FAAS_PROJECT_ID}"
    [[ ! "$output" =~ "allow-proxy-from-inside" ]]
    [[ ! "$output" =~ "allow-dns-from-inside" ]]
}
