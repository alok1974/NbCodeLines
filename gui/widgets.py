###########################################################################################
###########################################################################################
##                                                                                       ##
##  Nb Code Lines v 1.0 (c) 2015 Alok Gandhi (alok.gandhi2002@gmail.com)                 ##
##                                                                                       ##
##                                                                                       ##
##  This file is part of Nb Code Lines.                                                  ##
##                                                                                       ##
##  Nb Code lines is free software: you can redistribute it and/or modify                ##
##  it under the terms of the GNU General Public License, Version 3, 29 June 2007        ##
##  as published by the Free Software Foundation,                                        ##
##                                                                                       ##
##  Nb Code Lines is distributed in the hope that it will be useful,                     ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of                       ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                        ##
##  GNU General Public License for more details.                                         ##
##                                                                                       ##
##  You should have received a copy of the GNU General Public License                    ##
##  along with Scenetoc Res Manager.  If not, see <http://www.gnu.org/licenses/>.        ##
##                                                                                       ##
###########################################################################################
###########################################################################################



import os
import sys
from PyQt4 import QtCore, QtGui
import json


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.join(__file__)), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from gui import *
from logger import Logger



def EnableDoubleClickOnWidget(widget):
    # Re implementation for the Double Clicks
    class MouseDoubleClickFilter(QtCore.QObject):
        _doubleClicked = QtCore.pyqtSignal()

        def eventFilter(self, obj, event):
            if obj==widget:
                if event.type()==QtCore.QEvent.MouseButtonDblClick:
                    self._doubleClicked.emit()
                    return True

            return False

    filter = MouseDoubleClickFilter(widget)
    widget.installEventFilter(filter)

    return filter._doubleClicked


class JSONHelper(object):
    def __init__(self, fileType='', *args, **kwargs):
        super(JSONHelper, self).__init__(*args, **kwargs)
        self.extFile = os.path.join(ROOT_DIR, 'prefs', fileType)
        self._ext = {}
        self._createDefaults()
        
    def _createDefaults(self):
        if not os.path.exists(self.extFile):
            self._writeExtensions(fTypeDict=DEFAULT_FILETYPES)
        
    def _readExtensions(self):
        with open(self.extFile, 'rb') as file:
            self._ext = json.load(file)
    
    def _writeExtensions(self, fTypeDict={}):
        with open(self.extFile, 'wb') as file:
            json.dump(fTypeDict, file, sort_keys=True, indent=4)
        
    def getFileTypes(self):
        self._readExtensions()
        return self._ext
    
    def setFileTypes(self, fTypeDict):
        self._writeExtensions(fTypeDict=fTypeDict)
        

class RecentSearchData(object):
    def __init__(self, *args, **kwargs):
        super(RecentSearchData, self).__init__(*args, **kwargs)
        self.recentSearchesFile = os.path.join(ROOT_DIR, 'prefs', '_rs')
        self.recentSearchData = {}
        self.maxFiles = 5

    def _createDataFile(self):
        with open(self.recentSearchesFile, 'wb') as file:
            json.dump(self.recentSearchData, file, sort_keys=True, indent=4)

    def _fetchRecent(self):
        if not os.path.exists(self.recentSearchesFile):
            self._createDataFile()

        with open(self.recentSearchesFile, 'rb') as file:
            self.recentSearchData = json.load(file)

        return self.recentSearchData

    def _writeRecent(self):
        with open(self.recentSearchesFile, 'wb') as file:
            json.dump(self.recentSearchData, file, sort_keys=True, indent=8)

    def _addData(self, dataToAdd):
        
        self._fetchRecent()
        
        # If this entry already exists in the data dict
        # then we first remove it  and add it with new
        # order
        folder = dataToAdd[0]
        if folder in self.recentSearchData.keys():
            self.recentSearchData.pop(folder)          
        
        # We initialize the current order for the first entry
        currOrder = INFINITY
        
        if self.recentSearchData:
            # If this entry is more than the max allowed entry then
            # we remove the oldest entry
            if len(self.recentSearchData) == self.maxFiles:
                maxOrder = max([ self.recentSearchData[key]['order'] for key in self.recentSearchData.keys()])
                folderToRemove = ''
                for thisFolder, thisFolderdata in self.recentSearchData.iteritems():
                    thisOrder = thisFolderdata['order']
                    
                    if(thisOrder == maxOrder):
                        folderToRemove = thisFolder

                self.recentSearchData.pop(folderToRemove)
            
            # Now find the order to which to add this entry                
            currOrder = min([ self.recentSearchData[key]['order'] for key in self.recentSearchData.keys()])                


        # Finally we add the entry and write to the recent search data file
        self.recentSearchData[folder] = {
                                            'order': currOrder - 1,
                                            'ext': dataToAdd[1],
                                            'startDate': dataToAdd[2],
                                            'startMonth': dataToAdd[3],
                                            'startYear': dataToAdd[4]
                                         }

        self._writeRecent()


    def _removeData(self, searchFolderToRemove):
        self._fetchRecent()
        
        if searchFolderToRemove not in self.recentSearchData.keys():
            return
        
        self.recentSearchData.pop(searchFolderToRemove)
        
        self._writeRecent()
        
    
    def _clearAll(self):
        self.recentSearchData = {}
        self._writeRecent()


