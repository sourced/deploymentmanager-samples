#!/usr/bin/env bats

source tests/helpers.bash

# Create a random 10-char string and save it in a file.
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-natgatewayha.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on the random string saved in the file.
# envsubst requires all variables used in the example/config to be exported.
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-natgatewayha-${RAND}"
    # Replace underscores in the deployment name with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < templates/app_engine/tests/integration/app_engine.yaml > "${CONFIG}"
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
        delete_config
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps.
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

# Wait for app to deploy before verifying
sleep 10

@test "Verifying that standard App Engine resource was created in deployment ${DEPLOYMENT_NAME}" {

    run gcloud app versions list --filter="version:test-app-engine-standard-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-app-engine-standard-${RAND}" ]]
}

@test "Verifying that flexible App Engine resource was created in deployment ${DEPLOYMENT_NAME}" {
    run gcloud app versions list --filter="version:test-app-engine-flexible-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-app-engine-flexible-${RAND}" ]]

    run gcloud app instances list --filter="version:test-app-engine-flexible-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-app-engine-flexible-${RAND}" ]]

    run gcloud app versions describe "test-app-engine-flexible-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" \
        --service=default
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "test-app-engine-flexible-${RAND}" ]]
    [[ "$output" =~ "manualScaling:" ]]
    [[ "$output" =~ "instances: 5" ]]
}

@test "Deleting deployment" {
    run gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]

    run gcloud app versions list --filter="version:test-app-engine-standard-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "test-app-engine-standard-${RAND}" ]]
    [[ ! "$output" =~ "test-app-engine-flexible-${RAND}" ]]

    run gcloud app instances list --filter="version:test-app-engine-flexible-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "test-app-engine-flexible-${RAND}" ]]
}
