#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-iamcustomrole.txt"
if [[ ! -e ${RANDOM_FILE} ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > ${RANDOM_FILE}
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e ${RANDOM_FILE} ]]; then
    export RAND=$(cat ${RANDOM_FILE})
    DEPLOYMENT_NAME="${FAAS_PROJECT_NAME}-iamcustomrole"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/iam_custom_role.yaml > ${CONFIG}
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
  gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config ${CONFIG} --project ${FAAS_PROJECT_NAME}
}

@test "Verifying project iam roles were created in deployment ${DEPLOYMENT_NAME}" {
  run gcloud iam roles list --project ${FAAS_PROJECT_NAME} --filter="name:myCustomProjectRole${RAND}"
  [ "$status" -eq 0 ]
  [[ "${lines[1]}" = "description: My Project Role Description" ]]
  [[ "${lines[3]}" = "name: projects/${FAAS_PROJECT_NAME}/roles/myCustomProjectRole${RAND}" ]]
  [[ "${lines[4]}" = "stage: GA" ]]
  [[ "${lines[5]}" = "title: My Project Role Title" ]]
}

@test "Verifying organization iam roles were created in deployment ${DEPLOYMENT_NAME}" {
  run gcloud iam roles list --organization ${FAAS_ORGANIZATION_ID} --filter="name:myCustomOrgRole${RAND}"
  [ "$status" -eq 0 ]
  [[ "${lines[1]}" = "description: My Org Role Description" ]]
  [[ "${lines[3]}" = "name: organizations/${FAAS_ORGANIZATION_ID}/roles/myCustomOrgRole${RAND}" ]]
  [[ "${lines[4]}" = "stage: GA" ]]
  [[ "${lines[5]}" = "title: My Org Role Title" ]]
}

@test "Deployment Delete" {
    gcloud deployment-manager deployments delete ${DEPLOYMENT_NAME} -q --project ${FAAS_PROJECT_NAME}
}
