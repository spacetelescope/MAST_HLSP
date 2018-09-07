try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


class CAOMKeywordBox(QComboBox):
    """ Create a QComboBox populated with valid CAOM parameter choices.
    Distinguish between keywords already modified by code and those not
    currently in use.  Assign each to a default XML parent.
    """

    def __init__(self):
        super().__init__()
        self.setEditable(True)

        # Set up the dictionaries
        self.inuse = {"algorithm": "metadataList",
                      "aperture_radius": "metadataList",
                      "collection": "metadataList",
                      "instrument_keywords": "metadataList",
                      "instrument_name": "metadataList",
                      "intent": "metadataList",
                      "name": "provenance",
                      "observationID": "metadataList",
                      "project": "provenance",
                      "targetPosition_coordinates_cval1": "metadataList",
                      "targetPosition_coordinates_cval2": "metadataList",
                      "targetPosition_coordsys": "metadataList",
                      "targetPosition_equinox": "metadataList",
                      "target_name": "metadataList",
                      "telescope_name": "metadataList",
                      "type": "metadataList",
                      "version": "provenance"
                      }
        self.unused = {"dataRelease": "provenance",
                       "lastExecuted": "provenance",
                       "metaRelease": "metadataList",
                       "producer": "provenance",
                       "proposal_id": "provenance",
                       "proposal_pi": "provenance",
                       "proposal_title": "provenance",
                       "reference": "provenance",
                       "runID": "metadataList",
                       "sequenceNumber": "metadataList",
                       "target_keywords": "metadataList",
                       "target_moving": "metadataList",
                       "target_type": "metadataList"
                       }

        # Create a merged dictionary
        self.allvalues = dict(self.inuse)
        self.allvalues.update(self.unused)

        # Use a QFont object to distinguish category seperators
        font = QFont()
        font.setBold(True)

        # Put unused parameters at the top of the list
        self.addItem("")
        self.addItem("Unused Keywords")
        unused_parent = self.model().item(1)
        unused_parent.setSelectable(False)
        unused_parent.setFont(font)
        for c in sorted(self.unused.keys()):
            self.addItem(c)

        # Add a separator, followed by parameters already in use
        self.addItem("---------------")
        self.addItem("Keywords In Use")
        divider = self.model().item(self.count() - 2)
        divider.setSelectable(False)
        inuse_parent = self.model().item(self.count() - 1)
        inuse_parent.setSelectable(False)
        inuse_parent.setFont(font)
        for d in sorted(self.inuse.keys()):
            self.addItem(d)

    def setTo(self, target):
        """ Set the combo box to a certain index given a CAOM keyword.
        """

        if target in self.allvalues:
            n = self.findText(target)
            self.setCurrentIndex(n)
        else:
            self.setCurrentIndex(0)

    def getXMLParent(self, keyword):
        """ Retrieve the XML parent value for a given CAOM keyword from the
        dictionary.
        """

        if keyword in self.allvalues.keys():
            return self.allvalues[keyword]
        else:
            return None
