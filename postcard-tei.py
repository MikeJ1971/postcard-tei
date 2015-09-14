from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import make_parser
import sys


class GeoContentHandler(ContentHandler):

    def startElementNS(self, (uri, localname), qname, attrs):
        print("startElement '" + uri + " " + localname + "'")


handler = GeoContentHandler()
sax_parser = make_parser()
sax_parser.setContentHandler(handler)
sax_parser.setFeature(feature_namespaces, 1)

data_source = open("postcard.xml", "r")
sax_parser.parse(data_source)