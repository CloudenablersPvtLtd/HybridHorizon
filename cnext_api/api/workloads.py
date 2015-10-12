'''
Created on 12-Nov-2013

@author: ganesh
'''
import cloud_mongo.trail

def workloads_getcurrent(request):
    try:
        httpInst = httplib2.Http()
        user = Key.objects.get(name=request.user)
        httpInst.add_credentials(user.publickey, cloud_mongo.trail.encode_decode(user.secretkey,"decode"))
        # next rest call
        url='http://services.computenext.com/apiv1.0/workloads/getcurrent?format=json'
        resp, body = httpInst.request(url)
    
        WorkloadId = '"WorkloadId"'
        WorkloadName = '"WorkloadName"'
        NumberOfResourcesInWorkload = '"NumberOfResourcesInWorkload"'
        WorkloadElementDetail = '"WorkloadElementDetail"'
        bodyDict = {}

    # check if request succeeded by checking response code
        if resp.get('status') == '200' and body:
            for i in body.strip('{').strip('}').split(','):
                ilist = i.split(':')
                bodyDict[ilist[0]] = ilist[1].strip('"')
        else:
            bodyDict[WorkloadId] = bodyDict[WorkloadName] = bodyDict[NumberOfResourcesInWorkload] = bodyDict[WorkloadElementDetail] = ''
        currentWorkload = {'WorkloadId':bodyDict[WorkloadId], 'WorkloadName':bodyDict[WorkloadName], 'NumberOfResourcesInWorkload':bodyDict[NumberOfResourcesInWorkload], 'WorkloadElementDetail':bodyDict[WorkloadElementDetail]}
        workload = [currentWorkload]
    except:
        workload = []
    return workload

def workloads_getcurrentdetail(request):
    try:
        httpInst = httplib2.Http()
        user = Key.objects.get(name=request.user)
        httpInst.add_credentials(user.publickey, cloud_mongo.trail.encode_decode(user.secretkey,"decode"))
        
        # next rest call
        url='http://services.computenext.com/apiv1.0/workloads/getcurrentdetail?format=json'
        resp, body = httpInst.request(url)

        WorkloadElementId = '"WorkloadElementId"'
        WorkloadElementName = '"WorkloadElementName"'
        Price = '"Price"'
        Unit = '"Unit"'
        bodyDict = {}
    workloadDetails = []

    # check if request succeeded by checking response code
        if resp.get('status') == '200' and body:
            for i in body.strip('{').strip('}').split('"WorkloadElementDetail":[{')[1].rstrip('"}]}').split('},{'):
                for j in i.split('","'):
                    j = '"' + j.strip('"') + '"'
                    ilist = j.split(':')
                    bodyDict[ilist[0]] = ilist[1].strip('"')
                    print bodyDict
                workloadDetails.append({'WorkloadElementId':bodyDict[WorkloadElementId], 'WorkloadElementName':bodyDict[WorkloadElementName], 'Price':bodyDict[Price], 'Unit':bodyDict[Unit]})
        else:
            bodyDict[WorkloadElementId] = bodyDict[WorkloadElementName] = bodyDict[Price] = bodyDict[Unit] = ''
            workloadDetails.append({'WorkloadElementId':bodyDict[WorkloadElementId], 'WorkloadElementName':bodyDict[WorkloadElementName], 'Price':bodyDict[Price], 'Unit':bodyDict[Unit]})
    except:
        workloadDetails = []
    return workloadDetails

def workloads(request):
    try:
        httpInst = httplib2.Http()
        # next rest call
        url='http://services.computenext.com/apiv1.0/workloads?format=json'
        resp, body = httpInst.request(url)    
    workloads = []

    # check if request succeeded by checking response code
        if resp.get('status') == '200' and body:
            for i in body.strip('[').strip(']').split(','):
        workloads.append({'Name':i, 'Status':'', 'ID':'', 'CreateDate':''})
        else:
            workloads.append({'Name':'', 'Status':'', 'ID':'', 'CreateDate':''})
    except:
        workloads = []
    return workloads