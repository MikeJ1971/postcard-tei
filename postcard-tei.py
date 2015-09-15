"""
Process postcards for TEI XML for geo-spatial data.

Usage: python postcard-tei [options]

Options:
  -d, --directory         the directory holding the TEI documents
  -o, --output            the output file
  -h, --help              show this help

Examples:
  postcard-tei -d ~/postcards -o ~/data.csv

"""
import sys
import getopt
import os

from xml.sax.handler import ContentHandler, feature_namespaces
from xml.sax import make_parser


class GeoContentHandler(ContentHandler):

    def __init__(self):
        ContentHandler.__init__(self)
        self._charBuffer = []

    tei_ns = "http://www.tei-c.org/ns/1.0"
    inTeiHeader = False
    inRecto = False
    inMessage = False
    inDestination = False
    postcard_id = None
    data = []
    line = []

    def line_item(self, idno, type, geo):
        line = [idno, type]
        geo = ''.join(geo).split(" ")
        self.data.append(line + geo)

    def startElementNS(self, (uri, localname), qname, attrs):
        if uri == self.tei_ns:
            if localname == "teiHeader":
                self.inTeiHeader = True
            elif localname == "geo":
                self._charBuffer = []
            elif localname == "div":
                if attrs.getValue((None, u"type")) == "recto":
                    self.inRecto = True
                if attrs.getValue((None, u"type")) == "message":
                    self.inMessage = True
                if attrs.getValue((None, u"type")) == "destination":
                    self.inDestination = True

    def endElementNS(self, (uri, localname), qname):
        if uri == self.tei_ns:
            if localname == "teiHeader":
                self.inTeiHeader = False
            elif localname == "idno" and self.inTeiHeader:
                self.postcard_id = ''.join(self._charBuffer).strip()
            elif localname == "geo":
                if self.inRecto:
                    self.line_item(self.postcard_id, 'Recto', ''.join(self._charBuffer).strip())
                if self.inMessage:
                    self.line_item(self.postcard_id, 'Message', ''.join(self._charBuffer).strip())
                if self.inDestination:
                    self.line_item(self.postcard_id, 'Destination', ''.join(self._charBuffer).strip())
            elif localname == "TEI":
                print self.postcard_id
                print self.data
            elif localname == "div":
                print "Yes"
                self.inRecto = False
                self.inMessage = False
                self.inDestination = False

            del self._charBuffer[:]

    def characters(self, content):
        self._charBuffer.append(content)


class PostCardTei:

    def __init__(self, source_dir, output_file):
        self.source_dir = source_dir
        self.output_file = output_file

    def process_file(self, full_path):
        handler = GeoContentHandler()
        sax_parser = make_parser()
        sax_parser.setContentHandler(handler)
        sax_parser.setFeature(feature_namespaces, 1)
        data_source = open(full_path, "r")
        sax_parser.parse(data_source)

    def process(self):
        """
        Walk the directory looking for XML files.
        """
        for root, subFolders, files in os.walk(self.source_dir):
            files = [fi for fi in files if fi.endswith(".xml")]
            for name in files:
                self.process_file(os.path.abspath(os.path.join(root, name)))


def usage():
    """
    Display the usage instructions for the script.
    """
    print __doc__


def main():
    """
    Process the command-line arguments of the script.
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:o:h", ["directory", "output", "help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    directory = None
    output = None

    for o, a in opts:
        if o in ("-h", "--help"):
            print usage()
            exit(1)
        if o in ("-d", "--directory"):
            directory = a
        if o in ("-o", "--output"):
            output = a

    # process if an input directory and output directory is specified
    if directory is not None and output is not None:
        PostCardTei(directory, output).process()
    else:
        usage()
        exit(1)


if __name__ == "__main__":
    main()
