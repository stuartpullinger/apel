from apel.db.records import CloudSummaryRecord
from unittest import TestCase

class CloudRecordTest(TestCase):
    '''
    Test case for CloudSummaryRecord
    '''
    
    def setUp(self):
        self._msg1 = '''
SiteName: CESNET
Month: 10
Year: 2011
GlobalUserName: /DC=es/DC=irisgrid/O=cesga/CN=javier-lopez
VO: ops
VOGroup: /ops
VORole: Role=NULL
Status: completed
CloudType: OpenNebula
ImageId: 'scilin6'
EarliestStartTime: 1318840264
LatestStartTime: 1318840264
WallDuration: None
CpuDuration: None
NetworkInbound: 0
NetworkOutbound: 0
Memory: 512
Disk: None
NumberOfVMs: 1
'''
        
        self._values1 = {'SiteName': 'CESNET',
                        'Status': 'completed',
                        'CloudType': 'OpenNebula',
                        'NetworkInbound': 0,
                        'NetworkOutbound': 0,
                        'Memory': 512,
                        'ImageId': '\'scilin6\'',
                        'NumberOfVMs': 1
                        }
        
        
        self.cases = {}
        self.cases[self._msg1] = self._values1

    def test_load_from_msg(self):
        
        for msg in self.cases.keys():
        
            cr = CloudSummaryRecord()
            cr.load_from_msg(msg)
            
            cont = cr._record_content
        
            for key in self.cases[msg].keys():
                self.assertEqual(cont[key], self.cases[msg][key], "%s != %s for key %s" % (cont[key], self.cases[msg][key], key))
        
        
    def test_mandatory_fields(self):
        record = CloudSummaryRecord()
        record.set_field('SiteName', 'MySite')
        record.set_field('Month', 1)
        record.set_field('Year', 2012)
        record.set_field('GlobalUserName', 'me')
        record.set_field('VO', 'myVO')
        record.set_field('VOGroup', 'myVOGroup')
        record.set_field('VORole', 'myVORole')
        record.set_field('Status', 'completed')
        record.set_field('CloudType', 'OpenStack')
        record.set_field('ImageId', 'img-01')
        record.set_field('NumberOfVMs', 1)
        
        try:
            record._check_fields()
        except Exception, e:
            self.fail('_check_fields method failed: %s [%s]' % (str(e), str(type(e))))