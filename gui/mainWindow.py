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
##  along with Nb Code lines.  If not, see <http://www.gnu.org/licenses/>.               ##
##                                                                                       ##
###########################################################################################
###########################################################################################


import os
import sys
import functools
import re
import subprocess
import platform
from PyQt4 import QtCore, QtGui


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.join(__file__)), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from gui import *
from widgets import *
from modules.codeLines import CodeLines
from logger import Logger

# Setting the icon for the task bar in windows
if sys.platform.startswith('win'):
    import ctypes
    myappid = 'nbcodelines' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Separate worker thread for Analysing Folder Structure (Main Function)
class RunAnalyticsTask(QtCore.QThread):
    def __init__(self, folder="", ext=[], startDate=0, startMonth=0, startYear=0, parent=None, *args, **kwargs):
        QtCore.QThread.__init__(self, parent)
        
        self.data = None
        self._folder = folder
        self._ext = ext
        self._startDate = startDate
        self._startMonth = startMonth
        self._startYear = startYear
        
        self.cl = CodeLines(
                qThread=self,
                folder=self._folder,
                ext=self._ext,
                startDate=self._startDate,
                startMonth=self._startMonth,
                startYear=self._startYear
               )
        

    # Call this to launch the thread
    def runAnalytics(self):
        self.start()

    # This run method is called by Qt as a result of calling start()
    def run(self):
        self.data = self.cl.runThread()


