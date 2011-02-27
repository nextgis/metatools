"""
/***************************************************************************
 Metatools
                                 A QGIS plugin
 Metadata browser/editor
                              -------------------
        begin                : 2011-02-21
        copyright            : (C) 2011 by NextGIS
        email                : info@nextgis.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# Initialize Qt resources from file resources.py
import resources

#Import sys libs
from os import path

# Import the code for the dialogs
from metatoolsdialog import MetatoolsDialog
from metatoolsviewer import MetatoolsViewer
from metatoolseditor import MetatoolsEditor

#Import plugin code
import utils
from standard import MetaInfoStandard

class MetatoolsPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # Get QGIS version
        try:
            self.QgisVersion = unicode(QGis.QGIS_VERSION_INT)
        except:
            self.QgisVersion = unicode(QGis.qgisVersion)[ 0 ]
        
        # Get plugin folder
        userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/Metatools"
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/Metatools"

        if QFileInfo(userPluginPath).exists():
            self.pluginPath=userPluginPath
        else:
            self.pluginPath=systemPluginPath

        # i18n support
        overrideLocale = QSettings().value("locale/overrideFlag", QVariant(False)).toBool()
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", QVariant("")).toString()

        self.localePath = self.pluginPath + "/i18n/metatools_" + localeFullName + ".qm"
        
        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


    def initGui(self):
        # Create editAction that will start editor window
        self.editAction = QAction(QIcon(":/plugins/metatools/icon.png"), QCoreApplication.translate("Metatools", "Edit metadata"), self.iface.mainWindow())
        # connect the editAction to the doEdit method
        QObject.connect(self.editAction, SIGNAL("triggered()"), self.doEdit)

        # Create viewAction that will start viewer window
        self.viewAction = QAction(QIcon(":/plugins/metatools/icon.png"), QCoreApplication.translate("Metatools", "View metadata"), self.iface.mainWindow())
        # connect the viewAction to the doView method
        QObject.connect(self.viewAction, SIGNAL("triggered()"), self.doView)

        # Create configAction that will start plugin configuration
        self.configAction = QAction(QIcon(":/plugins/metatools/icon.png"), QCoreApplication.translate("Metatools", "Configure metadata plugin"), self.iface.mainWindow())
        # connect the configAction to the doConfigure method
        QObject.connect(self.configAction, SIGNAL("triggered()"), self.doConfigure)

        # Add menu item
        self.iface.addPluginToMenu("&Metatools", self.editAction)
        self.iface.addPluginToMenu("&Metatools", self.viewAction)
        self.iface.addPluginToMenu("&Metatools", self.configAction)

        # Add toolbar
        self.toolBar = self.iface.addToolBar(QCoreApplication.translate("Metatools", "Metatools"))
        self.toolBar.setObjectName(QCoreApplication.translate("Metatools", "Metatools"))

        self.toolBar.addAction(self.editAction)
        self.toolBar.addAction(self.viewAction)
        self.toolBar.addAction(self.configAction)



    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&Metatools", self.editAction)
        self.iface.removePluginMenu("&Metatools", self.viewAction)
        self.iface.removePluginMenu("&Metatools", self.configAction)
        del self.toolBar

    # run method that performs all the real work
    def doEdit(self):
        # create and show the dialog
        dlg = MetatoolsEditor()
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass

    # View metadata
    def doView(self):
        # shortcuts
        translatedMetatools=QCoreApplication.translate("Metatools", "Metatools")
        mainWindow=self.iface.mainWindow()
        
        # get active layer
        layer=self.iface.activeLayer()
        if not layer:
            QMessageBox.information(mainWindow, translatedMetatools, 'Choose any map layer')
            return
        
        # check layer type
        if layer.type()==QgsMapLayer.RasterLayer:
            pass
        else:
            if layer.type()==QgsMapLayer.VectorLayer:
                QMessageBox.warning(mainWindow,translatedMetatools, QCoreApplication.translate("Metatools", "Vector layers are not supported yet!"))
            else:
                QMessageBox.critical(mainWindow, translatedMetatools, QCoreApplication.translate("Metatools", "Unsupported layer type!"))
            return
        
        #TODO: check layer DS type (local, DB, service)
        
        # get metafile path 
        metaFilePath=utils.getMetafilePath(layer)
        
        # check metadata file exists
        #TODO: create suggestion
        if not path.exists(metaFilePath):
            QMessageBox.warning(mainWindow, translatedMetatools, "The layer does not have metadata!")
            return
        
        # check matadata standard
        standard=MetaInfoStandard.tryDetermineStandard(metaFilePath)
        if standard != MetaInfoStandard.ISO19138:
            QMessageBox.critical(mainWindow, translatedMetatools, QCoreApplication.translate("Metatools", "Unsupported metadata standard! Only ISO19139 support now! "))
            return
                
        #TODO: validate metadata file
        
        # get xsl file path
        #TODO: select xls by metadata type and settings
        xsltFilePath=self.pluginPath+'/xsl/iso19139.xsl'
        
        #------------ create and show the dialog
        #TODO: need singleton!        
        dlg = MetatoolsViewer()
        dlg.setContent(metaFilePath,xsltFilePath)
        dlg.show()
        result = dlg.exec_()
        
        """
        #for dock widget
        if not self.metadataDock:
            self.metadataDock = QDockWidget( "Metadata", self.iface.mainWindow())
            self.metadataDock.setObjectName("infoPanel")
            self.metadataDock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea)
            self.metadataDock.setContentsMargins ( 6, 6, 6, 6 )
            #self.metadataDock.setWidget( ??? ) #need remake window to control!!!
            self.iface.mainWindow().addDockWidget( Qt.RightDockWidgetArea, self.metadataDock )
        
        self.metadataDock.widget().setContent(???)    
        self.metadataDock.show()
        """

    def doConfigure(self):
        # create and show the dialog
        dlg = MetatoolsDialog()
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass