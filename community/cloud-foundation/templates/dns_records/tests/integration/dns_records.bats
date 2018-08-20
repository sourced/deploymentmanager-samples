#!/usr/bin/env bats

source tests/helpers.bash

TEST_NAME=$(basename "$0" .bats)

# Create and save a random 10 char string in a file
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
    # Deployment names cannot have underscores. Replace with dashes.
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
	export TXT_RECORD="txt.${CLOUDDNS_DNS_NAME}"

fi


########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < templates/dns_records/tests/integration/dns_records.yaml > "${CONFIG}"
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f "${CONFIG}"
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        create_config
        
        # Create DNS Managed Zone
        gcloud dns managed-zones create --dns-name="${CLOUDDNS_DNS_NAME}" \
			--description="Test managed zone" "${CLOUDDNS_ZONE_NAME}"
	
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        delete_config
        rm -f "${RANDOM_FILE}"
		
        # Delete DNS Managed Zone
        echo "Deleting cloud dns managed zone: ${CLOUDDNS_ZONE_NAME}"
        gcloud dns managed-zones delete "${CLOUDDNS_ZONE_NAME}"
    fi

    # Per-test teardown steps here
}


@test "[$BATS_TEST_NUMBER]: Creating deployment: ${DEPLOYMENT_NAME} from ${CONFIG}" {
    
	gcloud deployment-manager deployments create "${DEPLOYMENT_NAME}" --config "${CONFIG}" --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    [[ "$status" -eq 0 ]]
}

@test "[$BATS_TEST_NUMBER]: A record: $A_RECORD_NAME is created in Deployment ${DEPLOYMENT_NAME}" {

    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
			--project "${CLOUD_FOUNDATION_PROJECT_ID}" \
			--filter="name=($A_RECORD_NAME)" --format=flattened
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "$A_RECORD_NAME" ]]
}

@test "[$BATS_TEST_NUMBER]: A Record IP: ${A_RECORD_IP} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    a_result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
					--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(A)" \
					--format=flattened | grep "${A_RECORD_IP}")
    [[ "$status" -eq 0 ]]
    [[ "$a_result" =~ "${A_RECORD_IP}" ]]
}

@test "[$BATS_TEST_NUMBER]: A Record TTL is set to 20 for : ${A_RECORD_NAME} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
				--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(A)" \
				--format=flattened | grep 20)
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "20" ]]
}

@test "[$BATS_TEST_NUMBER]: AAAA Record: ${AAAA_RECORD_NAME} is created in Deployment ${DEPLOYMENT_NAME}" {
    
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
			--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="name=(${AAAA_RECORD_NAME})"
    [[ "$status" -eq 0 ]]
    [[ "$output" =~ "${AAAA_RECORD_NAME}" ]]
}

@test "[$BATS_TEST_NUMBER]: AAAA Record IP: ${AAAA_RECORD_IP} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
				--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(AAAA)" \
				--format=flattened | grep "${AAAA_RECORD_IP}")
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "${AAAA_RECORD_IP}" ]]
}

@test "[$BATS_TEST_NUMBER]: AAAA Record TTL is set to 30 for : ${AAAA_RECORD_NAME} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
				--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(AAAA)" \
				--format=flattened | grep 30)
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "30" ]]
}

@test "[$BATS_TEST_NUMBER]: MX Record: ${MX_RECORD} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    mxresult=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
					--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(MX)")
    [[ "$status" -eq 0 ]]
    [[ "$mxresult" =~ "${MX_RECORD_NAME}" ]]
}

@test "[$BATS_TEST_NUMBER]: MX Record TTL is set to 300: ${MX_RECORD} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
				--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(MX)" \
				--format=flattened | grep 300)
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "300" ]]
}

@test "[$BATS_TEST_NUMBER]: TXT Record: ${TXT_RECORD} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    run gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" --project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(TXT)"
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "${TXT_RECORD_NAME}" ]]
}

@test "[$BATS_TEST_NUMBER]: TXT Record TTL is set to 235 for: ${TXT_RECORD} is in rrdatas in Deployment ${DEPLOYMENT_NAME}" {
    
    result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}" \
				--project "${CLOUD_FOUNDATION_PROJECT_ID}" --filter="type=(TXT)" \
				--format=flattened | grep 235)
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "235" ]]
}

@test "[$BATS_TEST_NUMBER]: Resolving ${A_RECORD_NAME} with nslookup ..." {
    
    skip "This will be implemented soon"
    $result=$(gcloud dns managed-zones describe ${CLOUDDNS_ZONE_NAME} \
					--format=flattened | grep nameServers | cut -d' ' -f2 | xargs nslookup)
    [[ "$status" -eq 0 ]]
    [[ "$result" =~ "${A_RECORD_IP}" ]]
	$is_refused=$(echo "${result}" | grep --quiet "REFUSED")
    [[ "$status" -eq 0 ]]
}

@test "[$BATS_TEST_NUMBER]: Deleting deployment: ${DEPLOYMENT_NAME}" {

    gcloud deployment-manager deployments delete "${DEPLOYMENT_NAME}" -q --project "${CLOUD_FOUNDATION_PROJECT_ID}"
    result=$(gcloud dns record-sets list --zone="${CLOUDDNS_ZONE_NAME}"  --project "${CLOUD_FOUNDATION_PROJECT_ID}" --format=flattened)
    [[ "$status" -eq 0 ]]
    [[ ! "$output" =~ "${A_RECORD_NAME}" ]]
    [[ ! "$output" =~ "${AAAA_RECORD_NAME}" ]]
    [[ ! "$output" =~ "${A_RECORD_IP}" ]]
    [[ ! "$output" =~ "${AAAA_RECORD_IP}" ]]

}
