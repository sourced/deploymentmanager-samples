#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-natgatewayha.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-natgatewayha-${RAND}"
    # Deployment names cannot have underscores. Replace with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < templates/nat_gateway/tests/integration/nat_gateway.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        gcloud compute networks create "network-${RAND}" \
            --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
            --description "integration test ${RAND}" \
            --subnet-mode custom
        gcloud compute networks subnets create "subnet-${RAND}" \
            --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
            --network "network-${RAND}" \
            --range 10.0.1.0/24 \
            --region us-east1
        create_config
    fi
    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gcloud compute networks subnets delete "subnet-${RAND}" \
            --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
            --region us-east1 -q
        gcloud compute networks delete "network-${RAND}" \
            --project "${CLOUD_FOUNDATION_PROJECT_ID}" -q
        delete_config
        rm -f "${RANDOM_FILE}"
    fi
    # Per-test teardown steps here
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

@test "Verifying resources were created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute instances list --filter="name:test-nat-gateway-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-gateway-us-east1-b" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-gateway-us-east1-c" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-gateway-us-east1-d" ]]
}

@test "Verifying external IP created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute addresses list --filter="name:test-nat-gateway-${RAND}-ip-external" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-ip-external-us-east1-b" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-ip-external-us-east1-c" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-ip-external-us-east1-d" ]]
}

@test "Verifying internal IP created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute addresses list --filter="name:test-nat-gateway-${RAND}-ip-internal" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]] 
    [[ "$output" =~ "test-nat-gateway-${RAND}-ip-internal-us-east1-b" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-ip-internal-us-east1-c" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-ip-internal-us-east1-d" ]]
}

@test "Verifying routes created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute routes list --filter="name:test-nat-gateway-${RAND}-route" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-route-us-east1-b" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-route-us-east1-c" ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-route-us-east1-d" ]]
}

@test "Verifying firewall rule created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute firewall-rules list \
        --filter="name:test-nat-gateway-${RAND}-healthcheck-firewall" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-nat-gateway-${RAND}-healthcheck-firewall" ]]
}

@test "Deployment Delete" {
    run gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]

    run gcloud compute instances list \
        --filter="name:test-nat-gateway-${RAND}-gw-1-us-east1-b" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-gateway-us-east1-b" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-gateway-us-east1-c" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-gateway-us-east1-d" ]]

    run gcloud compute addresses list \
        --filter="name:test-nat-gateway-${RAND}-ip" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-ip-external-us-east1-b" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-ip-external-us-east1-c" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-ip-external-us-east1-d" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-ip-internal-us-east1-b" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-ip-internal-us-east1-c" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-ip-internal-us-east1-d" ]]

    run gcloud compute routes list \
        --filter="name:test-nat-gateway-${RAND}-route" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-route-us-east1-b" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-route-us-east1-c" ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-route-us-east1-d" ]]

    run gcloud compute firewall-rules list \
        --filter="name:test-nat-gateway-${RAND}-healthcheck-firewall" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "test-nat-gateway-${RAND}-healthcheck-firewall" ]]
}
