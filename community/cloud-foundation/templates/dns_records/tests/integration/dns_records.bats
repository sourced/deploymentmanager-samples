#!/usr/bin/env bats

source tests/helpers.bash

TEST_NAME=$(basename "${BATS_TEST_FILENAME}" | cut -d '.' -f 1)

# Create a random 10 char string and save to a file
RANDOM_FILE="/tmp/${CLOUD_FOUNDATION_ORGANIZATION_ID}-${TEST_NAME}.txt"
if [[ ! -e "${RANDOM_FILE}" ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > "${RANDOM_FILE}"
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e "${RANDOM_FILE}" ]]; then
    export RAND=$(cat "${RANDOM_FILE}")
    DEPLOYMENT_NAME="${CLOUD_FOUNDATION_PROJECT_ID}-${TEST_NAME}-${RAND}"
    # Replace underscores in the deployment names with dashes.
    DEPLOYMENT_NAME=${DEPLOYMENT_NAME//_/-}
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
    export CLOUDDNS_ZONE_NAME="test-managedzone-${RAND}"
    export CLOUDDNS_DNS_NAME="${RAND}.com."
    export A_RECORD_NAME="www.${CLOUDDNS_DNS_NAME}"
    export AAAA_RECORD_NAME="www.${CLOUDDNS_DNS_NAME}"
    export A_RECORD_IP="192.0.1.1"
    export AAAA_RECORD_IP="1002:db8::8bd:2001"
    export MX_RECORD_NAME="mail.${CLOUDDNS_DNS_NAME}"
    export MX_RECORD="25 smtp.mail.${CLOUDDNS_DNS_NAME}"
    export TXT_RECORD_NAME="txt.${CLOUDDNS_DNS_NAME}"
    export TXT_RECORD="my super awesome text record"
fi


########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < ${BATS_TEST_DIRNAME}/${TEST_NAME}.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this is executed once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        # Create DNS Managed Zone
        gcloud dns managed-zones create --dns-name="${CLOUDDNS_DNS_NAME}" \
            --description="Test managed zone" "${CLOUDDNS_ZONE_NAME}"
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this is executed once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        delete_config
        rm -f "${RANDOM_FILE}"
        # Delete DNS Managed Zone
        echo "Deleting cloud dns managed zone: ${CLOUDDNS_ZONE_NAME}"
        gcloud dns managed-zones delete "${CLOUDDNS_ZONE_NAME}"
    fi

    # Per-test teardown steps here
}


@test "Creating deployment: ${DEPLOYMENT_NAME} from ${CONFIG}" {
    gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" \
        --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

@test "A record: $A_RECORD_NAME is created " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}"  --filter="type=(A)" \
        --format="csv[no-heading](name)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "$A_RECORD_NAME" ]]
}

@test "A Record IP: ${A_RECORD_IP} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(A)" \
        --format="csv[no-heading](DATA)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${A_RECORD_IP}" ]]
}

@test "A Record TTL is set to 20 for : ${A_RECORD_NAME} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(A)" \
        --format="csv[no-heading](TTL)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "20" ]]
}

@test "AAAA Record: ${AAAA_RECORD_NAME} is created " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(AAAA)" \
        --format="csv[no-heading](name)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${AAAA_RECORD_NAME}" ]]
}

@test "AAAA Record IP: ${AAAA_RECORD_IP} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(AAAA)" \
        --format="csv[no-heading](DATA)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${AAAA_RECORD_IP}" ]]
}

@test "AAAA Record TTL is set to 30 for : ${AAAA_RECORD_NAME} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(AAAA)" \
        --format="csv[no-heading](TTL)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "30" ]]
}

@test "MX Record: ${MX_RECORD} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(MX)" \
        --format="csv[no-heading](name)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${MX_RECORD_NAME}" ]]
}

@test "MX Record TTL is set to 300: ${MX_RECORD} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(MX)" \
        --format="csv[no-heading](TTL)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "300" ]]
}

@test "TXT Record: ${TXT_RECORD_NAME} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(TXT)" \
        --format="csv[no-heading](name)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${TXT_RECORD_NAME}" ]]
}

@test "TXT Record has data: ${TXT_RECORD} " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(TXT)" \
        --format="csv[no-heading](DATA)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${TXT_RECORD}" ]]
}

@test "TXT Record TTL is set to 235 for: ${TXT_RECORD} is in rrdatas " {
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(TXT)" \
        --format="csv[no-heading](TTL)"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "235" ]]
}

@test "Deleting deployment: ${DEPLOYMENT_NAME}" {
    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" \
        -q --project "${CLOUD_FOUNDATION_PROJECT_ID}"

    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
        --project "${CLOUD_FOUNDATION_PROJECT_ID}" --format=flattened
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "${A_RECORD_NAME}" ]]
    [[ ! "$output" =~ "${AAAA_RECORD_NAME}" ]]
    [[ ! "$output" =~ "${A_RECORD_IP}" ]]
    [[ ! "$output" =~ "${AAAA_RECORD_IP}" ]]
}

