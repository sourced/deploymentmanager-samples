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
    # Replace underscores in the deployment name with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    envsubst < "templates/managed_instance_group/tests/integration/${TEST_NAME}.yaml" > "${CONFIG}"
}

function delete_config() {
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup; executed once per test file.
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        gcloud compute http-health-checks create "health-${RAND}" --port "80" \
            --request-path "/" --check-interval "5" --timeout "5" \
            --unhealthy-threshold "2" --healthy-threshold "2" \
            --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    fi

    # Per-test setup steps.
}

function teardown() {
    # Global teardown; executed once per test file.
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gcloud compute http-health-checks delete "health-${RAND}" -q \
            --project "${CLOUD_FOUNDATION_PROJECT_ID}"
        rm -f "${RANDOM_FILE}"
        delete_config
    fi

    # Per-test teardown steps.
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
    run gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

@test "Verifying that a zonal intance group was created" {
    run gcloud compute instance-groups managed list \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "zonal-mig-${RAND}" ]]
    [[ "$output" =~ "us-central1-c" ]]
}

@test "Verifying regional instance group properties" {
    run gcloud compute instance-groups managed list "regional-mig-${RAND}-igm" \
        --regions us-central1 --format "yaml(region)" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "us-central1" ]]
}

@test "Verifying zonal instance group properties" {
    run gcloud compute instance-groups managed describe "zonal-mig-${RAND}" \
        --zone us-central1-c --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "baseInstanceName: bin-${RAND}" ]]
    [[ "$output" =~ "instanceGroup/mig-${RAND}" ]]
    [[ "$output" =~ "instanceTemplate/it-${RAND}" ]]
    [[ "$output" =~ "name: http" ]]
    [[ "$output" =~ "port: 80" ]]
}

@test "Verifying autoscaler properties" {
    run gcloud compute instance-groups managed describe "zonal-mig-${RAND}" \
        --zone us-central1-c --format="yaml(autoscaler)"\
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "cpuUtilization:" ]]
    [[ "$output" =~ "utilizationTarget: 0.7" ]]
    [[ "$output" =~ "coolDownPeriodSec: 70" ]]
    [[ "$output" =~ "maxNumReplicas: 2" ]]
    [[ "$output" =~ "minNumReplicas: 1" ]]
    [[ "$output" =~ "name: autoscaler-${RAND}" ]]
}

@test "Verifying instance template properties" {
    run gcloud compute instance-templates describe "it-${RAND}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "name: it-${RAND}" ]]
    [[ "$output" =~ "ubuntu-1804-lts" ]]
    [[ "$output" =~ "networks/default" ]]
}

@test "Deleting deployment" {
    run gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}
