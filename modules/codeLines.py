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
from datetime import date
from PyQt4 import QtCore, QtGui
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.join(__file__)), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from gui.logger import Logger


class CodeLines(object):
    def __init__(self, qThread=None, folder="", ext=[], startDate=0, startMonth=0, startYear=0, *args, **kwargs):
        super(CodeLines, self).__init__(*args, **kwargs)
        
        # Supplied Arguments
        self._qThread = qThread
        self._folder = folder
        self._ext = ext
        self._startDate = startDate
        self._startMonth = startMonth
        self._startYear = startYear

        # Data to Calculate
        self._data = []
        self._prjStartDate = None        
        self._nbPrjDays = 0
        self._nbTotalLines = 0
        self._nbActualLines = 0
        self._codeDensity = 0.0
        self._avgLinesPerDay = 0
        self._avgLinesPerHour = 0
        self._hasError = False
        self._errStr = ''
        
        self._findAll = False
        if '*.*' in self._ext:
            self._findAll = True

        # Initialization Methods
        if not self._qThread:
            self._assert()
            self._generateData()
    
    def runThread(self):
        self._assert()
        self._generateData()

        return self.getData()

    def _assert(self):
        if self._folder == '':
            self._hasError = True
            self._errStr = 'No script folder provided!'
            
            if self._qThread:
                self._qThread.emit(QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._errStr)
            
            return
        
        if not os.path.exists(self._folder):
            self._hasError = True
            self._errStr = 'The folder <%s> does not exist!' % self._folder
            
            if self._qThread:
                self._qThread.emit(QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._errStr)

            return


        if len(self._ext) == 0:
            self._hasError = True
            self._errStr = 'No script file extensions provided!'

            if self._qThread:
                self._qThread.emit(QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._errStr)

            
            return
        
        try:
            self._prjStartDate = date(self._startYear, self._startMonth, self._startDate)
            self._nbPrjDays = (date.today() - self._prjStartDate).days
            
            if self._nbPrjDays <= 0:
                self._hasError = True
                self._errStr = 'Project Start Date should be smaller than current date !'

            if self._qThread:
                self._qThread.emit(QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._errStr)
                
            
        except:
            self._hasError = True
            self._errStr = 'Supplied Date parameters are not valid!'

            if self._qThread:
                self._qThread.emit(QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._errStr)
            
            return        
            
    
    def _generateData(self):
        if self._hasError:
            return

        for root, dirs, files in os.walk(self._folder):
            
            for f in files:
                fName, ext = os.path.splitext(f)
                
                openPath = os.path.abspath(os.path.join(root, f))
                
                if self._qThread:
                    self._qThread.emit(QtCore.SIGNAL("update(PyQt_PyObject)"), str(f))
                    
                
                if not self._findAll:
                    if ext not in self._ext:
                        continue
                
                
                with open(openPath) as file:
                    lines = file.readlines()
                    nbLines = len(lines)
                    n = 0
                    
                    for line in lines:
                        if not str(line).strip():
                            continue
                        
                        n += 1
    
                    self._data.append(((n, nbLines), str(f), str(os.path.join(root, f))))
                    self._nbTotalLines += nbLines
                    self._nbActualLines += n

        self._data.sort(reverse=True)

        if len(self._data) == 0:
            self._hasError = True
            self._errStr = self._wrap(self._folder, 'No Script files found in the root folder:')
            
            if self._qThread:
                self._qThread.emit(QtCore.SIGNAL("errorOccured(PyQt_PyObject)"), self._errStr)

            return

        self._codeDensity = (round((self._nbActualLines / float(self._nbTotalLines)) * 100, 2))
        self._avgLinesPerDay =  int(self._nbActualLines / float(self._nbPrjDays))
        self._avgLinesPerHour = int(self._avgLinesPerDay / 8.0)
        
        
    @staticmethod
    def _wrap(folderPath, defaultStr):
        result = ''
        if len(folderPath) > len(defaultStr):
            result = folderPath[:len(defaultStr) - 2]
            result += '... '
            
        return '%s\n\n%s' % (defaultStr, result)
    
    def getData(self):
        return self._data, self._nbPrjDays, self._avgLinesPerDay, self._avgLinesPerHour, self._codeDensity