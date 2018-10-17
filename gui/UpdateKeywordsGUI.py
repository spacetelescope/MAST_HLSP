import gui.GUIbuttons as gb
import os
import sys

from bin.read_yaml import read_yaml
from CHECK_METADATA_FORMAT.check_metadata_format import check_metadata_format
from CHECK_METADATA_FORMAT.precheck_data_format import precheck_data_format
from lib.CAOMKeywordBox import CAOMKeywordBox
from lib.FileType import FileType
from lib.FitsKeyword import FitsKeyword

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

TEMPLATES_DIR = "CHECK_METADATA_FORMAT/TEMPLATES"


class UpdateKeywordsGUI(QWidget):
    """
    This class constructs a GUI to view and modify FITS keywords values that
    HLSP data files are being checked for.

    ..module::  _add_keyword_row
    ..synopsis::  Add a new row to the keyword display area.  This may be
                  populated or a new empty row.

    ..module::  _del_last_keyword_row
    ..synopsis::  Remove the last keyword row from the display area.

    ..module::  _display_current_keywords
    ..synopsis::  Refresh the displayed keyword values based on the current
                  contents of self._keywords.

    ..module::  _find_in_keywords
    ..synopsis::  Look for a given keyword in self._keywords.

    ..module::  _get_current_standard
    ..synopsis::  Get the current FITS standard being used by the HLSPFile.
                  Currently only one standard can be handled at a time.

    ..module::  _load_standard_template
    ..synopsis::  Read a FITS keyword template file into FitsKeyword objects
                  and add these to self._keywords.

    ..module::  _read_keyword_row
    ..synopsis::  Read values from a row in the GUI and return them in a dict.

    ..module::  clear_keywords
    ..synopsis::  Remove all keyword rows currently in the display area.

    ..module::  load_current_fits
    ..synopsis::  Display information for all FITS keywords currently
                  associated with the HLSPFile.

    ..module::  update_hlsp_file
    ..synopsis::  Add FITS keyword information from the GUI to the parent
                  HLSPFile.
    """

    def __init__(self, parent):

        super().__init__(parent)

        # Set necesssary attributes.
        self._keywords = parent.hlsp.fits_keywords()
        self.master = parent
        cwd = os.getcwd()
        self.templates_dir = "/".join([cwd, TEMPLATES_DIR])
        self.standard_template = None

        # GUI elements to retrieve information from the current HLSPFile.
        update_button = gb.GreenButton("Refresh Keywords", 70)
        update_button.clicked.connect(self.load_current_fits)

        reset_button = gb.RedButton("Reset to Default Keywords", 70)
        reset_button.clicked.connect(self.reset_to_defaults)

        # GUI elements for column headers in the display area.
        bold = QFont()
        bold.setBold(True)
        standard_fits_label = QLabel("Standard FITS Keyword")
        standard_fits_label.setFont(bold)
        caom_keyword_label = QLabel("CAOM Keyword")
        caom_keyword_label.setFont(bold)
        alternate_fits_label = QLabel("Alternate FITS Keyword")
        alternate_fits_label.setFont(bold)
        header_num_label = QLabel("Header #")
        header_num_label.setFont(bold)
        default_val_label = QLabel("Default")
        default_val_label.setFont(bold)

        # Set up column order variables.
        self._select_col = 0
        self._standard_fits_col = 1
        self._caom_keyword_col = 2
        self._alternate_fits_col = 3
        self._header_num_col = 4
        self._default_val_col = 5

        # Set up row pointers.
        label_row = 1
        self._first_keyword = self._next_keyword = (label_row+1)

        # Construct the keyword display area.
        self.display_grid = QGridLayout()
        self.display_grid.addWidget(standard_fits_label,
                                    label_row,
                                    self._standard_fits_col
                                    )
        self.display_grid.addWidget(caom_keyword_label,
                                    label_row,
                                    self._caom_keyword_col
                                    )
        self.display_grid.addWidget(alternate_fits_label,
                                    label_row,
                                    self._alternate_fits_col
                                    )
        self.display_grid.addWidget(header_num_label,
                                    label_row,
                                    self._header_num_col
                                    )
        self.display_grid.addWidget(default_val_label,
                                    label_row,
                                    self._default_val_col
                                    )

        # GUI elements for a button to add additional keyword rows.
        self.new_keyword_button = gb.GreyButton("+ add a new keyword", 30)
        self.new_keyword_button.clicked.connect(self._add_keyword_row)
        self.remove_selected_button = gb.RedButton("- remove selected", 30)
        self.remove_selected_button.clicked.connect(self._remove_selected)

        # Construct the overall layout.
        self.meta_grid = QGridLayout()
        self.meta_grid.addWidget(update_button, 0, 0)
        self.meta_grid.addWidget(reset_button, 0, 1)
        self.meta_grid.addLayout(self.display_grid, 1, 0, 1, -1)
        self.meta_grid.addWidget(self.new_keyword_button, 2, 0)
        self.meta_grid.addWidget(self.remove_selected_button, 2, 1)

        # Display the GUI.
        self.setLayout(self.meta_grid)
        self.show()

    def _add_keyword_row(self, kw_obj=None):
        """
        Add a keyword row to the display area.  Populate it with FitsKeyword
        information if provided or leave it blank for the user to edit.

        :param kw_obj:  Option FitsKeyword object to display in the new row.
        :type kw_obj:  FitsKeyword
        """

        # GUI elements to edit alternate keywords, header numbers, and default
        # values.
        select_box = QCheckBox()
        select_box.setChecked(False)
        alt_fits_kw = QLineEdit()
        hdr_num = QLineEdit()
        def_val = QLineEdit()

        # If a FitsKeyword object was provided, populate the row with these
        # values.
        if kw_obj:
            if kw_obj.caom_status == "required":
                select_box.setEnabled(False)
            fits_kw = QLabel()
            fits_kw.setText(kw_obj.fits_keyword)
            caom_kw = QLabel()
            caom_kw.setText(kw_obj.caom_keyword)
            alt_fits_kw.setText(", ".join(kw_obj.alternates))
            hdr_num.setText(str(kw_obj.header))
            try:
                def_val.setText(str(kw_obj.default))
            except KeyError:
                pass

        # If no FitsKeyword is given, add editable FITS and CAOM keyword
        # fields.
        else:
            fits_kw = QLineEdit()
            caom_kw = CAOMKeywordBox()

        # Construct the row in the GUI.
        self.display_grid.addWidget(select_box,
                                    self._next_keyword,
                                    self._select_col
                                    )
        self.display_grid.addWidget(fits_kw,
                                    self._next_keyword,
                                    self._standard_fits_col
                                    )
        self.display_grid.addWidget(caom_kw,
                                    self._next_keyword,
                                    self._caom_keyword_col
                                    )
        self.display_grid.addWidget(alt_fits_kw,
                                    self._next_keyword,
                                    self._alternate_fits_col
                                    )
        self.display_grid.addWidget(hdr_num,
                                    self._next_keyword,
                                    self._header_num_col
                                    )
        self.display_grid.addWidget(def_val,
                                    self._next_keyword,
                                    self._default_val_col
                                    )

        # Update stretch values and the _next_keyword pointer.
        self.display_grid.setRowStretch(self._next_keyword, 0)
        self._next_keyword += 1
        self.display_grid.setRowStretch(self._next_keyword, 1)

    def _del_last_keyword_row(self):
        """
        Remove the last row from the keyword display area.
        """

        # Move the _next_keyword pointer back first to find the last row.
        self._next_keyword -= 1

        # Remove all GUI elements from the row.
        n_elements = self.display_grid.columnCount()
        for n in range(n_elements):
            x = self.display_grid.itemAtPosition(self._next_keyword, n)
            x = x.widget()
            x.setParent(None)

    def _display_current_keywords(self):
        """
        Display the current contents of self._keywords in the keyword display
        area.
        """

        # Clear any currently-displayed rows first.
        self.clear_keywords()

        # Make a new row for each entry in self._keywords.
        for kw in self.master.hlsp.fits_keywords().keywords:
            self._add_keyword_row(kw_obj=kw)

    def _find_in_keywords(self, target_kw):
        """
        Find a given keyword in self._keywords.
        """

        # Search self._keywords for target_kw and return the FitsKeyword
        # object if found.
        for kw_obj in self._keywords.keywords:
            if kw_obj.fits_keyword.upper() == target_kw:
                return kw_obj

        # Return None if no matching keyword was found.
        return None

    def _get_current_standard(self):
        """
        Get the current FITS standard used in the parent HLSPFile and construct
        the path to the appropriate template file.
        """

        # Get FITS standard information from the parent HLSPFile.
        standards = self.master.hlsp.member_fits_standards()

        # Display information on the results in the GUI (currently, only one
        # standard is expected).
        if standards is None:
            std_label = QLabel("No FITS standard found!")
        elif len(standards) > 1:
            std_label = QLabel("More than 1 FITS standard found!")
        else:
            std_label = QLabel("Loaded {0} keywords".format(standards[0]))
        self.display_grid.addWidget(std_label, 0, 0)

        # Update the self.standard_template filepath.
        std = ".".join([standards[0], "yml"])
        self.standard_template = "/".join([self.templates_dir, std])

    def _load_standard_template(self):
        """
        Read a FITS standard template file and add the info to self._keywords.
        """

        # If the standard template file has not been identified yet, return.
        if not self.standard_template:
            return

        # Read the template file and access the keywords information.
        template = read_yaml(self.standard_template)
        keywords = template["KEYWORDS"]

        # Use the template file information to create FitsKeyword objects and
        # add these to self._keywords.
        for key, info in keywords.items():
            kw = FitsKeyword(key, parameters=info)
            self._keywords.add(kw)

    def _read_keyword_row(self, row_num):
        """
        Collect information from a keyword row in the GUI.
        """

        # Access the needed GUI elements.
        std_fits = self.display_grid.itemAtPosition(row_num,
                                                    self._standard_fits_col
                                                    )
        caom_kw = self.display_grid.itemAtPosition(row_num,
                                                   self._caom_keyword_col
                                                   )
        new_fits = self.display_grid.itemAtPosition(row_num,
                                                    self._alternate_fits_col
                                                    )
        hdr_num = self.display_grid.itemAtPosition(row_num,
                                                   self._header_num_col
                                                   )
        default = self.display_grid.itemAtPosition(row_num,
                                                   self._default_val_col
                                                   )

        # Store the values in a dictionary.
        row_info_dict = {}

        # If the CAOM keyword widget is a CAOMKeywordBox object (should be)
        # add information from this class to the results dictionary.
        caom_kw = caom_kw.widget()
        if isinstance(caom_kw, CAOMKeywordBox):
            k = caom_kw.currentText()
            row_info_dict["caom_keyword"] = k
            row_info_dict["xml_parent"] = caom_kw.getXMLParent(keyword=k)
            row_info_dict["hlsp_status"] = "recommended"

        # Turn the alternates text field into a list.
        alternates = new_fits.widget().text()
        alternates = [a.strip().upper() for a in alternates.split(",")]
        if len(alternates) == 1 and alternates[0] == "":
            alternates = []
        row_info_dict["alternates"] = alternates

        # Read the remaining fields.
        row_info_dict["header"] = hdr_num.widget().text()

        def_text = default.widget().text()

        if (def_text == "" or def_text == "None"):
            row_info_dict["default"] = None
        else:
            row_info_dict["default"] = def_text

        this_kw = std_fits.widget().text().upper()

        # Return the keyword value and results dictionary.
        return this_kw, row_info_dict

    def _remove_selected(self):
        """
        Find any selected keywords in the display area and remove them from
        self._keywords, then reset the display.
        """

        for n in range(self._first_keyword, self._next_keyword):

            selected = self.display_grid.itemAtPosition(n, self._select_col)
            kw = self.display_grid.itemAtPosition(n, self._standard_fits_col)

            if selected.widget().isChecked():

                target = self._find_in_keywords(kw.widget().text())
                self._keywords.remove(target)

        self._display_current_keywords()

    def clear_keywords(self):
        """
        Remove all keyword rows from the GUI display area.
        """

        # Remove the last keyword row until the _next_keyword pointer is
        # looking at the first row.
        while self._next_keyword > self._first_keyword:
            self._del_last_keyword_row()

    def load_current_fits(self):
        """
        Set self._keywords equal to the current HLSPFile keywords and update
        the GUI.
        """

        self._keywords = self.master.hlsp.fits_keywords()
        if self._keywords.is_empty():
            self.master.hlsp._get_standard_fits_keywords()
        self._display_current_keywords()

    def reset_to_defaults(self):
        """
        Revert the HLSPFile object to standard default FITS keywords.
        """

        self.master.hlsp.reset_fits_keywords()
        self._display_current_keywords()

    def update_hlsp_file(self):
        """
        Update the parent HLSPFile with the values currently in the GUI.
        """

        print("Updating HLSPFile from UpdateKeywordsGUI")
        current_keywords = self.master.hlsp.fits_keywords()

        # Read each keyword row in the display area.
        for row in range(self._first_keyword, self._next_keyword):
            kw, row_info = self._read_keyword_row(row)

            # Look for this keyword in self._keywords.
            existing_kw = current_keywords.find_fits(kw)

            # If already in self._keywords, try updating the FitsKeyword
            # object.
            if existing_kw:
                update_flag = existing_kw.update(row_info)
                if update_flag:
                    print("GUI updated {0}".format(existing_kw))

                """
                # If it updates an existing FitsKeyword, add it to the
                # HLSPFile.
                if update_flag:
                    self.master.hlsp.add_keyword_update(existing_kw)
                """

            # If it is not already in self._keywords, create a new FitsKeyword
            # object and add it to self._keywords and the HLSPFile.
            else:
                new_kw = FitsKeyword(kw, parameters=row_info)
                self.master.hlsp.add_fits_keyword(new_kw)

        # Update the ingest step tracker.
        self.master.hlsp.ingest["03_fits_keywords_set"] = True
