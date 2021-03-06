'''
   Copyright (C) 2012 STFC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
   @author: Konrad Jopek
'''


import logging

from apel.db.records.storage import StorageRecord
from apel.db.records.group_attribute import GroupAttributeRecord
from apel.common.datetime_utils import parse_timestamp
from xml_parser import XMLParser, XMLParserException


log = logging.getLogger(__name__)


class StarParser(XMLParser):
    '''
    Parser for Storage Accounting Records
    
    For documentation please visit: 
    https://twiki.cern.ch/twiki/bin/view/EMI/StorageAccounting
    '''
    
    NAMESPACE = "http://eu-emi.eu/namespaces/2011/02/storagerecord"
    
    def get_records(self):
        '''
        Returns list of parsed records from STAR file.
        
        Please notice that this parser _requires_ valid
        structure of XML document, including namespace
        information and prefixes in XML tag (like urf:StorageUsageRecord).
        '''
        records = []
        
        xml_storage_records = self.doc.getElementsByTagNameNS(self.NAMESPACE, 'StorageUsageRecord')

        if len(xml_storage_records) == 0:
            raise XMLParserException('File does not contain StAR records!')

        for xml_storage_record in xml_storage_records:
            # get record and associated attributes
            record, group_attributes = self.parseStarRecord(xml_storage_record)
            # add all of them to the record list
            records.append(record)
            records += group_attributes

        return records
    
    def parseStarRecord(self, xml_storage_record):
        '''
        Parses single entry for Storage Accounting Record.
        The dictionary below contains fields from record and 
        methods to extract them from XML file.
        '''
        
        functions = {
            'RecordId'              : lambda nodes: self.getAttr(nodes['RecordIdentity'][0], 
                                                                 'recordId'),
            'CreateTime'            : lambda nodes: parse_timestamp(
                                                        self.getAttr(nodes['RecordIdentity'][0],
                                                                     'createTime')),
            'StorageSystem'         : lambda nodes: self.getText(
                                                        nodes['StorageSystem'][0].childNodes),
            'Site'                  : lambda nodes: self.getText(
                                                        nodes['Site'][0].childNodes),

            'StorageShare'          : lambda nodes: self.getText(
                                                        nodes['StorageShare'][0].childNodes),
            'StorageMedia'          : lambda nodes: self.getText(
                                                        nodes['StorageMedia'][0].childNodes),
            'StorageClass'          : lambda nodes: self.getText(
                                                        nodes['StorageClass'][0].childNodes),
            'FileCount'             : lambda nodes: self.getText(
                                                        nodes['FileCount'][0].childNodes),
            'DirectoryPath'         : lambda nodes: self.getText(
                                                        nodes['DirectoryPath'][0].childNodes),
            'LocalUser'             : lambda nodes: self.getText(
                                                        nodes['LocalUser'][0].childNodes),
            'LocalGroup'            : lambda nodes: self.getText(
                                                        nodes['LocalGroup'][0].childNodes),
            'UserIdentity'          : lambda nodes: self.getText(
                                                        nodes['UserIdentity'][0].childNodes),
            'Group'                 : lambda nodes: self.getText(
                                                        nodes['Group'][0].childNodes),
            'StartTime'             : lambda nodes: parse_timestamp(self.getText(nodes['StartTime'][0].childNodes)),
            'EndTime'               : lambda nodes: parse_timestamp(self.getText(nodes['EndTime'][0].childNodes)),
            'ResourceCapacityUsed'  : lambda nodes: self.getText(
                nodes['ResourceCapacityUsed'][0].childNodes),
            'LogicalCapacityUsed'   : lambda nodes: self.getText(
                nodes['LogicalCapacityUsed'][0].childNodes),
            'ResourceCapacityAllocated'   : lambda nodes: self.getText(
                nodes['ResourceCapacityAllocated'][0].childNodes)
            }

        # here we copy keys from functions
        # we only want to change 'RecordId' to 'RecordIdentity',
        nodes = {}.fromkeys( map (lambda f: f == 'RecordId' and 'RecordIdentity' or f, 
                                  [S for S in functions]) )
        # nodes = {}.fromkeys(functions.keys())
        data = {}

        for node in nodes:
            # empty list = element have not been found in XML file
            nodes[node] = xml_storage_record.getElementsByTagNameNS(self.NAMESPACE, node)
            
        for field in functions:
            try:
                # if field == 'Group':
                #     data['GroupName'] = functions[field](nodes)
                # else:
                data[field] = functions[field](nodes)
            except (IndexError, KeyError), e:
                log.debug("Failed to get field %s: %s", field, e)

        sr = StorageRecord()
        sr.set_all(data)

        return sr, self.parseGroupAttributes(
                        xml_storage_record.getElementsByTagNameNS(
                                self.NAMESPACE,'GroupAttribute'),
                        sr.get_field('RecordId'))
    
    
    def parseGroupAttributes(self, nodes, star_record_id):
        '''
        Return a list of GroupAttributes associated with StarRecord.
        '''
        ret = []

        for node in nodes:
            group_attr = GroupAttributeRecord()
            group_attr.set_field('StarRecordID', star_record_id)
            attr_type = self.getAttr(node, 'attributeType')
            group_attr.set_field('AttributeType', attr_type)
            attr_value = self.getText(node.childNodes)
            group_attr.set_field('AttributeValue', attr_value)
            ret.append(group_attr)
        
        return ret