class StyleSheet(object):
    def __init__(self, *args, **kwargs):
        super(StyleSheet, self).__init__(*args, **kwargs)
        self.prefFile = os.path.join(ROOT_DIR, 'prefs', '_cs')
        self.style = ''

    def _createPrefs(self):
        with open(self.prefFile, 'w') as f:
            f.write('theme:%s' % DEFAULT_THEME)

    def _readPrefs(self):
        if not os.path.exists(self.prefFile):
            self._createPrefs()

        with open(self.prefFile, 'r') as f:
            s = f.readlines()

        self.style= s[0].split(':')[1]

        return self.style

    def _writePrefs(self, pref=''):
        if not os.path.exists(self.prefFile):
            self._createPrefs()

        with open(self.prefFile, 'w') as f:
            f.write('theme:%s:' % pref)

    def setColor(self, widget, app=None, init=False):
        self._readPrefs()

        if not self.style:
            if app:
                pass
                app.setStyle(QtGui.QStyleFactory.create(APP_STYLE))

            widget.setStyleSheet("")

            return

        if self.style not in STYLESHEET_OPTIONS:
            raise Exception('"%s" type of stylesheet option does not exist !!' % self.style)

        p = os.path.join(ROOT_DIR, 'styleSheets', str(self.style))

        if not os.path.exists(p):
            raise Exception('Style Path - %s does not exist !!' % p)

        with open(p, 'r') as f:
            s = f.read()

        if app:
            app.setStyle(QtGui.QStyleFactory.create("Plastique"))

        widget.setStyleSheet(s)


class AboutWidget(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutWidget, self).__init__(*args, **kwargs)
        self.setModal(True)
        StyleSheet().setColor(self)
        self._initUI()

    def _initUI(self):
        self.pic = QtGui.QLabel(self)
        self.pic.setFixedSize(376, 240)
        self. pic.setPixmap(QtGui.QPixmap(os.path.abspath(os.path.join(ROOT_DIR, 'rsc/_ai'))))
        self.setFixedSize(376, 240)
        self.setWindowTitle('About')
    