class MainWidget(MainWidgetUI):
    _ranSignal = QtCore.pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)
    
        self._rootDir = DEFAULT_FOLDER_STRING
        self._result = ''
        self._data = None
        self._rootDirChanged = False
        self._day = 0
        self._month = 0
        self._year = 0
        self._fileTypesData = {}
        self._fileExt = []
        self._hasError = False
        self._updateString = 'Analysing File: \n'
        self._animCounter = 0
        self._animTimerCounter = 0
        self._nbHoldFrame = 300
        self._animatedStr = PROGRESS_ANIM_TEXT_LIST[0]
        self._nbPrjDays = -1
        self._avgLinesPerDay = -1
        self._avgLinesPerHour = -1
        self._codeDensity = -1
        self._sumTotalLine = 0
        self._sumActualLine = 0
        self._rsd = RecentSearchData()
        
        
    
        # Setup Layout
        self._initUI()
        self._connectSignals()


    def _initUI(self):
        self._setupUI()
        self._initLineEdits()
        self._initDataLineEdits()
        self._initTable()

    def _initLineEdits(self):
        self._selectedFolderLineEdit.setText(DEFAULT_FOLDER_STRING)
        self._selectedFileTypeLineEdit.setText(DEFAULT_EXT_STRING)
        self._selectedDateLineEdit.setText(DEFAULT_DATE_STRING)
        
    def _initDataLineEdits(self):
        self._fileStatusLabel.setText(DEFAULT_FILESTATUS_STRING)
        self._sumTotalLinesLineEdit.setText(DEFAULT_DATALINEEDIT_STRING)
        self._sumActualLinesLineEdit.setText(DEFAULT_DATALINEEDIT_STRING)
        self._nbPrjDaysLineEdit.setText(DEFAULT_DATALINEEDIT_STRING)
        self._avgLinesPerDayLineEdit.setText(DEFAULT_DATALINEEDIT_STRING)
        self._avgLinesPerHourLineEdit.setText(DEFAULT_DATALINEEDIT_STRING)
        self._codeDensityLineEdit.setText(DEFAULT_DATALINEEDIT_STRING)
        
        for w in [  self._selectedFolderLineEdit, self._selectedFileTypeLineEdit,
                    self._selectedDateLineEdit, self._sumTotalLinesLineEdit,
                    self._sumActualLinesLineEdit,self._nbPrjDaysLineEdit,
                    self._avgLinesPerDayLineEdit,self._avgLinesPerDayLineEdit,
                    self._avgLinesPerHourLineEdit, self._codeDensityLineEdit]:
            
            w.setAlignment(QtCore.Qt.AlignCenter)
    


    def _initTable(self):
        self._dataTableItem = QtGui.QTableWidgetItem()
        self._dataTableBtn = QtGui.QPushButton()
        
        self._dataTable.setRowCount(1)
        self._dataTable.setColumnCount(3)
        self._dataTable.setHorizontalHeaderLabels(["File Name", "Total Lines", "Actual Lines"])
        self._dataTable.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._dataTable.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._dataTable.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._dataTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self._dataTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self._dataTable.horizontalHeader().setVisible(False)
        self._dataTable.verticalHeader().setVisible(False)
        self._dataTable.setItem(0, 0, self._dataTableItem)
        self._dataTableBtn.setStyleSheet("QPushButton {background-color : \
                                        rgb(58, 84, 92); font-size: 12pt;}")
        self._dataTableBtn.setText("|  N o    D a t a  |")
        self._dataTable.setCellWidget(0,0, self._dataTableBtn)
        self._dataTable.setSpan(0,0, self._dataTable.rowCount(), self._dataTable.columnCount())
        
    def _hideDataTableBtn(self):
        self._dataTable.horizontalHeader().setVisible(True)
        self._dataTable.setCellWidget(0,0, None)
        self._dataTable.setSpan(0, 0, 1, 1)
    

    def _connectSignals(self):
        # Implemented double click event filter in the Widget Module
        EnableDoubleClickOnWidget(self._selectedFolderLineEdit).connect(self._handleRootFolderChange)
        EnableDoubleClickOnWidget(self._selectedFileTypeLineEdit).connect(self._handleFileTypeChange)
        EnableDoubleClickOnWidget(self._selectedDateLineEdit).connect(self._handleDateChange)
        
        # Implemented a F2 Press Event in the Widget Module
        self.connect(self._selectedFolderLineEdit, QtCore.SIGNAL("F2Pressed"), self._handleRootFolderChange)
        self.connect(self._selectedFileTypeLineEdit, QtCore.SIGNAL("F2Pressed"), self._handleFileTypeChange)
        self.connect(self._selectedDateLineEdit, QtCore.SIGNAL("F2Pressed"), self._handleDateChange)
        
        self._okBtn.clicked.connect(self._okBtnOnClicked)
        self._cancelBtn.clicked.connect(self._cancelBtnOnClicked)
        self._dataTable.doubleClicked.connect(self._handleTableDoubleClick)

    def _clearData(self):
        self._clearDataLineEdits()
        self._clearDataTable()
    
    def _clearDataLineEdits(self):
        self._initDataLineEdits()

    def _clearDataTable(self):
        self._dataTable.clear()
        self._initTable()

    def _clearRootFolder(self):
        self._clearData()
        self._rootDir = DEFAULT_FOLDER_STRING
        self._selectedFolderLineEdit.setText(DEFAULT_FOLDER_STRING)

    
    def _clearFileExt(self):
        self._clearData()
        self._fileExt = []
        self._selectedFileTypeLineEdit.setText(DEFAULT_EXT_STRING)
        
    def _clearDate(self):
        self._clearData()
        self._day = 0
        self._month = 0
        self._year = 0
        self._selectedDateLineEdit.setText(DEFAULT_DATE_STRING)
        
    
    def _handleRootFolderChange(self):
        self._clearRootFolder()
        
        fg = QtGui.QFileDialog()
        fg.setFileMode(QtGui.QFileDialog.Directory)
        fg.setOptions(QtGui.QFileDialog.ShowDirsOnly)
        fg.setOption(QtGui.QFileDialog.ShowDirsOnly)
        f = str(fg.getExistingDirectory(self, 'Select Root Folder',
                                        os.path.abspath(ROOT_DIR),
                                        QtGui.QFileDialog.ShowDirsOnly))

        if not f:
            return
        
        if self._rootDir != f:
            self._rootDirChanged = True

        self._rootDir = str(f)
        self._selectedFolderLineEdit.setText(str(f))
        self._selectedFolderLineEdit.setToolTip(str(f))
        self._selectedFolderLineEdit.setCursorPosition(0)
        
        
    
    def _handleFileTypeChange(self):
        self._clearFileExt()

        
        if not hasattr(self, 'ft'):
            self.ft = FileTypeWidget()
        else:
            self.ft = None
            self.ft = FileTypeWidget()
    
        self.ft.setGeometry(100, 100, 100, 250)
        self.ft.exec_()
        
        # The modal dialog box for file type has been closed just now
        # grabbing the data from the file type widget
        self._fileExt = self.ft._fileExt
        self._selectedFileTypeLineEdit.setText(self.ft._displayString)
        self._selectedFileTypeLineEdit.setToolTip(self.ft._displayString)
        self._selectedFileTypeLineEdit.setCursorPosition(0)
        
        if len(self._fileExt) == 0:
            self._clearFileExt()
            

    def _handleDateChange(self):
        self._clearDate()
        
        if not hasattr(self, 'ft'):
            self.cw = CalendarWidget()
        else:
            self.cw = None
            self.cw = CalendarWidget()
    
        
        self.cw.setGeometry(100, 100, 300, 250)
        self.cw.exec_()
        
        self._day = self.cw._day
        self._month = self.cw._month
        self._year = self.cw._year
        self._selectedDateLineEdit.setText(self.cw._dateString)
        self._selectedDateLineEdit.setCursorPosition(0)
        
        if self._day == 0 or self._month == 0 or self._year == 0:
            self._clearDate()
            
    
    def _handleTableDoubleClick(self, item):
        if item.column() != 0:
            return            
            
        path = self._data[item.row()][2]

        if sys.platform=='win32':
            subprocess.Popen(r'explorer /select,"%s"' % path)
        
        elif sys.platform=='darwin':
            subprocess.Popen(['open', path])
        
        else:
            try:
                subprocess.Popen(['xdg-open', path])
            except OSError:
                pass
                # er, think of something else to try
                # xdg-open *should* be supported by recent Gnome, KDE, Xfce
                    
    
    def _setAnalyticDataFromMainWindow(self, inFolder, recentSearchData):
        self._clearRootFolder()
        self._clearFileExt()
        self._clearDate()
        
        self._rat = None
        
        self._rootDir = inFolder
        self._selectedFolderLineEdit.setText(inFolder)
        self._selectedFolderLineEdit.setToolTip(inFolder)        
        
        self._fileExt = recentSearchData[inFolder]['ext']
        self._selectedFileTypeLineEdit.setText(' | '.join(self._fileExt))
        self._selectedFileTypeLineEdit.setToolTip(' | '.join(self._fileExt))        
        
        
        self._day = recentSearchData[inFolder]['startDate']
        self._month = recentSearchData[inFolder]['startMonth']
        self._year = recentSearchData[inFolder]['startYear']
        
        date = QtCore.QDate(self._year, self._month, self._day)
        self._selectedDateLineEdit.setText(date.toString())
        
        self._okBtnOnClicked()
        
    
    def _okBtnOnClicked(self):
        QtGui.QApplication.processEvents()

        self._clearData()
        self._hasError = False
        self._animCounter = 0
        self._animTimerCounter = 0
        self._animatedStr = PROGRESS_ANIM_TEXT_LIST[0]        

        folder = ''
        if self._rootDir != DEFAULT_FOLDER_STRING:
            folder = self._rootDir

        self._rat = RunAnalyticsTask(   folder=folder,
                                        ext=self._fileExt,
                                        startDate=self._day,
                                        startMonth=self._month,
                                        startYear=self._year
                                    )

        self._rat.runAnalytics()
        
        
        # Signals that will be emitted from CodeLines to sync task process
        self.connect(self._rat, QtCore.SIGNAL("update(PyQt_PyObject)"), self._informOfUpdate)
        self.connect(self._rat, QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._informOfErrorOccured)        
        self.connect(self._rat, QtCore.SIGNAL("finished()"), self._informOfFinished)
        
        
        
    def _informOfErrorOccured(self, errStr):
        # This function is called even when the signal is
        # not emitted from an error in the code lines module, this is strange behaviour
        # or some bug!! maybe.
        # In order to make sure that some error has actually occured
        # we have to check the length of the error string to make sure
        # we are not setting self._hasError from some ghost call.
        if errStr:
            self._hasError = True

        self._dataTableBtn.setText(errStr)
    
    def _informOfUpdate(self, fileName):
        s = 'A N A L Y S I N G    F I L E S'
        s += '\n'
        
        if (self._animTimerCounter % self._nbHoldFrame == 0):
            self._animatedStr = PROGRESS_ANIM_TEXT_LIST[self._animCounter]
            self._animCounter += 1
            if(self._animCounter == len(PROGRESS_ANIM_TEXT_LIST) - 1):
                self._animCounter = 0
        
        s += self._animatedStr
        s += '\n'
        s += str(fileName)
        self._dataTableBtn.setText(s)
        
        self._animTimerCounter += 1
    
    def _informOfFinished(self):
        if self._hasError:
            return

        self._dataTableBtn.setText('DONE')
        self._data, self._nbPrjDays, self._avgLinesPerDay, self._avgLinesPerHour, self._codeDensity = self._rat.data
        self._fillData()
        
        self._rsd._addData([self._rootDir, self._fileExt,
                            self._day, self._month,
                            self._year,])
        
        self._ranSignal.emit()
        

    def _fillData(self):
        self._fillDataTable()
        self._fillDataLineEdits()


    def _fillDataTable(self):
        self._hideDataTableBtn()
        self._dataTable.setRowCount(len(self._data))
        
        self._sumTotalLine = 0
        self._sumActualLine = 0
        
        color = [0, 0, 0]
        
        for n, t in enumerate(self._data):
            if n % 2 == 0:
                color = [58, 84, 92]
            else:
                color = [57, 67, 76]
            lineData, scriptName, path = t
            actualLines, totalLines = lineData
            self._sumTotalLine += totalLines
            self._sumActualLine += actualLines
            
            for m, d in enumerate([scriptName, totalLines, actualLines]):
                d = str(d)
                newItem = QtGui.QTableWidgetItem(d)
                newItem.setFlags(QtCore.Qt.ItemIsEnabled)
                brush = QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2]))
                brush.setStyle(QtCore.Qt.SolidPattern)
                newItem.setBackground(brush)
                newItem.setForeground(QtGui.QColor(255, 244, 237))
                newItem.setToolTip(path)
                if m == 0:
                    newItem.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
                else:
                    newItem.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            
                self._dataTable.setItem(n, m, newItem)
        

    def _fillDataLineEdits(self):
        self._fileStatusLabel.setText('<b>Found (%s) files</b>   <i>(Double click file name to show in explorer)</i>' % len(self._data))
        self._sumTotalLinesLineEdit.setText(str(self._sumTotalLine))
        self._sumActualLinesLineEdit.setText(str(self._sumActualLine))
        self._nbPrjDaysLineEdit.setText(str(self._nbPrjDays))
        self._avgLinesPerDayLineEdit.setText(str(self._avgLinesPerDay))
        self._avgLinesPerHourLineEdit.setText(str(self._avgLinesPerHour))
        self._codeDensityLineEdit.setText('%s %%' % str(self._codeDensity))
        
        
        for w in [  self._sumTotalLinesLineEdit, self._sumActualLinesLineEdit,
                    self._nbPrjDaysLineEdit, self._avgLinesPerDayLineEdit,
                    self._avgLinesPerHourLineEdit, self._codeDensityLineEdit]:
            
            w.setAlignment(QtCore.Qt.AlignRight)
    
    def _cancelBtnOnClicked(self):
        QtCore.QCoreApplication.instance().quit()
        
        
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
        
                
        
