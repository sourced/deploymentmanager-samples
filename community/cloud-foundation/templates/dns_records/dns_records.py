
'''Deployment manager template script to create and delete DNS records in Cloud DNS.'''

def generate_config(context):
    """ Entry point for the deployment resources """

    resources = []
    dnstypeprovider = 'gcp-types/dns-v1'
    zonename = context.properties['zoneName']

    for resource_recordset in context.properties['resourceRecordSets']:
        deployment_name = generate_unique_recordsetname(resource_recordset)
        recordset_create = {
            'name': '%(deploymentName)s-create' % {'deploymentName': deployment_name},
            'action': '%(dnsTypeProvider)s:dns.changes.create' % {
                'dnsTypeProvider': dnstypeprovider},
            'metadata': {
                'runtimePolicy': [
                    'CREATE'
                ]
            },
            'properties': {
                'managedZone': zonename,
                'additions': [
                    resource_recordset
                ]
            },
        }
        recordset_delete = {
            'name': '%(deploymentName)s-delete' % {'deploymentName': deployment_name},
            'action': '%(dnsTypeProvider)s:dns.changes.create' % {
                'dnsTypeProvider': dnstypeprovider},
            'metadata': {
                'runtimePolicy': [
                    'DELETE'
                ]
            },
            'properties': {
                'managedZone': zonename,
                'deletions': [
                    resource_recordset
                ]
            },
        }

        resources.append(recordset_create)
        resources.append(recordset_delete)



    return {'resources': resources}

def generate_unique_recordsetname(resource_recordset):
    """ generates a unique string joined with properties from a resourceRecordset """

    return '%(name)s-%(type)s-%(ttl)s' % {
        'name': resource_recordset['name'],
        'type': resource_recordset['type'].lower(),
        'ttl': resource_recordset['ttl']
    }


def generate_config(context):
    
    resources = []
    dnsTypeProvider = 'gcp-types/dns-v1'

    deploymentname = context.env['deployment']
    zonename = context.properties['zoneName']
    dnsname = context.properties['dnsName']
    
    for resourceRecordSet in context.properties['resourceRecordSets']:
        # Updates will need to match names, create unique name for this RSS
        unqName = GenerateUniqueRecordSetName(resourceRecordSet)
        recordset_create = {
            'name': '%(deploymentName)s-create' % {'deploymentName': unqName} ,
            'action': '%(dnsTypeProvider)s:dns.changes.create' % { 'dnsTypeProvider': dnsTypeProvider },
            'metadata': {
                'runtimePolicy': [
                    'CREATE'
                ]
            },
            'properties': {
                'managedZone': zonename,
                'additions': [
                    resourceRecordSet
                ]
            },
        }
        recordset_delete = {
            'name': '%(deploymentName)s-delete' % {'deploymentName': unqName},
            'action': '%(dnsTypeProvider)s:dns.changes.create' % { 'dnsTypeProvider': dnsTypeProvider },
            'metadata': {
                'runtimePolicy': [
                    'DELETE'
                ]
            },
            'properties': {
                'managedZone': zonename,
                'deletions': [
                    resourceRecordSet
                ]
            },
        }
    
        resources.append(recordset_create)
        resources.append(recordset_delete)



    return {'resources': resources}

def GenerateUniqueRecordSetName(resourceRecordSet):
    return '%(name)s-%(type)s-%(ttl)s' % {
       'name': resourceRecordSet['name'],
       'type': resourceRecordSet['type'].lower(),
       'ttl': resourceRecordSet['ttl']
    }


