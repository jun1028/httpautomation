# -*- coding: UTF-8 -*-
# package: cfg.XMLConfiguration
'''
@author: Water.Zhang
'''
import os
try:
    import xml.dom.minidom
except:
    print 'import dom.minidom fail'
from log.Log import Log

class XMLConfiguration(object):

    doc = None

    def __init__(self, path):
        self.path = path
        print path
        try:
            self.doc = xml.dom.minidom.parse(path)
        except:
            Log.exception('can not create doc document object')
            print 'system exit'
            os._exit(0)
    
    def appendNode(self, node):
        self.doc.appendChild(node)
        
    def createElement(self, nodeName):
        return self.doc.createElement(nodeName)
    
    def getElementList(self, nodeName):
        return self.doc.getElementsByTagName(nodeName)
    
    def getElementsByTagName(self, element, sectionName):
        return element.getElementsByTagName(sectionName)
  
    #@param node: object 
    # remove child by node
    def removeChildsOfNode(self, node):
        try:
            if node != None:
                nl = node._get_childNodes()
                for n in nl:
                    if n.nodeType == xml.dom.Node.ELEMENT_NODE:
                        node.removeChild(n)
                Log.debug('have successfully removed element')
        except BaseException, e:
            Log.exception(e)
            
    #@param node: object 
    # remove child by node
    def removeTextNodesByNodename(self, nodeName):
        try:
            elementList = self.getElementList(nodeName)
            for element in elementList:
                if element.nodeType == xml.dom.Node.TEXT_NODE:
                    self.doc.removeChild(element)
                    continue
                else:
                    el = element._get_childNodes()
                    for e in el:
                        if e.nodeType == xml.dom.Node.TEXT_NODE:
                            element.removeChild(e)
        except BaseException, e:
            Log.exception(e)
                      
    def removeChildsByElementList(self, parentsnode, elementList):
        for element in elementList:
            parentsnode.removeChild(element)
    
    def removeChildsOfNodeList(self, nodeName):
        elementList = self.getElementList(nodeName)
        for element in elementList:
            self.removeChildsOfNode(element)
            
    def stripNullLine(self):
        for node in self.doc.childNodes:
            if node.nodeType == xml.dom.Node.TEXT_NODE:
                self.doc.removeChild(node)
       
    def set(self, key, value, sectionName):
        elementList = self.doc.getElementsByTagName(sectionName)
        element = elementList[0]
        element.setAttribute(key, value)
    
    def setElement(self, key, value, element):
        if element is not None:
            element.setAttribute(key, value)
        else:
            print 'set fail'
        
    def writeToConfigfile(self, path = ''):
        if path == '':
            path = self.path
        try:
            writer = open(path, 'w')
            self.doc.writexml(writer, indent=" s", newl="\n", encoding = 'UTF-8')
        except IOError, e:
            print 'can not write into xml configuration file'
            os._exit(0)
    
    #@param id: string type 
    def findElementById(self, element, id):
        result = None
        elementList = self.doc.getElementsByTagName(element)
        for element in elementList:
            elementid = element.getAttribute('id')
            if id == elementid:
                result = element
                break
        return result
    
    def existElementOfKey(self, node, nodeName, key, keyvalue):
        result = False
        if node != None:
            try:
                elementList = node.getElementsByTagName(nodeName)
                for element in elementList:
                    value = element.getAttribute(key)
                    if value == keyvalue:
                        result = True
                        break
            except:
                pass
        return result
    
    
