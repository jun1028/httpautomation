
import os
import xml.dom.minidom
from StringIO import StringIO

filename = 'test.xml'
doc = xml.dom.minidom.parse(filename)
nodeList = doc._get_childNodes()
for node in nodeList:
    if node.nodeType == xml.dom.Node.TEXT_NODE:
        doc.removeChild(node)
    
#senarionodelist = doc.getElementsByTagName('scenario')
#doc.createNode('task')
#===============================================================================
# senarioelement = senarionodelist[0]
# print 'senario duration_sec:', senarioelement.getAttribute('duration_sec')
# instancenodelist = doc.getElementsByTagName('instance')
# instanceelement = instancenodelist[0]
# print 'instance case: ', instanceelement.getAttribute('case')
# filenodelist = doc.getElementsByTagName('filelist')
# filenodelistelement = filenodelist[0]
# print 'len', len(filenodelist)
# for elment in filenodelist:
#    elment.parentNode.removeChild(elment)
# print filenodelistelement.getAttribute('id')
# 
# taskNodeList = self.config.getNode('task')
# for elment in taskNodeList:
#    elment.parentNode.removeChild(elment)
# 
# element = doc.createElement('file')
# element.setAttribute('path', 'ffff')
# element.setAttribute('id', '1')
# filenodelistelement.appendChild(element)
# filelist = filenodelistelement.getElementsByTagName('file')
# fileelement = filelist[0]
# print fileelement.getAttribute('path')
# #filenodelistelement.removeChild(fileelement)
# print fileelement.getAttribute('path')
writer = open(filename, 'w')
#===============================================================================
#server_port_element.writexml(writer)
#element.parentNode.removeChild(element)
doc.writexml(writer, indent="    ", newl="\n", encoding = 'UTF-8')
if __name__ == '__main__':
    pass