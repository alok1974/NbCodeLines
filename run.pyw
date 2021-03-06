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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if not ROOT_DIR in sys.path:
    sys.path.append(ROOT_DIR)

if __name__ == "__main__":
    from gui.mainWindow import run
    run()