class TextWidget(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(TextWidget, self).__init__(*args, **kwargs)
        self.setModal(True)

        # Set UI
        self._initUI()

        StyleSheet().setColor(self)

        # Connect Signals
        self._connectSignals()

    def _initUI(self):
        # Add Widgets
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setAcceptRichText(True)

        self.okBtn = QtGui.QPushButton('Ok')
        self.okBtn.setMinimumSize(80, 25)

        # Add Layout
        self._vLayout = QtGui.QVBoxLayout()
        self._hLayout = QtGui.QHBoxLayout()
        #self._hLayout.addStretch(1)

        # Add Widgets to Layouts
        self._hLayout.addWidget(self.okBtn)

        self._vLayout.addWidget(self.textEdit)
        self._vLayout.addLayout(self._hLayout)

        self.setGeometry(300, 100, 500, 600)

        self.setLayout(self._vLayout)

    def _connectSignals(self):
        self.okBtn.clicked.connect(self._okBtnOnClicked)

    def _okBtnOnClicked(self):
        self.textEdit.sizeHint()
        self.close()
        
        
class FileTypeEntryWidget(QtGui.QDialog):
    def __init__(self, entry=[], title = 'Add New Entry', *args, **kwargs):
        super(FileTypeEntryWidget, self).__init__(*args, **kwargs)
        self.setModal(True)
        self.setWindowTitle(title)
        StyleSheet().setColor(self)
        
        self._entry = entry
    
        # Set UI
        self._initUI()
        self._updateUI()
        self._connect()
        
    def _initUI(self):
        # QLabels
        self._fileTypeNameLabel = QtGui.QLabel("File Type Name")
        self._fileTypeExtLabel = QtGui.QLabel("File Type Extention")
        
        # QLineEdits
        self._fileTypeNameLineEdit = QtGui.QLineEdit()
        self._fileTypeExtLineEdit = QtGui.QLineEdit()
        
        # QPushButton
        self._okBtn = QtGui.QPushButton("OK")
        
        # Grid
        self._grid = QtGui.QGridLayout()
        self._grid.setSpacing(20)
        
        self._grid.addWidget(self._fileTypeNameLabel, 1, 0)
        self._grid.addWidget(self._fileTypeNameLineEdit, 1, 1)
        
        self._grid.addWidget(self._fileTypeExtLabel, 2, 0)
        self._grid.addWidget(self._fileTypeExtLineEdit, 2, 1)
        
        self._grid.addWidget(self._okBtn, 3, 0, 1, 2)

        self.setLayout(self._grid)
        
        self.move(300, 100)
        self.setMinimumSize(300, 150)
    
    
    def _updateUI(self):
        # Open UI with entry
        self._fileTypeNameLineEdit.setText(self._entry[0])
        self._fileTypeNameLineEdit.setCursorPosition(0)
        
        self._fileTypeExtLineEdit.setText(self._entry[1])
        self._fileTypeExtLineEdit.setCursorPosition(0)
        
    def _connect(self):
        self._okBtn.clicked.connect(self._okBtnOnClicked)
        
    def _okBtnOnClicked(self):
        self._entry[0] = str(self._fileTypeNameLineEdit.text())
        self._entry[1] = str(self._fileTypeExtLineEdit.text())
        self.close()
    
    
        
        
class FileTypeWidget(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(FileTypeWidget, self).__init__(*args, **kwargs)
        self.setModal(True)
        self.setWindowTitle('Select File Types (Right click to edit item)')
        self._fileTypesData = {}
        self._fileExt = []
        self._entry = ['', '']
        self._displayString = ''
        self._prefFileType = '_fext'

        # Set UI
        self._initUI()
        self._updateFileTypesListWidget()

        StyleSheet().setColor(self)

        # Connect Signals
        self._connectSignals()

    def _initUI(self):
        # QLists
        self._fileTypesListWidget = QtGui.QListWidget()
        self._fileTypesListWidget.setMinimumSize(150, 150)
        self._fileTypesListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.addBtn = QtGui.QPushButton('Add New File Type')
        self.addBtn.setMinimumSize(80, 25)

        
        self.okBtn = QtGui.QPushButton('Ok')
        self.okBtn.setMinimumSize(80, 25)

        # Add Layout
        self._vLayout = QtGui.QVBoxLayout()
        self._hLayout01 = QtGui.QHBoxLayout()
        self._hLayout02 = QtGui.QHBoxLayout()
  

        # Add Widgets to Layouts
        self._hLayout01.addWidget(self.addBtn)
        self._hLayout02.addWidget(self.okBtn)

        self._vLayout.addWidget(self._fileTypesListWidget)
        self._vLayout.addLayout(self._hLayout01)
        self._vLayout.addLayout(self._hLayout02)

        self.setGeometry(300, 100, 500, 600)

        self.setLayout(self._vLayout)

    def _connectSignals(self):
        self.okBtn.clicked.connect(self._okBtnOnClicked)
        self.addBtn.clicked.connect(self._addBtnOnClicked)
        self._fileTypesListWidget.itemChanged.connect(self._fileTypesCheckBoxOnClicked)
        self._fileTypesListWidget.connect(self._fileTypesListWidget, QtCore.SIGNAL("customContextMenuRequested(QPoint)" ), self._listItemOnRightClicked)

    
    def _fileTypesCheckBoxOnClicked(self, item):
        if item == self._fileTypesListWidget.item(0):
            for index in range(self._fileTypesListWidget.count()):
                if index == 0:
                    continue
                thisItem = self._fileTypesListWidget.item(index)
                thisItem.setCheckState(item.checkState())
        
            
            return
            
        thisExt = self._fileTypesData[str(item.text())]
        
        if item.checkState()== 2:
            if thisExt not in self._fileExt:
                self._fileExt.append(thisExt)
                
        
        if item.checkState() == 0:
            self._fileTypesListWidget.blockSignals(True) # blocking signals so the func does not go in recursion
            self._fileTypesListWidget.item(0).setCheckState(0)
            self._fileTypesListWidget.blockSignals(False)
            
            if thisExt in self._fileExt:
                self._fileExt.remove(thisExt)
                
        self._displayString = ' | '.join(self._fileExt)
    
    
    def _listItemOnRightClicked(self, QPos):
        # Adding Context Menu
        self._contextMenu= QtGui.QMenu()
        StyleSheet().setColor(self._contextMenu)
        _editAction = self._contextMenu.addAction("Edit File Type")
        _removeAction = self._contextMenu.addAction("Remove File Type")
       
        
        if len(self._fileTypesData.keys())==0 or str(self._fileTypesListWidget.currentItem().text()) == 'All':
            _editAction.setDisabled(True)
            _removeAction.setDisabled(True)
        
        # Connections for Context Menu Actions
        self.connect(_removeAction, QtCore.SIGNAL("triggered()"), self._removeEntry)
        self.connect(_editAction, QtCore.SIGNAL("triggered()"), self._editEntry) 

        # Settings the position of the Context Menu
        parentPosition = self._fileTypesListWidget.mapToGlobal(QtCore.QPoint(0, 0))        
        self._contextMenu.move(parentPosition + QPos)
        self._contextMenu.show()
        
    
    def _removeEntry(self):
        fileTypeName = str(self._fileTypesListWidget.currentItem().text())
        self._fileTypesData.pop(fileTypeName)
        self._rebuildFileTypes()
        
        
    def _editEntry(self):
        
        fileTypeName = str(self._fileTypesListWidget.currentItem().text())
        fileTypeExt = str(self._fileTypesData[fileTypeName])

        # remove the entry as it will be added again
        # by the update entry call and no duplicates
        # will be created
        self._fileTypesData.pop(fileTypeName)
        
        self._entry[0] = fileTypeName
        self._entry[1] = fileTypeExt
        
        self._updateEntry(editing=True)
    
    def _addEntry(self):
        self._entry = ['', '']
        self._updateEntry()

    def _updateEntry(self, editing=False):
        self._fileExt = []
        
        if editing:
            title = "Edit Entry"
        else:
            title = "Add New Entry"
            
        if not hasattr(self, 'fe'):
            self.fe = FileTypeEntryWidget(entry=self._entry, title=title)
        else:
            self.fe = None
            self.fe = FileTypeEntryWidget(entry=self._entry, title=title)
    
        self.fe.setGeometry(100, 100, 100, 100)
        self.fe.exec_()
        
        if self._validateEntry(editing=editing) == -1:
            return
        
        self._fileTypesData[self._entry[0]] = self._entry[1]
        
        self._rebuildFileTypes()
    
    def _validateEntry(self, editing=False):
        if self._entry[0] == '' or self._entry[1] == '':
            return -1
        
        self._formatEntry()
        
        if str(self._entry[0]).lower() in [str(e).lower() for e in self._fileTypesData.keys()]:
            if editing:
                return 0
            
            else:
                errStr = "This File Type already exist!\n\n"
                errStr += "Right click on the entry to edit it."
                self._showErrorText(winTitle="Duplicate Entry", err=errStr)
                return -1

        return 0
    
    def _formatEntry(self):
        fileNameType = ' '.join([str(fn[0]).upper() + str(fn[1:]).lower() for fn in (str(self._entry[0]).split(' '))])  

        fileExtType = self._entry[1]
        if str(fileExtType).startswith('.'):
            fileExtType = fileExtType[1:]

        fileExtType = str(fileExtType).lower()
        fileExtType = '.%s' % fileExtType
        
        self._entry[0] = fileNameType
        self._entry[1] = fileExtType
        
      
    def _showErrorText(self, winTitle="Error", err=""):
        if not hasattr(self, 'tw'):
            self.tw = TextWidget()
        else:
            self.tw = None
            self.tw = TextWidget()
    
        self.tw.textEdit.setText(err)
        self.tw.setWindowTitle(winTitle)
        self.tw.setGeometry(100, 100, 100, 100)
        self.tw.show()  
    
    
    def _rebuildFileTypes(self):
        jh = JSONHelper(fileType=self._prefFileType)
        jh.setFileTypes(fTypeDict=self._fileTypesData)
        self._updateFileTypesListWidget()
        
        
    def _updateFileTypesListWidget(self):
        self._fileTypesListWidget.clear()
        jh = JSONHelper(fileType=self._prefFileType)
        self._fileTypesData = jh.getFileTypes()
        
        # Add an item for All
        w = QtGui.QListWidgetItem('Select All')
        w.setCheckState(0)
        self._fileTypesListWidget.addItem(w)
        
        fileNames = self._fileTypesData.keys()
        
        fileNames.sort()
        
        for fileName in fileNames:
            w = QtGui.QListWidgetItem(fileName)
            w.setCheckState(0)
            self._fileTypesListWidget.addItem(w)
            

    def _addBtnOnClicked(self):
        self._addEntry()

    def _okBtnOnClicked(self):
        self.close()


class CalendarWidget(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(CalendarWidget, self).__init__(*args, **kwargs)
        self.setModal(True)
        self._day = 0
        self._month = 0
        self._year = 0
        self._dateString = ''
        self.setWindowTitle('Set Start Date')

        # Set UI
        self._initUI()
        

        StyleSheet().setColor(self)

        # Connect Signals
        self._connectSignals()

    def _initUI(self):
        # Calendar
        self._calendar = QtGui.QCalendarWidget()
        self._calendar.setGridVisible(True)
        self._calendar.setMinimumSize(150, 150)
        
        self.okBtn = QtGui.QPushButton('Ok')
        self.okBtn.setMinimumSize(80, 25)

        # Add Layout
        self._vLayout = QtGui.QVBoxLayout()
        self._hLayout = QtGui.QHBoxLayout()

        # Add Widgets to Layouts
        self._hLayout.addWidget(self.okBtn)

        self._vLayout.addWidget(self._calendar)
        self._vLayout.addLayout(self._hLayout)

        self.setLayout(self._vLayout)

    def _connectSignals(self):
        self.okBtn.clicked.connect(self._okBtnOnClicked)
        self._calendar.clicked[QtCore.QDate].connect(self._calendarOnClicked)


    def _calendarOnClicked(self, date):
        self._day = date.day()
        self._month = date.month()
        self._year = date.year()
        
        self._dateString = date.toString()


    def _okBtnOnClicked(self):
        self.close()


# This class overrides the F2 Key Pressed Signal for the line edits
class F2PressableLineEdit(QtGui.QLineEdit):
    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)
        
    def event(self, event):
        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_F2):
            self.emit(QtCore.SIGNAL("F2Pressed"))
            return True

        return QtGui.QLineEdit.event(self, event)


class MainWidgetUI(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWidgetUI, self).__init__(*args, **kwargs)
        
        
    def _setupUI(self):
        # Lines
        self._lines = []
        for i in range(2):
            _line = QtGui.QFrame()
            _line.setGeometry(QtCore.QRect(170, 90, 118, 8))
            _line.setFrameShape(QtGui.QFrame.HLine)
            _line.setFrameShadow(QtGui.QFrame.Sunken)
            _line.setStyleSheet("QFrame {background-color : rgb(58, 84, 92);}")
            self._lines.append(_line)
            
        self._vLine = QtGui.QFrame()
        self._vLine.setGeometry(QtCore.QRect(170, 90, 118, 8))
        self._vLine.setFrameShape(QtGui.QFrame.VLine)
        self._vLine.setFrameShadow(QtGui.QFrame.Sunken)
        self._vLine.setStyleSheet("QFrame {background-color : rgb(58, 84, 92);}")

            
        # Labels
        
        # Column 01
        self._selectFolderLabel = QtGui.QLabel('<b>Select root folder containg code files</b> <i>(Double Click or press F2)</i>')
        self._selectExtLabel = QtGui.QLabel('<b>Select File Types to include in the analytics</b> <i>(Double Click or press F2)</i>')
        self._selectDateLabel = QtGui.QLabel('<b>Select Project Start Date</b> <i>(Double Click or press F2)</i>')
        
        # Column 02
        self._fileStatusLabel = QtGui.QLabel()
        self._sumTotalLinesLabel = QtGui.QLabel('<b>Sum Total Lines: </b>')
        self._sumActualLinesLabel = QtGui.QLabel('<b>Sum Actual Lines: </b>')
        self._nbPrjDaysLabel = QtGui.QLabel('<b>Days Since Project Started</b>')
        self._avgLinesPerDayLabel = QtGui.QLabel('<b>Avegrage Lines Per Day</b>')
        self._avgLinesPerHourLabel = QtGui.QLabel('<b>Average Lines Per Hour</b>')
        self._codeDensityLabel = QtGui.QLabel('<b>Code Density</b>')
        
        

        # Line Edits
        bg = (57, 67, 76)
        fg = (255, 255, 255)
        
        self._selectedFolderLineEdit = F2PressableLineEdit()
        self._selectedFolderLineEdit.setReadOnly(True)
        self._selectedFolderLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        self._selectedFileTypeLineEdit = F2PressableLineEdit()
        self._selectedFileTypeLineEdit.setReadOnly(True)
        self._selectedFileTypeLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        
        self._selectedDateLineEdit = F2PressableLineEdit()
        self._selectedDateLineEdit.setReadOnly(True)
        self._selectedDateLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        
        self._sumTotalLinesLineEdit = QtGui.QLineEdit()
        self._sumTotalLinesLineEdit.setReadOnly(True)
        self._sumTotalLinesLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        
        self._sumActualLinesLineEdit = QtGui.QLineEdit()
        self._sumActualLinesLineEdit.setReadOnly(True)
        self._sumActualLinesLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        
        self._nbPrjDaysLineEdit = QtGui.QLineEdit()
        self._nbPrjDaysLineEdit.setReadOnly(True)
        self._nbPrjDaysLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        
        self._avgLinesPerDayLineEdit = QtGui.QLineEdit()
        self._avgLinesPerDayLineEdit.setReadOnly(True)
        self._avgLinesPerDayLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))
        
        
        self._avgLinesPerHourLineEdit = QtGui.QLineEdit()
        self._avgLinesPerHourLineEdit.setReadOnly(True)
        self._avgLinesPerHourLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))

        
        self._codeDensityLineEdit = QtGui.QLineEdit()
        self._codeDensityLineEdit.setReadOnly(True)
        self._codeDensityLineEdit.setStyleSheet("QLineEdit {background-color : \
                                                   rgb(%s, %s, %s); \
                                                   color : \
                                                   rgb(%s, %s, %s)}"
                                                    % (bg[0], bg[1], bg[2],
                                                       fg[0], fg[1], fg[2]))


        
        # Buttons
        self._okBtn = QtGui.QPushButton('Get Code Details')
        self._okBtn.setToolTip('Get Results.')
       
        self._cancelBtn = QtGui.QPushButton('Close')
        self._cancelBtn.setToolTip('Quit Application.')
       
        
        # Table
        self._dataTable = QtGui.QTableWidget()
        


        # Just a display Table with no functionality
        self._displayTable = QtGui.QTableWidget()
        self._displayTable.setFrameShape(QtGui.QFrame.NoFrame)     
        
        self._displayTableItem = QtGui.QTableWidgetItem()
        
        self._displayTableBtn = QtGui.QPushButton()
        self._displayTableBtn.setIcon(QtGui.QIcon(os.path.join(ROOT_DIR, 'rsc/_bi')))
        self._displayTableBtn.setIconSize(QtCore.QSize(600, 1200))


        
        self._displayTable.setRowCount(1)
        self._displayTable.setColumnCount(3)
        self._displayTable.setHorizontalHeaderLabels(["File Name", "Total Lines", "Actual Lines"])
        self._displayTable.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._displayTable.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._displayTable.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._displayTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self._displayTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self._displayTable.horizontalHeader().setVisible(False)
        self._displayTable.verticalHeader().setVisible(False)
        self._displayTable.setItem(0, 0, self._displayTableItem)
        self._displayTable.setCellWidget(0,0, self._displayTableBtn)
        self._displayTable.setSpan(0, 0, self._displayTable.rowCount(), self._displayTable.columnCount())
        

        # Horizontal Layouts
        self._hFolderLayout01 = QtGui.QHBoxLayout()
        self._hFolderLayout01.addWidget(self._okBtn)
        self._hFolderLayout01.addWidget(self._cancelBtn)


        # Grid Layout for Analyed Data
        self._grid02 = QtGui.QGridLayout()
        
        self._grid02.addWidget(self._sumActualLinesLabel, 0, 0)
        self._grid02.addWidget(self._sumActualLinesLineEdit, 0, 1)
        
        self._grid02.addWidget(self._sumTotalLinesLabel, 1, 0)
        self._grid02.addWidget(self._sumTotalLinesLineEdit, 1, 1)

        self._grid02.addWidget(self._nbPrjDaysLabel, 2, 0)
        self._grid02.addWidget(self._nbPrjDaysLineEdit, 2, 1)
        
        self._grid02.addWidget(self._avgLinesPerDayLabel, 3, 0)
        self._grid02.addWidget(self._avgLinesPerDayLineEdit, 3, 1)
        
        self._grid02.addWidget(self._avgLinesPerHourLabel, 4, 0)
        self._grid02.addWidget(self._avgLinesPerHourLineEdit, 4, 1)
        
        self._grid02.addWidget(self._codeDensityLabel, 5, 0)
        self._grid02.addWidget(self._codeDensityLineEdit, 5, 1)           


        
        # Grid Layout Management
        self._grid = QtGui.QGridLayout()
        self._grid.setSpacing(15)

        gridLayoutData =    {
                                0:  {
                                        'width' : 2,
                                        
                                        'widgets':  [

                                                        (self._displayTable, 15),
                                                        (self._lines[0], 1),
                                                        (self._selectFolderLabel, 1),
                                                        (self._selectedFolderLineEdit, 1),
                                                        (self._selectExtLabel, 1),
                                                        (self._selectedFileTypeLineEdit, 1),
                                                        (self._selectDateLabel, 1),
                                                        (self._selectedDateLineEdit, 1),
                                                        (self._hFolderLayout01, 1),
                                                        
                                                    ],
                                                    
                                    },
                                
                                1:  {
                                        'width' : 1,
                                        
                                        'widgets':  [
                                                        (self._vLine, 23)
                                                    ],
                                    },
                                
                                2:  {
                                        'width': 1,
                                        
                                        'widgets':  [
                                                        (self._dataTable, 15),
                                                        (self._lines[1], 1),
                                                        (self._fileStatusLabel, 1),
                                                        (self._grid02, 6),

                                                    ],
                                    
                                    }
                            
                        }
        
        
        # Creating the grid layout
        columns = gridLayoutData.keys()
        currColumn = min(columns)
        for c in sorted(columns):
            #currColumn = c
            data = gridLayoutData[c]
            width = data['width']
            widgets = data['widgets']
            i = 0
            for t in widgets:
                w, height = t
                if str(type(w)) == "<class 'PyQt4.QtGui.QHBoxLayout'>" or  str(type(w)) == "<class 'PyQt4.QtGui.QGridLayout'>":
                    self._grid.addLayout(w, i, currColumn, height, width)
                else:
                    self._grid.addWidget(w, i, currColumn, height, width)
                    
                i += height
            
            currColumn += width

        # Adding the grid to the main layout
        self._mainLayout = QtGui.QVBoxLayout(self)
        self._mainLayout.addLayout(self._grid)
        
        
        
def testWidget(widget=None, *args, **kwargs):
    app = QtGui.QApplication(sys.argv)
    tw = widget(*args, **kwargs)
    tw.show()
    tw.raise_()
    app.exec_()    
