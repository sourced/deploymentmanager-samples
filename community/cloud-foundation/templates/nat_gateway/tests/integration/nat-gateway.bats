#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-natgateway.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-natgateway-${RAND}"
    # Deployment names cannot have underscores. Replace with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < templates/nat_gateway/tests/integration/nat-gateway.yaml > "${CONFIG}"
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

@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
}

@test "Verifying resources were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute instances list --filter="name:simple-natgw-${RAND}-gw" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ "$output" =~ "simple-natgw-${RAND}-gw" ]]
}

@test "Verifying external IP created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute addresses list --filter="name:simple-natgw-${RAND}-ip" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ "$output" =~ "simple-natgw-${RAND}-ip" ]]
}

@test "Verifying routes created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute routes list --filter="name:simple-natgw-${RAND}-route" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ "$output" =~ "simple-natgw-${RAND}-route" ]]
}

@test "Verifying firewall rule created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute firewall-rules list --filter="name:simple-natgw-${RAND}-fw" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ "$output" =~ "simple-natgw-${RAND}-fw" ]]
}

@test "Deployment Delete" {
    run gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt

    run gcloud compute instances list --filter="name:simple-natgw-${RAND}-gw" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ ! "$output" =~ "simple-natgw-${RAND}-gw" ]]

    run gcloud compute addresses list --filter="name:simple-natgw-${RAND}-ip" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ ! "$output" =~ "simple-natgw-${RAND}-ip" ]]

    run gcloud compute routes list --filter="name:simple-natgw-${RAND}-route" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ ! "$output" =~ "simple-natgw-${RAND}-route" ]]

    run gcloud compute firewall-rules list --filter="name:simple-natgw-${RAND}-fw" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    echo "$output" >> ~/output.txt
    [[ ! "$output" =~ "simple-natgw-${RAND}-fw" ]]

}
