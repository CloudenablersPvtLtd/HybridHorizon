from horizon import tables
from wangle.cloud.myclouds.forms import tenantclouds,clouds
from wangle.cloud.addcloud import tables as addcloud_tables
from wangle.cloud.myclouds import tables as myclouds_tables


class CloudObj():
    def __init__(self,id,name,platform,tenantid,endpoint,cloudtype,username):
        self.id = id
        self.name=name
        self.platform = platform
        self.tenantid = tenantid
        self.endpoint = endpoint
        self.cloudtype = cloudtype
        self.username = username

class Obj():
    def __init__(self,id,name):
        self.id = id
        self.name=name

class IndexView(tables.MultiTableView):
    table_classes = (addcloud_tables.AddCloudTable,
                     myclouds_tables.MyCloudsTable)
    template_name = 'wangle/cloud/index.html'

    def has_more_data(self, table):
        return getattr(self, "_more_%s" % table.name, False)

    def get_addcloud_data(self):
        clo = []
        cloud = clouds.objects.all()
        for i in cloud:
            c_obj = Obj(i.id,i.name)
            clo.append(c_obj)
        return clo

    def get_myclouds_data(self):
        obj = tenantclouds.objects(tenantid=self.request.user.tenantid.id)
        clouds = []
       
        for cloud in obj:
            cld_obj = CloudObj(cloud.id,cloud.name,cloud.platform,\
                                cloud.tenantid.name,cloud.cloud_meta['endpoint'],\
                                cloud.cloud_type,cloud.cloud_meta['publickey'])
            clouds.append(cld_obj)
       
        return clouds