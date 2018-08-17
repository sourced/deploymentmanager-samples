'''Deployment manager template script to create and delete DNS records in Cloud DNS.'''

def generate_config(context):
    
    resources = []
    dnsTypeProvider = 'gcp-types/dns-v1'

    deploymentname = context.env['deployment']
    zonename = context.properties['zoneName']
    dnsname = context.properties['dnsName']
    
    if dnsname.endswith('.') != True:
        dnsname = dnsname + '.'
    
    for resourceRecordSet in context.properties['resourceRecordSets']:
        recordset_create = {
            'name': '%(deploymentName)s-create' % {'deploymentName': deploymentname} ,
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
            'name': '%(deploymentName)s-delete' % {'deploymentName': deploymentname},
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


