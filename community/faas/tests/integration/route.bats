#!/usr/bin/env bats

source tests/helpers.bash

# Create and save a random 10 char string in a file
RANDOM_FILE="/tmp/${FAAS_ORGANIZATION_ID}-route.txt"
if [[ ! -e ${RANDOM_FILE} ]]; then
    RAND=$(head /dev/urandom | LC_ALL=C tr -dc a-z0-9 | head -c 10)
    echo ${RAND} > ${RANDOM_FILE}
fi

# Set variables based on random string saved in the file
# envsubst requires all variables used in the example/config to be exported
if [[ -e ${RANDOM_FILE} ]]; then
    export RAND=$(cat ${RANDOM_FILE})
    DEPLOYMENT_NAME="${FAAS_PROJECT_NAME}-route"
    CONFIG=".${DEPLOYMENT_NAME}.yaml"
fi

########## HELPER FUNCTIONS ##########

function create_config() {
    echo "Creating ${CONFIG}"
    envsubst < tests/fixtures/configs/route.yaml > ${CONFIG}

    # Replace the router, vpn tunnel and network in the config
    sed -i "s/<YOUR_NETWORK>/network-${RAND}/g" ${CONFIG}
    sed -i "s/<YOUR_VPN_TUNNEL>/vpntunnel-${RAND}/g" ${CONFIG}
}

function delete_config() {
    echo "Deleting ${CONFIG}"
    rm -f ${CONFIG}
}

function setup() {
    # Global setup - this gets executed only once per test file
    if [ ${BATS_TEST_NUMBER} -eq 1 ]; then
        gcloud compute networks create network-${RAND} \
            --project ${FAAS_PROJECT_NAME} \
            --description "integration test ${RAND}" \
            --subnet-mode custom
        gcloud compute networks subnets create subnet-${RAND} \
            --network network-${RAND} \
            --range 10.118.8.0/22 \
            --region us-east1
        gcloud compute routers create router-${RAND} \
            --network network-${RAND} \
            --asn 65001 \
            --region us-east1
        gcloud compute target-vpn-gateways create gateway-${RAND} \
            --network network-${RAND} \
            --region us-east1
        gcloud compute addresses create staticip-${RAND} \
            --region us-east1
        gcloud compute forwarding-rules create esprule-${RAND} \
            --target-vpn-gateway gateway-${RAND} \
            --region us-east1 \
            --ip-protocol "ESP" \
            --address staticip-${RAND}
        gcloud compute forwarding-rules create udp4500rule-${RAND} \
            --target-vpn-gateway gateway-${RAND} \
            --region us-east1 \
            --ip-protocol "UDP" \
            --address staticip-${RAND} \
            --ports 4500
        gcloud compute forwarding-rules create udp500rule-${RAND} \
            --target-vpn-gateway gateway-${RAND} \
            --region us-east1 \
            --ip-protocol "UDP" \
            --address staticip-${RAND} \
            --ports 500
        gcloud compute vpn-tunnels create vpntunnel-${RAND} \
        --peer-address 1.2.3.4 \
        --shared-secret 'superSecretPassw0rd' \
        --target-vpn-gateway gateway-${RAND} \
        --router router-${RAND} \
        --region us-east1
        create_config
    fi

    # Per-test setup steps here
}

function teardown() {
    # Global teardown - this gets executed only once per test file
    if [[ "$BATS_TEST_NUMBER" -eq "${#BATS_TEST_NAMES[@]}" ]]; then
        gcloud compute vpn-tunnels delete vpntunnel-${RAND} --region us-east1 -q
        gcloud compute forwarding-rules delete udp500rule-${RAND} --region us-east1 -q
        gcloud compute forwarding-rules delete udp4500rule-${RAND} --region us-east1 -q
        gcloud compute forwarding-rules delete esprule-${RAND} --region us-east1 -q
        gcloud compute addresses delete staticip-${RAND} --region us-east1 -q
        gcloud compute target-vpn-gateways delete gateway-${RAND} --region us-east1 -q
        gcloud compute routers delete router-${RAND} --region us-east1 -q
        gcloud compute networks subnets delete subnet-1 --region us-east1 -q
        gcloud compute networks delete network-${RAND} --project ${FAAS_PROJECT_NAME} -q
        delete_config
        rm -f ${RANDOM_FILE}
    fi

    # Per-test teardown steps here
}


@test "Creating deployment ${DEPLOYMENT_NAME} from ${CONFIG}" {
  gcloud config set project ${FAAS_PROJECT_NAME}
  gcloud deployment-manager deployments create ${DEPLOYMENT_NAME} --config $CONFIG
}

@test "Verifying resources were created in deployment ${DEPLOYMENT_NAME}" {
  run gcloud compute routes list --filter="name:gateway-route-${RAND} AND priority:40000"
  [ "$status" -eq 0 ]
  [[ "${lines[1]}" =~ "gateway-route-${RAND}" ]]

  run gcloud compute routes list --filter="name:instance-route-${RAND} AND priority:30000"
  [ "$status" -eq 0 ]  
  [[ "${lines[1]}" =~ "instance-route-${RAND}" ]]

  run gcloud compute routes list --filter="(name:ip-route-${RAND} AND priority:20000)"
  [ "$status" -eq 0 ]
  [[ "${lines[1]}" =~ "ip-route-${RAND}" ]]

  run gcloud compute routes list --filter="(name:vpn-tunnel-route-${RAND} AND priority:500)"
  [ "$status" -eq 0 ]
  [[ "${lines[1]}" =~ "vpn-tunnel-route-${RAND}" ]]
}

@test "Deployment Delete" {
  # Delete the deployment
  run gcloud deployment-manager deployments delete $DEPLOYMENT_NAME -q
  [ "$status" -eq 0 ]
}

@test "Verifying resources were deleted in deployment ${DEPLOYMENT_NAME}" {
    run gcloud compute routes list --filter="name:gateway-route-${RAND}"
    [[ ! "$output" =~ "gateway-route-${RAND}" ]]

    run gcloud compute routes list --filter="name:instance-route-${RAND}"
    [[ ! "$output" =~ "instance-route-${RAND}" ]]

    run gcloud compute routes list --filter="name:ip-route-${RAND}"
    [[ ! "$output" =~ "ip-route-${RAND}" ]]

    run gcloud compute routes list --filter="name:vpn-runnel-route-${RAND}"
    [[ ! "$output" =~ "vpn-tunnel-route-${RAND}" ]]
}