class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self._rsd = RecentSearchData()
        
        mainWidget = QtGui.QFrame()
        self._mainWidget = MainWidget()
        
        # A signal from MainWidget will be emitted after running
        # this is connect to slot in the MainWindow to update recent menu
        self._mainWidget._ranSignal.connect(self._updateRecentSearchMenu)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self._mainWidget)
        mainWidget.setLayout(mainLayout)
        
        clearRecentSearchesAction = QtGui.QAction('Clea&r Recent', self)
        clearRecentSearchesAction.setShortcut('Ctrl+R')
        clearRecentSearchesAction.setStatusTip('Clear Recent Searches')
        clearRecentSearchesAction.triggered.connect(self._onClearRecentSearches)
        
        quitAction = QtGui.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit Application')
        quitAction.triggered.connect(self._onQuit)
        
        
        defaultStyleAction = QtGui.QAction('Default', self)
        defaultStyleAction.setShortcut('Ctrl+1')
        defaultStyleAction.setStatusTip('Default Style Theme : Windowsvista on Windows OS else Plastique')
        defaultStyleAction.triggered.connect(self._onDefaultStyleAction)

        dark01StyleAction = QtGui.QAction('Dark01', self)
        dark01StyleAction.setShortcut('Ctrl+2')
        dark01StyleAction.setStatusTip('Generic Dark01 Style Theme')
        dark01StyleAction.triggered.connect(self._onDark01StyleAction)

        dark02StyleAction = QtGui.QAction('Dark02', self)
        dark02StyleAction.setShortcut('Ctrl+3')
        dark02StyleAction.setStatusTip('Generic Dark02 Style Theme')
        dark02StyleAction.triggered.connect(self._onDark02StyleAction)

        dark03StyleAction = QtGui.QAction('Dark03', self)
        dark03StyleAction.setShortcut('Ctrl+4')
        dark03StyleAction.setStatusTip('Generic Dark03 Style Theme')
        dark03StyleAction.triggered.connect(self._onDark03StyleAction)
        
        aboutAction = QtGui.QAction('About', self)
        aboutAction.triggered.connect(self._onAboutAction)
        
        licenseAction = QtGui.QAction('View License', self)
        licenseAction.triggered.connect(self._onViewLicenseAction)


        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        self._recentSearchMenu = fileMenu.addMenu('Run Recent Analytics')
        self._updateRecentSearchMenu()
        
        fileMenu.addAction(clearRecentSearchesAction)
        fileMenu.addAction(quitAction)
        
        editMenu = menubar.addMenu('&Edit')
        themeMenu = editMenu.addMenu('A&pply Themes')
        themeMenu.addAction(defaultStyleAction)
        themeMenu.addAction(dark01StyleAction)
        themeMenu.addAction(dark02StyleAction)
        themeMenu.addAction(dark03StyleAction)
        
        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(aboutAction)
        aboutMenu.addAction(licenseAction)

        self.setCentralWidget(mainWidget)
        self.move(100, 100)
        self.setWindowTitle(WIN_TITLE)
        self.setMinimumSize(1000, 600)
        
        StyleSheet().setColor(self, app=QtCore.QCoreApplication.instance())
        StyleSheet().setColor(self._mainWidget)   
        
    def _onDefaultStyleAction(self):
        self._setTheme('')

    def _onDark01StyleAction(self):
        self._setTheme('dark01')

    def _onDark02StyleAction(self):
        self._setTheme('dark02')

    def _onDark03StyleAction(self):
        self._setTheme('dark03')

    def _setTheme(self, theme=''):
        ss = StyleSheet()
        ss._writePrefs(pref=theme)
        ss.setColor(self._mainWidget)
        ss.setColor(self, app= QtCore.QCoreApplication.instance())
        
        
    def _onClearRecentSearches(self):
        self._recentSearchMenu.clear()
        self._rsd._clearAll()
        
    def _updateRecentSearchMenu(self):
        self._recentSearchMenu.clear()
        recentSearchData = self._rsd._fetchRecent()
        keys = recentSearchData.keys()
        
        folders = []
        for folder, data in recentSearchData.iteritems():
            order = data['order']
            
            folders.append((order, folder))
            
        folders.sort()

        for index, t in enumerate(folders):
            _, folder = t
            fileAction = QtGui.QAction('%s. %s' % (index + 1, folder), self)
            fileAction.triggered.connect(functools.partial(self._fileOpenMappedSlot, folder))
            self._recentSearchMenu.addAction(fileAction)
            

    def _fileOpenMappedSlot(self, inFolder):
        if not os.path.exists(inFolder):
            self._rsd._removeData(inFolder)
            self._showErrorText(err='The folded <%s> does not exist.\nRemoving it from the recent search menu.' % inFolder)
            self._updateRecentSearchMenu()
            return

        self._mainWidget._setAnalyticDataFromMainWindow(inFolder, self._rsd._fetchRecent())
        
    def _onAboutAction(self):
        if not hasattr(self, 'tw'):
            self.ab = AboutWidget()
        else:
            self.ab = None
            self.ab = AboutWidget()

        self.ab.show() 
    
    def _onViewLicenseAction(self):
        if not hasattr(self, 'tw'):
            self.tw = TextWidget()
        else:
            self.tw = None
            self.tw = TextWidget()
    
        self.tw.textEdit.setText(LICENSE_TEXT)
        self.tw.setWindowTitle('L I C E N S E')
        self.tw.setFixedSize(400, 300)
        self.tw.show()    
    
    def _showErrorText(self, winTitle="Folder does not exist", err=""):
        if not hasattr(self, 'tw'):
            self.tw = TextWidget()
        else:
            self.tw = None
            self.tw = TextWidget()
    
        self.tw.textEdit.setText(err)
        self.tw.setWindowTitle(winTitle)
        self.tw.setGeometry(100, 100, 100, 100)
        self.tw.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self._onQuit()
        
    def _onQuit(self):
        QtCore.QCoreApplication.instance().quit()
        

def run():
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    ico = os.path.join(ROOT_DIR, 'rsc/_icos')
    app.setWindowIcon(QtGui.QIcon(ico))    
    mw.show()
    mw.raise_()
    app.exec_()