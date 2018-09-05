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
    export CLOUD_FOUNDATION_PROJECT_ID=$(echo ${CLOUD_FOUNDATION_PROJECT_ID} | cut -c 1-10)
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-${TEST_NAME}-${RAND}"
    # Replace underscores in the deployment name with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < "templates/project/tests/integration/${TEST_NAME}.yaml" > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup; this is executed once per test file.
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
    fi

    # Per-test setup steps.
}

function teardown() {
    # Global teardown; this is executed once per test file.
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        delete_config
        rm -f "${RANDOM_FILE}"
    fi

    # Per-test teardown steps.
}


########## TESTS ##########

@test "Deploy project $DEPLOYMENT_NAME" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}"
}

@test "Verify that project $CLOUD_FOUNDATION_PROJECT_ID was created" {
    run gcloud projects list
    [[ "$output" =~ "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" ]]
}

@test "Verify that APIs were activated for project ${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" {
    run gcloud services list --project "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}"
    [[ "$output" =~ "compute.googleapis.com" ]]
    [[ "$output" =~ "deploymentmanager.googleapis.com" ]]
    [[ "$output" =~ "pubsub.googleapis.com" ]]

    # Ensure that storage API is enabled if usageExportBucket is "True".
    [[ "$output" =~ "storage-component.googleapis.com" ]]
}

@test "Verify that usage report export to the bucket was created for project ${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" {
    run gcloud compute project-info describe --project "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" \
        --format="flattened[no-pad](usageExportLocation)"
    [[ "$output" =~ "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}-usage-export" ]]
}

@test "Ccheck if ${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" project is a shared vpc host project {
    run gcloud compute shared-vpc organizations list-host-projects "${CLOUD_FOUNDATION_ORGANIZATION_ID}"
    [[ "$output" =~ "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" ]]
}

@test "Check if the default VPC was deleted for project ${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" {
    run gcloud compute networks list --project "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}"
    [[ ! "$output" =~ "default" ]]
}

@test "Check if the default compute engine SA was removed for project" {
    run gcloud iam service-accounts list --project "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}"
    [[ ! "$output" =~ "Compute Engine default service account" ]]
}

@test "Deleting deployment" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q

    run gcloud projects list
    [[ ! "$output" =~ "${CLOUD_FOUNDATION_PROJECT_ID}-${RAND}" ]]
}
