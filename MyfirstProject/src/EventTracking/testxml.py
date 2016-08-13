tree = ET.fromstring(status_xml_document_output)
                    self.remove_namespace(tree.find("."), u'http://www.tandberg.com/XML/CUIL/2.0')
                    i=0
                    for element in tree.findall("./Time"):
                        i+=1
                        if element.find("./ZoneOlson")!=None:
                            Time_Zone.append((i-1,element.find("./ZoneOlson").text))