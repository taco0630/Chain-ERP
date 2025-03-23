from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit,QTextEdit, QPlainTextEdit, QPushButton, QStatusBar, QTableWidget, QTableWidgetItem, QDialog, QFileDialog, QVBoxLayout, QWidget, QAbstractItemView
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 

import req
from orderformui import orderformui
from logisticsformui import logisticsformui
from signininventoryui import signininventoryui
from skureviewui import skureviewui

import bcrypt
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
import base64, hashlib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from datetime import date
from datetime import datetime
import time
import sys, os, logging, random, json, requests, pyotp
import pyperclip
import azure.cosmos.cosmos_client as cosmos_client
import pandas as pd
from pandas import json_normalize
import numpy as np
from barcode import EAN13
from barcode.writer import ImageWriter

class appui(QMainWindow):

    timer = QTimer()

    totpkey = pyotp.random_base32().replace("'","")
    totp = pyotp.TOTP(totpkey, interval=900)
    code = totp.at(int(time.time()))

    apptitle = req.apptitle

    uri = req.azure_supplychain_uri
    rkey = req.azure_supplychain_readkey
    rwkey = req.azure_supplychain_readwritekey

    demouri = req.demo_azure_supplychain_uri
    demorkey = req.demo_azure_supplychain_readkey
    demorwkey = req.demo_azure_supplychain_readwritekey

    getaccessurl = req.gcp_getaccesslevel_url
    setaccessurl = req.gcp_setpassword_url
    
    hrdbname = req.azure_hrmanagement_db
    hruri = req.azure_hrmanagement_uri
    hrrkey = req.azure_hrmanagement_readkey
    hrrwkey = req.azure_hrmanagement_readwritekey
    sgkey = req.sendgrid_key2

    inventorydb = req.azure_inventory_db
    inventorycr = req.azure_inventory_cr 
    productdb = req.azure_product_category_db 
    productcr = req.azure_product_cr
    productcategorycr = req.azure_productcategory_cr
    supplierdb = req.azure_supplier_order_db 
    suppliercr = req.azure_supplier_cr
    ordercr = req.azure_order_cr
    vendordb = req.azure_vendor_logistic_order_db 
    logisticcr = req.azure_logistic_cr 
    vendorcr = req.azure_vendor_cr

    demoinventorydb = req.demo_azure_inventory_db
    demoinventorycr = req.demo_azure_inventory_cr 
    demoproductdb = req.demo_azure_product_category_db 
    demoproductcr = req.demo_azure_product_cr
    demoproductcategorycr = req.demo_azure_productcategory_cr
    demosupplierdb = req.demo_azure_supplier_order_db 
    demosuppliercr = req.demo_azure_supplier_cr
    demoordercr = req.demo_azure_order_cr
    demovendordb = req.demo_azure_vendor_logistic_order_db 
    demologisticcr = req.demo_azure_logistic_cr 
    demovendorcr = req.demo_azure_vendor_cr

    def openappwindow(self, MainWindow, username, role, lang):

        stlan = ''
        if 'ZHTW' in lang: 
            uic.loadUi("App_UI_ZHTW.ui",self)
            stlan = ', ZHTW繁中'
        elif 'ZHCN' in lang: 
            uic.loadUi("App_UI_ZHCN.ui",self)
            stlan = ', ZHCN简中'
        else: 
            uic.loadUi("App_UI.ui",self)

        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle(appui.apptitle)
        
        self.label_username.setText(self.label_username.text() + " "+ username + '('+role+stlan+')')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.click_pushButton_logout)
        self.timer.start(1800000)

        #Access control
        if('ReadOnly' in role):
            self.supplier_pushButton_batchUpload.setVisible(False)
            self.vendor_pushButton_batchUpload.setVisible(False)
            self.productcatogory_pushButton_batchUpload.setVisible(False)
            self.product_pushButton_batchUpload.setVisible(False)
            self.order_pushButton_newOrder.setVisible(False)
            self.order_pushButton_batchUpload.setVisible(False)
            self.logistics_pushButton_newLogistics.setVisible(False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('BuyerManager' in role):
            self.productcatogory_pushButton_batchUpload.setVisible(False)
            self.tabs_main.setTabVisible(6, False)
        elif('Buyer' in role):
            self.supplier_pushButton_batchUpload.setVisible(False)
            self.vendor_pushButton_batchUpload.setVisible(False)
            self.productcatogory_pushButton_batchUpload.setVisible(False)
            self.product_pushButton_batchUpload.setVisible(False)
            self.order_pushButton_newOrder.setVisible(False)
            self.order_pushButton_batchUpload.setVisible(False)
            self.tabs_main.setTabVisible(6, False)
        elif('OperationManager' in role):
            self.tabs_main.setTabVisible(0, False)
            self.order_pushButton_newOrder.setVisible(False)
            self.order_pushButton_batchUpload.setVisible(False)
            self.logistics_pushButton_newLogistics.setVisible(False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('OperationOfficer' in role):
            self.tabs_main.setTabVisible(0, False)
            self.vendor_pushButton_batchUpload.setVisible(False)
            self.productcatogory_pushButton_batchUpload.setVisible(False)
            self.product_pushButton_batchUpload.setVisible(False)
            self.order_pushButton_newOrder.setVisible(False)
            self.order_pushButton_batchUpload.setVisible(False)
            self.logistics_pushButton_newLogistics.setVisible(False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('MarketingManager' in role):
            self.tabs_main.setTabVisible(0, False)
            self.tabs_main.setTabVisible(1, False)
            self.tabs_main.setTabVisible(2, False)
            self.product_pushButton_batchUpload.setVisible(False)
            self.tabs_main.setTabVisible(4, False)
            self.tabs_main.setTabVisible(5, False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('Marketing' in role):
            self.tabs_main.setTabVisible(0, False)
            self.tabs_main.setTabVisible(1, False)
            self.tabs_main.setTabVisible(2, False)
            self.product_pushButton_batchUpload.setVisible(False)
            self.tabs_main.setTabVisible(4, False)
            self.tabs_main.setTabVisible(5, False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('WarehouseManager' in role):
            self.tabs_main.setTabVisible(0, False)
            self.tabs_main.setTabVisible(1, False)
            self.tabs_main.setTabVisible(2, False)
            self.tabs_main.setTabVisible(3, False)
            self.order_pushButton_newOrder.setVisible(False)
            self.order_pushButton_batchUpload.setVisible(False)
            self.logistics_pushButton_newLogistics.setVisible(False)
        elif('WarehouseOfficer' in role):
            self.tabs_main.setTabVisible(0, False)
            self.tabs_main.setTabVisible(1, False)
            self.tabs_main.setTabVisible(2, False)
            self.tabs_main.setTabVisible(3, False)
            self.order_pushButton_newOrder.setVisible(False)
            self.order_pushButton_batchUpload.setVisible(False)
            self.logistics_pushButton_newLogistics.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('CustomerServiceManager' in role):
            self.tabs_main.setTabVisible(0, False)
            self.tabs_main.setTabVisible(1, False)
            self.tabs_main.setTabVisible(2, False)
            self.tabs_main.setTabVisible(3, False)
            self.tabs_main.setTabVisible(4, False)
            self.tabs_main.setTabVisible(5, False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)
        elif('CustomerService' in role):
            self.tabs_main.setTabVisible(0, False)
            self.tabs_main.setTabVisible(1, False)
            self.tabs_main.setTabVisible(2, False)
            self.tabs_main.setTabVisible(3, False)
            self.tabs_main.setTabVisible(4, False)
            self.tabs_main.setTabVisible(5, False)
            self.inventory_pushButton_signInInventory.setVisible(False)
            self.inventory_pushButton_skuReview.setVisible(False)
            self.inventory_pushButton_batchUpload.setVisible(False)

        self.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;}")
        self.pushButton_logout.clicked.connect(self.click_pushButton_logout)
       
        self.supplier_pushButton_search.clicked.connect(self.click_supplier_pushButton_search)
        self.supplier_pushButton_last100Updated.clicked.connect(self.click_supplier_pushButton_last100Updated)
        self.supplier_pushButton_last300Updated.clicked.connect(self.click_supplier_pushButton_last300Updated)
        self.supplier_pushButton_last100Added.clicked.connect(self.click_supplier_pushButton_last100Added)
        self.supplier_pushButton_last300Added.clicked.connect(self.click_supplier_pushButton_last300Added)
        self.supplier_pushButton_generateCSV.clicked.connect(self.click_supplier_pushButton_generateCSV)
        self.supplier_pushButton_printPostLabel.clicked.connect(self.click_supplier_pushButton_printPostalLabel)
        self.supplier_pushButton_printBarcode.clicked.connect(self.click_supplier_pushButton_generateBarcode)
        self.supplier_pushButton_batchUpload.clicked.connect(self.click_supplier_pushButton_batchUpload)

        self.vendor_pushButton_search.clicked.connect(self.click_vendor_pushButton_search)
        self.vendor_pushButton_generateCSV.clicked.connect(self.click_vendor_pushButton_generateCSV)
        self.vendor_pushButton_batchUpload.clicked.connect(self.click_vendor_pushButton_batchUpload)

        self.productcategory_pushButton_listAll.clicked.connect(self.click_productcategory_pushButton_listAll)
        self.productcategory_pushButton_generateCSV.clicked.connect(self.click_productcategory_pushButton_generateCSV)
        self.productcatogory_pushButton_batchUpload.clicked.connect(self.click_productcategory_pushButton_batchUpload)

        self.product_pushButton_search.clicked.connect(self.click_product_pushButton_search)
        self.product_pushButton_last100Updated.clicked.connect(self.click_product_pushButton_last100Updated)
        self.product_pushButton_last300Updated.clicked.connect(self.click_product_pushButton_last300Updated)
        self.product_pushButton_last100Added.clicked.connect(self.click_product_pushButton_last100Added)
        self.product_pushButton_last300Added.clicked.connect(self.click_product_pushButton_last300Added)
        self.product_pushButton_generateCSV.clicked.connect(self.click_product_pushButton_generateCSV)
        self.product_pushButton_printBarcode.clicked.connect(self.click_product_pushButton_generateBarcode)
        self.product_pushButton_batchUpload.clicked.connect(self.click_product_pushButton_batchUpload)

        self.order_pushButton_search.clicked.connect(self.click_order_pushButton_search)
        self.order_pushButton_last100orders.clicked.connect(self.click_order_pushButton_last100Updated)
        self.order_pushButton_last300orders.clicked.connect(self.click_order_pushButton_last300Updated)
        self.order_pushButton_viewDetails.clicked.connect(self.click_order_pushButton_viewDetails)
        self.order_pushButton_newOrder.clicked.connect(self.click_order_pushButton_newOrder)
        self.order_pushButton_generateCSV.clicked.connect(self.click_order_pushButton_generateCSV)
        self.order_pushButton_batchUpload.clicked.connect(self.click_order_pushButton_batchUpload)

        self.logistics_pushButton_search.clicked.connect(self.click_logistics_pushButton_search)
        self.logistics_pushButton_last100fullfilled.clicked.connect(self.click_logistics_pushButton_last100Fulfilled)
        self.logistics_pushButton_last300fulfilled.clicked.connect(self.click_logistics_pushButton_last300Fulfilled)
        self.logistics_pushButton_atTransit.clicked.connect(self.click_logistics_pushButton_atTransit)
        self.logistics_pushButton_viewDetails.clicked.connect(self.click_logistics_pushButton_viewDetails)
        self.logistics_pushButton_newLogistics.clicked.connect(self.click_logistics_pushButton_newLogistics)
        self.logistics_pushButton_generateCSV.clicked.connect(self.click_logistics_pushButton_generateCSV)

        self.inventory_pushButton_search.clicked.connect(self.click_inventory_pushButton_search)
        self.inventory_pushButton_generateCSV.clicked.connect(self.click_inventory_pushButton_generateCSV)
        self.inventory_pushButton_printBarcode.clicked.connect(self.click_inventory_pushButton_generateBarcode)
        self.inventory_pushButton_signInInventory.clicked.connect(self.click_inventory_pushButton_signInInventory)
        self.inventory_pushButton_skuReview.clicked.connect(self.click_inventory_pushButton_reviewSKU)
        self.inventory_pushButton_batchUpload.clicked.connect(self.click_inventory_pushButton_batchUpload)

        self.show()

    #------------------------------APP Admin Stuff------------------------------    
    
    def click_pushButton_logout(self):

        self.window = QMainWindow()

        if 'ZHTW' in self.label_username.text():
            self.createDialog('您已成功登出或超過30分鐘未使用，系統已自動登出。請重新登入。')
            self.openZHTWWindow()
        elif 'ZHCN' in self.label_username.text():
            self.createDialog('您已成功登出或超过30分钟未使用，系统已自动登出。请重新登入。')
            self.openZHCNWindow()
        else:       
            self.createDialog('Your session is expired or you have successfully logged out. Please login again.')
            self.openEngWindow()

    def closeEvent(self, event):

        sys.exit()

    #------------------------------Supplier Management------------------------------

    def click_supplier_pushButton_search(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()
        
        supplierID = str(self.supplier_textEdit_ID.toPlainText())
        supplierNameOL = str(self.supplier_textEdit_nameOL.toPlainText()) 
        supplierNameEN = str(self.supplier_textEdit_nameEN.toPlainText())
        supplierCountryEN = str(self.supplier_textEdit_countryEN.toPlainText())
        supplierStateEN = str(self.supplier_textEdit_stateEN.toPlainText())
        supplierRegionEN = str(self.supplier_textEdit_regionEN.toPlainText())
        supplierCityEN = str(self.supplier_textEdit_cityEN.toPlainText())

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(supplierID)==12 and isinstance(int(supplierID), int)):
                        body = container.read_item(supplierID,supplierID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif(supplierNameOL != "" ):

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = 'SELECT * FROM c',
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            name = df_list2['Name']
                            if('True' in self.isValidEntry(name) and supplierNameOL in name):
                                df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break

                    elif (supplierID != "" or supplierNameEN != "" or supplierCountryEN != "" or supplierStateEN != "" or supplierRegionEN != "" or supplierCityEN != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (supplierID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierID}%'"

                        if (supplierNameEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierNameEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierNameEN}%'"

                        if (supplierCountryEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierCountryEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierCountryEN}%'"
                        
                        if (supplierStateEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierStateEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierStateEN}%'"
                        
                        if (supplierRegionEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierRegionEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierRegionEN}%'"
                        
                        if (supplierCityEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierCityEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierCityEN}%'"

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = querystr,
                        #SELECT * FROM c  WHERE c.body LIKE '%Huizhou City%' AND c.body LIKE '%Huidong County%'
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break
             
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.supplier_tableWidget_display

        self.display_on_table(table, final_df)

    def click_supplier_pushButton_last100Updated(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        
        try:

            df_list = []

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>100):
                final_df = final_df[0:100]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.supplier_tableWidget_display

        self.display_on_table(table, final_df)
    
    def click_supplier_pushButton_last300Updated(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)
        try:

            df_list = []

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>300):
                final_df = final_df[0:300]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.supplier_tableWidget_display

        self.display_on_table(table, final_df)
    
    def click_supplier_pushButton_last100Added(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            df_list = []

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='CreatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>100):
                final_df = final_df[0:100]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.supplier_tableWidget_display

        self.display_on_table(table, final_df)

    def click_supplier_pushButton_last300Added(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            df_list = []

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='CreatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>300):
                final_df = final_df[0:300]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.supplier_tableWidget_display

        self.display_on_table(table, final_df)

    def click_supplier_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.supplier_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()
        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)

        try:
            filepath = self.get_save_csv_file_name('Supplier')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    def click_supplier_pushButton_printPostalLabel(self):

        self.timer.start(1800000)

        row = self.supplier_tableWidget_display.currentRow()
        table = self.supplier_tableWidget_display

        col_count = table.columnCount()

        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []

        for col in range(col_count):
            table_item = table.item(row,col)
            df_list.append('' if table_item is None else str(table_item.text()))

        df = pd.DataFrame([df_list], columns=headers)
        		        		
        postlabel = str(df['Postcode'][0]) + '\n\n' + str(df['Country(EN)'][0]) + '  '+str(df['Region(EN)'][0])+', '+str(df['State(EN)'][0])
        postlabel += '\n\n' + str(df['Country'][0]) + str(df['State'][0]) + str(df['Region'][0]) + str(df['City'][0])+ str(df['Address'][0])
        postlabel += '\n\n' + str(df['Name'][0]) +'  '+str(df['ContactWindow'][0]) + str(df['ContactNumber'][0])
        postlabel = postlabel.replace('None','')

        self.createPostLabel(postlabel)

    def click_supplier_pushButton_generateBarcode(self):

        try: 
            self.timer.start(1800000)

            row = self.supplier_tableWidget_display.currentRow()

            number = self.supplier_tableWidget_display.item(row,3).text()

            try:
                self.my_code = EAN13(number, writer=ImageWriter())
            
                filepath = self.get_save_png_file_name(number)
                
                self.my_code.save(filepath)

                if 'ZHTW' in self.label_username.text():
                    self.createDialog('條碼已儲存')
                elif 'ZHCN' in self.label_username.text():
                    self.createDialog('条码已储存')
                else: 
                    self.createDialog('Barcode is saved')
            except:
                if 'ZHTW' in self.label_username.text():
                    self.createDialog('不正確的檔案路徑或是png檔沒有關閉')
                elif 'ZHCN' in self.label_username.text():
                    self.createDialog('不正确的档案路径或是png档没有关闭')
                else: 
                    self.createDialog('Invalid directory or the .png file to be overwritten is not closed.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

    def click_supplier_pushButton_batchUpload(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        try:
            path = self.get_upload_csv_file_name()
            df = pd.read_csv(path,header =0,index_col=False,encoding='utf_8_sig')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('請選擇正確CSV檔案')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('请选择正确CSV档案')
            else: 
                self.createDialog('Please select a valid .csv file.')
            return

        if(len(df)>1500):
            df = df[0:1500]
        df['SupplierID'] = df['SupplierID'].astype(str).str.slice(stop=12)
    
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorwkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rwkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['SupplierID'][i]
                        if(key == ''):
                            break
                            break
                        data = df.iloc[i].to_json(orient='columns')

                        if('False' in self.isSupplierExisted(key,username)):
                            container.upsert_item({'id': key, 'body':data})
                            
                        else:
                            item = container.read_item(key,key)
                            if item != None and item != '' and item != 'null' and item != 'NULL':
                                container.upsert_item({'id': key, 'body':data})
            
            if 'ZHTW' in self.label_username.text():
                self.createDialog('系統已更新')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('系统已更新')
            else: 
                self.createDialog('System updated')

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('無法更新系統，請聯絡IT團隊')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('无法更新系统，请联络IT团队')
            else: 
                self.createDialog('Cannot update system. Contact IT support.')

    #------------------------------Vendor Management------------------------------
    
    def click_vendor_pushButton_search(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()
        
        vendorID = str(self.vendor_textEdit_vendorID.toPlainText())
        vendorEN = str(self.vendor_textEdit_vendorEN.toPlainText())
        vendorOL = str(self.vendor_textEdit_vendorOL.toPlainText())        

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.vendordb)

        try:

            for cr in database.list_containers():
                
                if(appui.vendorcr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(vendorID)==7 and isinstance(int(vendorID), int)):
                        body = container.read_item(vendorID,vendorID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif(vendorOL != ""):

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = 'SELECT * FROM c',
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            name = df_list2['Name']

                            if('True' in self.isValidEntry(name) and vendorOL in name):
                                df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break

                    elif (vendorID != "" or vendorEN != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (vendorID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{vendorID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{vendorID}%'"

                        if (vendorEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{vendorEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{vendorEN}%'"

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = querystr,
                        #SELECT * FROM c  WHERE c.body LIKE '%Huizhou City%' AND c.body LIKE '%Huidong County%'
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break
             
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.vendor_tableWidget_display

        self.display_on_table(table, final_df)

    def click_vendor_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.vendor_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()

        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        try: 
            filepath = self.get_save_csv_file_name('Vendor')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    def click_vendor_pushButton_batchUpload(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        try:
            path = self.get_upload_csv_file_name()
            df = pd.read_csv(path,header =0,index_col=False,encoding='utf_8_sig')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('請選擇正確CSV檔案')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('请选择正确CSV档案')
            else: 
                self.createDialog('Please select a valid .csv file.')
            return

        if(len(df)>1500):
            df = df[0:1500]
        df['VendorID'] = df['VendorID'].astype(str).str.slice(stop=7)
    
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorwkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rwkey) 
            database = client.get_database_client(appui.vendordb)

        try:

            for cr in database.list_containers():
                
                if(appui.vendorcr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['VendorID'][i]
                        if(key == ''):
                            break
                            break
                        data = df.iloc[i].to_json(orient='columns')

                        if('False' in self.isVendorExisted(key,username)):
                            container.upsert_item({'id': key, 'body':data})
                            
                        else:
                            item = container.read_item(key,key)
                            if item != None and item != '' and item != 'null' and item != 'NULL':
                                container.upsert_item({'id': key, 'body':data})

            if 'ZHTW' in self.label_username.text():
                self.createDialog('系統已更新')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('系统已更新')
            else: 
                self.createDialog('System updated')

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('無法更新系統，請聯絡IT團隊')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('无法更新系统，请联络IT团队')
            else: 
                self.createDialog('Cannot update system. Contact IT support.')

    #------------------------------Product Category Management------------------------------
    
    def click_productcategory_pushButton_listAll(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)
        try:

            df_list = []

            for cr in database.list_containers():
                
                if(appui.productcategorycr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.productcategory_tableWidget_display

        self.display_on_table(table, final_df)

    def click_productcategory_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.productcategory_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()

        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        try: 
            filepath = self.get_save_csv_file_name('ProductCategory')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    def click_productcategory_pushButton_batchUpload(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        try:
            path = self.get_upload_csv_file_name()
            df = pd.read_csv(path,header =0,index_col=False,encoding='utf_8_sig')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('請選擇正確CSV檔案')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('请选择正确CSV档案')
            else: 
                self.createDialog('Please select a valid .csv file.')
            return

        if(len(df)>1500):
            df = df[0:1500]
        df['CategoryID'] = df['CategoryID'].astype(str).str.slice(stop=7)
    
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorwkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rwkey) 
            database = client.get_database_client(appui.productdb)

        try:

            for cr in database.list_containers():
                
                if(appui.productcategorycr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['CategoryID'][i]
                        if(key == ''):
                            break
                            break
                        data = df.iloc[i].to_json(orient='columns')

                        if('False' in self.isProductCategoryExisted(key,username)):
                            container.upsert_item({'id': key, 'body':data})
                            
                        else:
                            item = container.read_item(key,key)
                            if item != None and item != '' and item != 'null' and item != 'NULL':
                                container.upsert_item({'id': key, 'body':data})

            if 'ZHTW' in self.label_username.text():
                self.createDialog('系統已更新')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('系统已更新')
            else: 
                self.createDialog('System updated')

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('無法更新系統，請聯絡IT團隊')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('无法更新系统，请联络IT团队')
            else: 
                self.createDialog('Cannot update system. Contact IT support.')

    #------------------------------Product Management------------------------------

    def click_product_pushButton_search(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()
        
        productID = str(self.product_textEdit_productID.toPlainText())
        productName = str(self.product_textEdit_productName.toPlainText()) 
        productCategoryName = str(self.product_textEdit_categoryName.toPlainText())
        productCategoryID = str(self.product_textEdit_categoryID.toPlainText())
        productCollection = str(self.product_textEdit_collection.toPlainText())
        productSupplierID = str(self.product_textEdit_supplierID.toPlainText())
        productTags = str(self.product_textEdit_tags.toPlainText())
        productColour = str(self.product_textEdit_colour.toPlainText())

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)

        try:

            for cr in database.list_containers():
                
                if(appui.productcr in cr['id'] and appui.productcategorycr not in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(productID)==12 and isinstance(int(productID), int)):
                        body = container.read_item(productID,productID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif (productID != "" or productName != "" or productCategoryName != "" or productCategoryID != "" or productCollection != "" or productSupplierID != "" or productTags != "" or productColour != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (productID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productID}%'"

                        if (productName != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productName}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productName}%'"

                        if (productCategoryName != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productCategoryName}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productCategoryName}%'"

                        if (productCategoryID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productCategoryID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productCategoryID}%'"
                        
                        if (productCollection != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productCollection}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productCollection}%'"
                        
                        if (productSupplierID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productSupplierID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productSupplierID}%'"
                        
                        if (productTags != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productTags}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productTags}%'"

                        if (productColour != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productColour}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productColour}%'"

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = querystr,
                        #SELECT * FROM c  WHERE c.body LIKE '%Huizhou City%' AND c.body LIKE '%Huidong County%'
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break
             
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.product_tableWidget_display

        self.display_on_table(table, final_df)

    def click_product_pushButton_last100Updated(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)
        
        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.productcr in cr['id'] and appui.productcategorycr not in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>100):
                final_df = final_df[0:100]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.product_tableWidget_display

        self.display_on_table(table, final_df)
    
    def click_product_pushButton_last300Updated(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)

        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.productcr in cr['id'] and appui.productcategorycr not in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>300):
                final_df = final_df[0:300]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.product_tableWidget_display

        self.display_on_table(table, final_df)
    
    def click_product_pushButton_last100Added(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)

        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.productcr in cr['id'] and appui.productcategorycr not in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='CreatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>100):
                final_df = final_df[0:100]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.product_tableWidget_display

        self.display_on_table(table, final_df)

    def click_product_pushButton_last300Added(self):

        self.timer.start(1800000)

        username = self.label_username.text()

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)

        try:

            df_list = []

            for cr in database.list_containers():
                
                if(appui.productcr in cr['id'] and appui.productcategorycr not in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)
            
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='CreatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>300):
                final_df = final_df[0:300]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")


        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return
        
        table = self.product_tableWidget_display

        self.display_on_table(table, final_df)

    def click_product_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.product_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()

        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        try:
            filepath = self.get_save_csv_file_name('Product')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    def click_product_pushButton_generateBarcode(self):
        
        try: 
            self.timer.start(1800000)

            row = self.product_tableWidget_display.currentRow()

            number = self.product_tableWidget_display.item(row,3).text()

            try:
                self.my_code = EAN13(number, writer=ImageWriter())
            
                filepath = self.get_save_png_file_name(number)
                
                self.my_code.save(filepath)

                if 'ZHTW' in self.label_username.text():
                    self.createDialog('條碼已儲存')
                elif 'ZHCN' in self.label_username.text():
                    self.createDialog('条码已储存')
                else: 
                    self.createDialog('Barcode is saved')
                
            except:
                if 'ZHTW' in self.label_username.text():
                    self.createDialog('不正確的檔案路徑或是png檔沒有關閉')
                elif 'ZHCN' in self.label_username.text():
                    self.createDialog('不正确的档案路径或是png档没有关闭')
                else: 
                    self.createDialog('Invalid directory or the .png file to be overwritten is not closed.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

    def click_product_pushButton_batchUpload(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        try:
            path = self.get_upload_csv_file_name()
            df = pd.read_csv(path,header =0,index_col=False,encoding='utf_8_sig')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('請選擇正確CSV檔案')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('请选择正确CSV档案')
            else: 
                self.createDialog('Please select a valid .csv file.')
            return

        if(len(df)>1500):
            df = df[0:1500]

        df['ProductID'] = df['ProductID'].astype(str).str.slice(stop=12)
    
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorwkey) 
            productdatabase = client.get_database_client(appui.demoproductdb)
            inventorydatabase = client.get_database_client(appui.demoinventorydb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rwkey) 
            productdatabase = client.get_database_client(appui.productdb)
            inventorydatabase = client.get_database_client(appui.inventorydb)

        try:

            for cr in productdatabase.list_containers():
                
                if(appui.productcategorycr not in cr['id'] and appui.productcr in cr['id']):
                    container = productdatabase.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['ProductID'][i]
                        if(key == ''):
                            break
                            break
                        data = df.iloc[i].to_json(orient='columns')

                        if('False' in self.isProductExisted(key,username)):
                            container.upsert_item({'id': key, 'body':data})
                            
                        else:
                            item = container.read_item(key,key)
                            if item != None and item != '' and item != 'null' and item != 'NULL':
                                container.upsert_item({'id': key, 'body':data})

            for cr in inventorydatabase.list_containers():
                
                if(appui.inventorycr in cr['id']):
                    container = inventorydatabase.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['ProductID'][i]
                        if(key == ''):
                            break
                            break

                        item = container.read_item(key,key)
                        if item != None and item != '' and item != 'null' and item != 'NULL':

                            body = item['body']
                            inventory_df = json_normalize(json.loads(body))

                            if(len(inventory_df) > 0):

                                inventory_df.at[0,'CategoryName'] = df.at[i,'CategoryName']
                                inventory_df.at[0,'Name'] = df.at[i,'Name']
                                inventory_df.at[0,'SupplierID'] = df.at[i,'SupplierID']
                                inventory_df.at[0,'Collection'] = df.at[i,'Collection']
                                inventory_df.at[0,'Tag'] = df.at[i,'Tag']
                                inventory_df.at[0,'Colour'] = df.at[i,'Colour']
                                inventory_df.at[0,'Set'] = df.at[i,'Set']
                                inventory_df.at[0,'GiftBundle'] = df.at[i,'GiftBundle']

                                data = inventory_df.iloc[0].to_json(orient='columns')

                                container.upsert_item({'id': key, 'body':data})
            
            if 'ZHTW' in self.label_username.text():
                self.createDialog('系統已更新')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('系统已更新')
            else: 
                self.createDialog('System updated')

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('無法更新系統，請聯絡IT團隊')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('无法更新系统，请联络IT团队')
            else: 
                self.createDialog('Cannot update system. Contact IT support.')

    #------------------------------Order Management------------------------------

    def click_order_pushButton_search(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        
        orderID = str(self.order_textEdit_orderID.toPlainText())
        supplierID = str(self.order_textEdit_supplierID.toPlainText()) 
        supplierEN = str(self.order_textEdit_supplierEN.toPlainText())
        supplierOL = str(self.order_textEdit_supplierOL.toPlainText())
        vendorID = str(self.order_textEdit_vendorID.toPlainText())
        vendorEN = str(self.order_textEdit_vendorEN.toPlainText())
        vendorOL = str(self.order_textEdit_vendorOL.toPlainText())
        destination = str(self.order_textEdit_destination.toPlainText())
        

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            for cr in database.list_containers():
                
                if(appui.ordercr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(orderID)==7 and isinstance(int(orderID), int)):
                        body = container.read_item(orderID,orderID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif(supplierOL != ""  or  vendorOL != ""):

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = 'SELECT * FROM c',
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            suppliername = df_list2['SupplierName']
                            vendorname = df_list2['VendorName']

                            if(supplierOL != '' and vendorOL != '' and 'True' in self.isValidEntry(suppliername) and 'True' in self.isValidEntry(vendorname) and supplierOL in suppliername and vendorOL in vendorname):
                                df_list.append(df_list2)
                            elif(supplierOL != '' and vendorOL == '' and 'True' in self.isValidEntry(suppliername) and supplierOL in suppliername):
                                df_list.append(df_list2)
                            elif(supplierOL == '' and vendorOL != '' and 'True' in self.isValidEntry(vendorname) and vendorOL in vendorname):
                                df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break

                    elif (orderID != "" or supplierID != "" or supplierEN != "" or vendorID != "" or vendorEN != "" or destination != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (orderID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{orderID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{orderID}%'"

                        if (supplierID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierID}%'"

                        if (supplierEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierEN}%'"
                        
                        if (vendorID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{vendorID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{vendorID}%'"
                        
                        if (vendorEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{vendorEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{vendorEN}%'"
                        
                        if (destination != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{destination}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{destination}%'"

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = querystr,
                        #SELECT * FROM c  WHERE c.body LIKE '%Huizhou City%' AND c.body LIKE '%Huidong County%'
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break
             
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.order_tableWidget_display

        self.display_on_table(table, final_df)

    def click_order_pushButton_last100Updated(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)
        
        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.ordercr in cr['id'] and appui.productcategorycr not in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>100):
                final_df = final_df[0:100]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.order_tableWidget_display

        self.display_on_table(table, final_df)

    def click_order_pushButton_last300Updated(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)
        
        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.ordercr in cr['id'] and appui.productcategorycr not in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>300):
                final_df = final_df[0:300]
            
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.order_tableWidget_display

        self.display_on_table(table, final_df)

    def click_order_pushButton_viewDetails(self):

        self.timer.start(1800000)
        
        try:
            row = self.order_tableWidget_display.currentRow()

            #[{"ProductID":"102010000012","Quantity":"3","UnitPrice":"15"},{"ProductID":"105010000003","Quantity":"6","UnitPrice":"25"},{"ProductID":"105010000005","Quantity":"3","UnitPrice":"40"},{"ProductID":"105010000006","Quantity":"3","UnitPrice":"40"}]
            # [{"ProductID":"102010000012","Quantity":"5","UnitPrice":"45.6"},{"ProductID":"105010000005","Quantity":"6","UnitPrice":"45.6"}]
            detail = self.order_tableWidget_display.item(row,8).text()
            id = self.order_tableWidget_display.item(row,3).text()
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return
        
        listheader = ['ProductID','Quantity','UnitPrice']
        list = detail.split('},{')
        list2, listfinal = [], []
        
        for i in range(len(list)):
            productid = str(list[i].split(',')[0]).replace('"ProductID":','').replace('[','').replace('{','').replace('"','')
            quantity = str(list[i].split(',')[1]).replace('"Quantity":','').replace('"','')
            unitprice = str(list[i].split(',')[2]).replace('"UnitPrice":','').replace(']','').replace('}','').replace('"','')
            list2 = [productid, quantity, unitprice]
            listfinal.append(list2)

        df = pd.DataFrame(listfinal, columns = listheader)
        
        self.createDetailWindow(id, df, 'Order_')

    def click_order_pushButton_newOrder(self):

        self.timer.start(1800000)
        
        role = str(self.label_username.text()).split('(')[1].replace(')','') if str(self.label_username.text()) != '' else ''
        username = str(self.label_username.text()).split(',')[1].split('(')[0] if str(self.label_username.text()) != '' else ''

        lang = 'ENG'
        if 'ZHTW' in self.label_username.text():
            lang = 'ZHTW'
        elif 'ZHCN' in self.label_username.text():
            lang = 'ZHCN'

        self.widget = QWidget()
        self.orderformui = orderformui()
        self.orderformui.openform(self.widget, username, role, lang)
       
    def click_order_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.order_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()

        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        try:
            filepath = self.get_save_csv_file_name('Order')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    def click_order_pushButton_batchUpload(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        try:
            path = self.get_upload_csv_file_name()
            df = pd.read_csv(path,header =0,index_col=False,encoding='utf_8_sig')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('請選擇正確CSV檔案')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('请选择正确CSV档案')
            else: 
                self.createDialog('Please select a valid .csv file.')
            return

        if(len(df)>1500):
            df = df[0:1500]
        df['OrderID'] = df['OrderID'].astype(str).str.slice(stop=7)
    
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorwkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rwkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['OrderID'][i]
                        if(key == ''):
                            break
                            break
                        data = df.iloc[i].to_json(orient='columns')

                        if('False' in self.isOrderExisted(key,username)):
                            container.upsert_item({'id': key, 'body':data})
                            
                        else:
                            item = container.read_item(key,key)
                            if item != None and item != '' and item != 'null' and item != 'NULL':
                                container.upsert_item({'id': key, 'body':data})

            if 'ZHTW' in self.label_username.text():
                self.createDialog('系統已更新')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('系统已更新')
            else: 
                self.createDialog('System updated')

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('無法更新系統，請聯絡IT團隊')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('无法更新系统，请联络IT团队')
            else: 
                self.createDialog('Cannot update system. Contact IT support.')
    #------------------------------Logistics Management------------------------------

    def click_logistics_pushButton_search(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        
        orderID = str(self.logistics_textEdit_orderID.toPlainText())
        supplierID = str(self.logistics_textEdit_supplierID.toPlainText()) 
        vendorID = str(self.logistics_textEdit_vendorID.toPlainText())
        vendorEN = str(self.logistics_textEdit_vendorEN.toPlainText())
        vendorOL = str(self.logistics_textEdit_vendorOL.toPlainText())
        destination = str(self.logistics_textEdit_destination.toPlainText())
        tracknumber = str(self.logistics_textEdit_trackingNumber.toPlainText())
        

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.vendordb)

        try:

            for cr in database.list_containers():
                
                if(appui.logisticcr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(orderID)==7 and isinstance(int(orderID), int)):
                        body = container.read_item(orderID,orderID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif(tracknumber != ""  or  vendorOL != ""):

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = 'SELECT * FROM c',
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            track = df_list2['TrackingNumber']
                            vendorname = df_list2['VendorName']
                            if(tracknumber != '' and vendorOL != '' and 'True' in self.isValidEntry(track) and 'True' in self.isValidEntry(vendorname) and tracknumber in track and vendorOL in vendorname):
                                df_list.append(df_list2)
                            elif(tracknumber != '' and vendorOL == '' and 'True' in self.isValidEntry(track) and tracknumber in track):
                                df_list.append(df_list2)
                            elif(tracknumber == '' and vendorOL != '' and 'True' in self.isValidEntry(vendorname) and vendorOL in vendorname):
                                df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break

                    elif (orderID != "" or supplierID != "" or vendorID != "" or vendorEN != "" or destination != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (orderID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{orderID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{orderID}%'"

                        if (supplierID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{supplierID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{supplierID}%'"
                        
                        if (vendorID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{vendorID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{vendorID}%'"
                        
                        if (vendorEN != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{vendorEN}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{vendorEN}%'"
                        
                        if (destination != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{destination}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{destination}%'"

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = querystr,
                        #SELECT * FROM c  WHERE c.body LIKE '%Huizhou City%' AND c.body LIKE '%Huidong County%'
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break
                
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.logistics_tableWidget_display

        self.display_on_table(table, final_df)

    def click_logistics_pushButton_last100Fulfilled(self):

        self.timer.start(1800000)
            
        username = self.label_username.text()

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.vendordb)
        
        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.logisticcr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        status = df_list2['CargoStatus']
                        if('Fulfilled' in status):
                            df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['PostedAt'] = pd.to_datetime(final_df['PostedAt'])
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>100):
                final_df = final_df[0:100]
            
            final_df['PostedAt'] =  final_df['PostedAt'].dt.strftime("%d-%b-%y")
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.logistics_tableWidget_display

        self.display_on_table(table, final_df)

    def click_logistics_pushButton_last300Fulfilled(self):

        self.timer.start(1800000)
            
        username = self.label_username.text()

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.vendordb)
        
        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.logisticcr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        status = df_list2['CargoStatus']
                        if('Fulfilled' in status):
                            df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['PostedAt'] = pd.to_datetime(final_df['PostedAt'])
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='LastUpdatedAt', ascending = False, inplace=True)
            
            if (len(final_df)>300):
                final_df = final_df[0:300]
            
            final_df['PostedAt'] =  final_df['PostedAt'].dt.strftime("%d-%b-%y")
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.logistics_tableWidget_display

        self.display_on_table(table, final_df)

    def click_logistics_pushButton_atTransit(self):

        self.timer.start(1800000)
            
        username = self.label_username.text()

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.vendordb)
        
        try:
            
            df_list = []

            for cr in database.list_containers():
                
                if(appui.logisticcr in cr['id']):

                    df_list2 = []
                    container = database.get_container_client(cr['id'])
                    
                    for item in container.query_items(
                    query = 'SELECT * FROM c',
                    enable_cross_partition_query = True,
                    ):
                    
                        body = item['body']
                        df_list2 = json.loads(body)
                        status = df_list2['CargoStatus']
                        if('Fulfilled' not in status):
                            df_list.append(df_list2)

            final_df = pd.DataFrame(df_list)

            final_df['PostedAt'] = pd.to_datetime(final_df['PostedAt'])
            final_df['CreatedAt'] = pd.to_datetime(final_df['CreatedAt'])
            final_df['LastUpdatedAt'] = pd.to_datetime(final_df['LastUpdatedAt'])
            final_df['ChangesApprovedAt'] = pd.to_datetime(final_df['ChangesApprovedAt'])

            final_df.sort_values(by='PostedAt', ascending = True, inplace=True)
                    
            final_df['PostedAt'] =  final_df['PostedAt'].dt.strftime("%d-%b-%y")
            final_df['CreatedAt'] =  final_df['CreatedAt'].dt.strftime("%d-%b-%y")
            final_df['LastUpdatedAt'] =  final_df['LastUpdatedAt'].dt.strftime("%d-%b-%y")
            final_df['ChangesApprovedAt'] =  final_df['ChangesApprovedAt'].dt.strftime("%d-%b-%y")

        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.logistics_tableWidget_display

        self.display_on_table(table, final_df)

    def click_logistics_pushButton_viewDetails(self):

        self.timer.start(1800000)

        try:
            
            row = self.logistics_tableWidget_display.currentRow()

            #[{"ProductID":"102010000012","Quantity":"3","UnitPrice":"15"},{"ProductID":"105010000003","Quantity":"6","UnitPrice":"25"},{"ProductID":"105010000005","Quantity":"3","UnitPrice":"40"},{"ProductID":"105010000006","Quantity":"3","UnitPrice":"40"}]
            # [{"ProductID":"102010000012","Quantity":"5","UnitPrice":"45.6"},{"ProductID":"105010000005","Quantity":"6","UnitPrice":"45.6"}]
            detail = self.logistics_tableWidget_display.item(row,16).text()
            id = self.logistics_tableWidget_display.item(row,3).text()
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return
        
        listheader = ['ProductID','Quantity','UnitPrice']
        list = detail.split('},{')
        list2, listfinal = [], []
        
        for i in range(len(list)):
            productid = str(list[i].split(',')[0]).replace('"ProductID":','').replace('[','').replace('{','').replace('"','')
            quantity = str(list[i].split(',')[1]).replace('"Quantity":','').replace('"','')
            unitprice = str(list[i].split(',')[2]).replace('"UnitPrice":','').replace(']','').replace('}','').replace('"','')
            list2 = [productid, quantity, unitprice]
            listfinal.append(list2)

        df = pd.DataFrame(listfinal, columns = listheader)
        
        self.createDetailWindow(id, df, 'Order_')

    def click_logistics_pushButton_newLogistics(self):

        self.timer.start(1800000)
            
        role = str(self.label_username.text()).split('(')[1].replace(')','') if str(self.label_username.text()) != '' else ''
        username = str(self.label_username.text()).split(',')[1].split('(')[0] if str(self.label_username.text()) != '' else ''

        lang = 'ENG'
        if 'ZHTW' in self.label_username.text():
            lang = 'ZHTW'
        elif 'ZHCN' in self.label_username.text():
            lang = 'ZHCN'
        
        self.widget = QWidget()
        self.logisticsformui = logisticsformui()
        self.logisticsformui.openform(self.widget, username, role, lang)

    def click_logistics_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.logistics_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()
        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        try:
            filepath = self.get_save_csv_file_name('Logistic')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    #------------------------------Inventory Management------------------------------

    def click_inventory_pushButton_search(self):

        self.timer.start(1800000)

        username = self.label_username.text()
        
        warehouse = str(self.inventory_textEdit_warehouse.toPlainText())
        productID = str(self.inventory_textEdit_productID.toPlainText()) 
        productName = str(self.inventory_textEdit_productName.toPlainText())  

        final_df = pd.DataFrame()

        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoinventorydb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.inventorydb)

        try:

            for cr in database.list_containers():
                
                if(appui.inventorycr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(productID)==12 and isinstance(int(productID), int)):
                        body = container.read_item(productID,productID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif (productID != "" or productName != "" or warehouse != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (productID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productID}%'"

                        if (productName != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{productName}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{productName}%'"
                        
                        if (warehouse != ""):

                            if("%" not in querystr):
                                querystr += " WHERE c.body NOT LIKE '%{}%'".format(warehouse+'_Warehouse\":0')
                            else:
                                querystr += " AND c.body NOT LIKE '%{}%'".format(warehouse+'_Warehouse\":0')

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = querystr,
                        #SELECT * FROM c  WHERE c.body LIKE '%Huizhou City%' AND c.body LIKE '%Huidong County%'
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break
                
        except Exception as e:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.inventory_tableWidget_display

        self.display_on_table(table, final_df)

    def click_inventory_pushButton_generateCSV(self):

        self.timer.start(1800000)
        
        table = self.inventory_tableWidget_display

        col_count = table.columnCount()
        row_count = table.rowCount()
        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count):
                table_item = table.item(row,col)
                df_list2.append('' if table_item is None else str(table_item.text()))
            df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)
        try:
            filepath = self.get_save_csv_file_name('Inventory')
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.label_username.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('不正確的檔案路徑或是CSV檔沒有關閉')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('不正确的档案路径或是CSV档没有关闭')
            else: 
                self.createDialog('Invalid directory or the .csv file to be overwritten is not closed.')
            return

    def click_inventory_pushButton_generateBarcode(self):

        try: 
            self.timer.start(1800000)

            row = self.inventory_tableWidget_display.currentRow()

            number = self.inventory_tableWidget_display.item(row,3).text()

            try:
                self.my_code = EAN13(number, writer=ImageWriter())
            
                filepath = self.get_save_png_file_name(number)
                
                self.my_code.save(filepath)

                if 'ZHTW' in self.label_username.text():
                    self.createDialog('條碼已儲存')
                elif 'ZHCN' in self.label_username.text():
                    self.createDialog('条码已储存')
                else: 
                    self.createDialog('Barcode is saved')
            except:
                if 'ZHTW' in self.label_username.text():
                    self.createDialog('不正確的檔案路徑或是png檔沒有關閉')
                elif 'ZHCN' in self.label_username.text():
                    self.createDialog('不正确的档案路径或是png档没有关闭')
                else: 
                    self.createDialog('Invalid directory or the .png file to be overwritten is not closed.')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

    def click_inventory_pushButton_signInInventory(self):

        self.timer.start(1800000)
            
        role = str(self.label_username.text()).split('(')[1].replace(')','') if str(self.label_username.text()) != '' else ''
        username = str(self.label_username.text()).split(',')[1].split('(')[0] if str(self.label_username.text()) != '' else ''

        lang = 'ENG'
        if 'ZHTW' in self.label_username.text():
            lang = 'ZHTW'
        elif 'ZHCN' in self.label_username.text():
            lang = 'ZHCN'
        
        self.widget = QWidget()
        self.signininventoryui = signininventoryui()
        self.signininventoryui.openform(self.widget, username, role, lang)

    def click_inventory_pushButton_reviewSKU(self):

        self.timer.start(1800000)
            
        role = str(self.label_username.text()).split('(')[1].replace(')','') if str(self.label_username.text()) != '' else ''
        username = str(self.label_username.text()).split(',')[1].split('(')[0] if str(self.label_username.text()) != '' else ''

        lang = 'ENG'
        if 'ZHTW' in self.label_username.text():
            lang = 'ZHTW'
        elif 'ZHCN' in self.label_username.text():
            lang = 'ZHCN'
        
        self.widget = QWidget()
        self.skureviewui = skureviewui()
        self.skureviewui.openform(self.widget, username, role, lang)

    def click_inventory_pushButton_batchUpload(self):

        self.timer.start(1800000)
        
        username = self.label_username.text()
        destination = self.inventory_textEdit_warehouse.toPlainText()

        try:
            path = self.get_upload_csv_file_name()
            df = pd.read_csv(path,header =0,index_col=False,encoding='utf_8_sig')
        except:
            if 'ZHTW' in self.label_username.text():
                self.createDialog('請選擇正確CSV檔案')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('请选择正确CSV档案')
            else: 
                self.createDialog('Please select a valid .csv file.')
            return
        

        if(len(destination) < 2 or len(destination)>4):
            self.createDialog('Warehouse is incorrect.')
            return

        if(len(df)>1500):
            df = df[0:1500]
        df['ProductID'] = df['ProductID'].astype(str).str.slice(stop=12)
    
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorwkey) 
            database = client.get_database_client(appui.demoinventorydb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rwkey) 
            database = client.get_database_client(appui.inventorydb)

        try:

            for cr in database.list_containers():
                
                if(appui.inventorycr in cr['id']):
                    container = database.get_container_client(cr['id'])

                    for i in range(len(df)):

                        key = df['ProductID'][i]
                        if(key == ''):
                            break
                            break

                        item = container.read_item(key,key)
                        if item != None and item != '' and item != 'null' and item != 'NULL':

                            body = item['body']
                            inventory_df = json_normalize(json.loads(body))

                            if(len(inventory_df) > 0):

                                inventory_df.at[0,destination+'_Warehouse'] = df.at[i,destination+'_Warehouse']
                                inventory_df.at[0,'LastUpdatedAt'] = date.today().strftime("%d-%b-%y")
                                inventory_df.at[0,'LastUpdatedBy'] = username

                                data = inventory_df.iloc[0].to_json(orient='columns')

                                container.upsert_item({'id': key, 'body':data})

            if 'ZHTW' in self.label_username.text():
                self.createDialog('系統已更新')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('系统已更新')
            else: 
                self.createDialog('System updated')

        except Exception as e:

            if 'ZHTW' in self.label_username.text():
                self.createDialog('無法更新系統，請聯絡IT團隊')
            elif 'ZHCN' in self.label_username.text():
                self.createDialog('无法更新系统，请联络IT团队')
            else: 
                self.createDialog('Cannot update system. Contact IT support.')
    #------------------------------Call Methods (Login and ResetPW)------------------------------

    def openresetpwwindow(self, MainWindow, lang):
        
        self.totpkey = pyotp.random_base32().replace("'","")
        self.totp = pyotp.TOTP(self.totpkey, interval=900)
        self.code = self.totp.at(int(time.time()))

        if 'ZHTW' in lang: 
            uic.loadUi("ResetPassword_UI_ZHTW.ui",self)
            self.label_lang.setVisible(False)
            self.label_lang.setText('ZHTW')
        elif 'ZHCN' in lang: 
            uic.loadUi("ResetPassword_UI_ZHCN.ui",self)
            self.label_lang.setVisible(False)
            self.label_lang.setText('ZHCN')
        else: 
            uic.loadUi("ResetPassword_UI.ui",self)
            self.label_lang.setVisible(False)
            self.label_lang.setText('ENG')

        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle(appui.apptitle)
        self.setFixedSize(800,610)

        self.lineEdit_pw1.setEchoMode(QLineEdit.Password)
        self.lineEdit_pw2.setEchoMode(QLineEdit.Password)

        self.label_pwinstru.setVisible(False)
        self.label_code.setVisible(False)
        self.label_pw1.setVisible(False)
        self.label_pw2.setVisible(False)

        self.textEdit_code.setVisible(False)
        self.lineEdit_pw1.setVisible(False)
        self.lineEdit_pw2.setVisible(False)

        self.pushButton_resendcode.setVisible(False)

        self.pushButton_submit.clicked.connect(self.click_submit)
        self.pushButton_resendcode.clicked.connect(self.click_resendcode)

        self.show()      

    def click_submit(self):
        
        authcode = self.textEdit_code.toPlainText()
        user = self.textEdit_username.toPlainText()

        if(user == 'Demo'):

            if(authcode == ""):
            
                self.label_code.setVisible(True)
                self.textEdit_code.setVisible(True)
                self.pushButton_resendcode.setVisible(True)
            
            elif(authcode == "111111" and self.lineEdit_pw1.text() == "" ):
                
                self.label_pwinstru.setVisible(True)
                self.label_pw1.setVisible(True)
                self.label_pw2.setVisible(True)
                self.lineEdit_pw1.setVisible(True)
                self.lineEdit_pw2.setVisible(True)
            
            elif (self.lineEdit_pw1.text() == "111111" and self.lineEdit_pw2.text() == "111111"):
                
                if 'ZHTW' in self.label_lang.text():
                    self.createDialog('密碼已重設，請重新登入')
                    self.openZHTWWindow()
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('密码已重设，请重新登入')
                    self.openZHCNWindow()
                else:
                    self.createDialog('Password is reset. Please login again.')
                    self.openEngWindow()

                self.setWindowIcon(QIcon('logo.ico'))
                self.setWindowTitle(appui.apptitle)
                self.setFixedSize(800,500)

                self.lineEdit_pw.setEchoMode(QLineEdit.Password)
                self.show()
                self.pushButton_eng.clicked.connect(self.openEngWindow)
                self.pushButton_zhtw.clicked.connect(self.openZHTWWindow)
                self.pushButton_zhcn.clicked.connect(self.openZHCNWindow)

                self.pushButton_register.clicked.connect(self.click_register)
                self.pushButton_submit.clicked.connect(self.click_submit_login)

            elif (self.lineEdit_pw1.text() != "111111" or self.lineEdit_pw2.text() != "111111"):
                if 'ZHTW' in self.label_lang.text():
                    self.createDialog('密碼錯誤')
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('密码错误')
                else:
                    self.createDialog('Wrong password')

        else:

            if(authcode == ""):
                
                self.label_code.setVisible(True)
                self.textEdit_code.setVisible(True)
                self.pushButton_resendcode.setVisible(True)
                self.getEmailfromDBAndSendEmail()
                
            elif(authcode != "" and self.lineEdit_pw1.text() == "" and self.totp.verify(authcode)):
                
                self.label_pwinstru.setVisible(True)
                self.label_pw1.setVisible(True)
                self.label_pw2.setVisible(True)
                self.lineEdit_pw1.setVisible(True)
                self.lineEdit_pw2.setVisible(True)
                
            elif(not self.totp.verify(authcode)):
                if 'ZHTW' in self.label_lang.text():
                    self.createDialog('驗證失敗，請重新輸入')
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('验证失败，请重新输入')
                else:
                    self.createDialog('Authorisation failed. Please try again.')
            
            elif (self.lineEdit_pw1.text() != "" and self.lineEdit_pw2.text() != ""):
                self.verifyPassWord()
    
    def click_resendcode(self):
        self.totpkey = pyotp.random_base32().replace("'","")
        self.totp = pyotp.TOTP(self.totpkey, interval=900)
        self.code = self.totp.at(int(time.time()))
        self.getEmailfromDBAndSendEmail()
    
    def callUpdatePassword(self):
        
        username = str(self.textEdit_username.toPlainText())
        inputpw = str(self.lineEdit_pw1.text())

        client = cosmos_client.CosmosClient(appui.hruri, appui.hrrwkey) 
        database = client.get_database_client('hrmanagement')
        df = pd.DataFrame()

        try:

            for cr in database.list_containers():
                    
                if('staff' in cr['id']):

                    container = database.get_container_client(cr['id'])
                    body = container.read_item(username,username)['body']
                    jsondisplay = json.loads(body)
                    df = json_normalize(jsondisplay)
                    break
        except:
            if 'ZHTW' in self.label_lang.text():
                self.createDialog("狀態404: 找不到使用者，請聯繫IT團隊")
            elif 'ZHCN' in self.label_lang.text():
                self.createDialog("状态404: 找不到使用者，请联系IT团队")
            else: 
                self.createDialog("Status 404: User not found. Contact IT support")

        salt = bcrypt.gensalt(rounds=8)
        hash = bcrypt.hashpw(inputpw.encode('utf-8'), salt)

        df.at[0,'Salt'] = salt
        df.at[0,'Hash'] = hash
        
        body = df.iloc[0].to_json(orient='columns')

        try:
    
            if (username != '' and username != 'Demo' and container != None and container != '' and container != 'null' and container != 'NULL'):

                key = username
                container.upsert_item({'id': key, 'body':body})    
                
                self.window = QMainWindow()

                if 'ZHTW' in self.label_lang.text():
                    self.createDialog('密碼已重設，請重新登入')
                    uic.loadUi("LoginPage_UI_ZHTW.ui",self)
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('密码已重设，请重新登入')
                    uic.loadUi("LoginPage_UI_ZHCN.ui",self)
                else: 
                    self.createDialog('Password is reset. Please log in again.')
                    uic.loadUi("LoginPage_UI.ui",self)

                self.setWindowIcon(QIcon('logo.ico'))
                self.setWindowTitle(appui.apptitle)
                self.setFixedSize(800,500)

                self.lineEdit_pw.setEchoMode(QLineEdit.Password)
                self.show()
                self.pushButton_register.clicked.connect(self.click_register)
                self.pushButton_submit.clicked.connect(self.click_submit_login)

        except: 
            if 'ZHTW' in self.label_lang.text():
                self.createDialog('密碼重設失敗，請再試一次')
            elif 'ZHCN' in self.label_lang.text():
                self.createDialog('密码重设失败，请再试一次')
            else: 
                self.createDialog('Password reset failed. Please try again.')
            pass 
    
    def openEngWindow(self):
        uic.loadUi("LoginPage_UI.ui",self)
        self.label_lang.setVisible(False)
        self.label_lang.setText('ENG')
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle(appui.apptitle)
        self.setFixedSize(800,500)
        
        self.lineEdit_pw.setEchoMode(QLineEdit.Password)
        self.show()
        self.pushButton_eng.clicked.connect(self.openEngWindow)
        self.pushButton_zhtw.clicked.connect(self.openZHTWWindow)
        self.pushButton_zhcn.clicked.connect(self.openZHCNWindow)

        self.pushButton_register.clicked.connect(self.openresetpwwindow)
        self.pushButton_submit.clicked.connect(self.click_submit_login)

    def openZHTWWindow(self):
        uic.loadUi("LoginPage_UI_ZHTW.ui",self)
        self.label_lang.setVisible(False)
        self.label_lang.setText('ZHTW')
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle(appui.apptitle)
        self.setFixedSize(800,500)
        
        self.lineEdit_pw.setEchoMode(QLineEdit.Password)
        self.show()
        self.pushButton_eng.clicked.connect(self.openEngWindow)
        self.pushButton_zhtw.clicked.connect(self.openZHTWWindow)
        self.pushButton_zhcn.clicked.connect(self.openZHCNWindow)

        self.pushButton_register.clicked.connect(self.openresetpwwindow)
        self.pushButton_submit.clicked.connect(self.click_submit_login)

    def openZHCNWindow(self):
        uic.loadUi("LoginPage_UI_ZHCN.ui",self)
        self.label_lang.setVisible(False)
        self.label_lang.setText('ZHCN')
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle(appui.apptitle)
        self.setFixedSize(800,500)
        
        self.lineEdit_pw.setEchoMode(QLineEdit.Password)
        self.show()
        self.pushButton_eng.clicked.connect(self.openEngWindow)
        self.pushButton_zhtw.clicked.connect(self.openZHTWWindow)
        self.pushButton_zhcn.clicked.connect(self.openZHCNWindow)

        self.pushButton_register.clicked.connect(self.openresetpwwindow)
        self.pushButton_submit.clicked.connect(self.click_submit_login)
    
    def click_register(self):

        self.window = QMainWindow()
        self.openresetpwwindow(self.window)
        self.destroy()

    def click_submit_login(self):

        username = str(self.textEdit_username.toPlainText())
        inputpw = str(self.lineEdit_pw.text())

        if(username == 'Demo'):

            if(inputpw == '111111'):

                self.window = QMainWindow()
                self.appui = appui()
            
                if 'ZHTW' in self.label_lang.text():
                    self.createDialog('登入成功')
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('登入成功')
                else:
                    self.createDialog('Login success')
                self.appui.openappwindow(self.window, 'Demo', 'ReadWrite', self.label_lang.text())
                self.destroy()
            else:
                if 'ZHTW' in self.label_lang.text():
                    self.createDialog('密碼錯誤')
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('密碼錯誤')
                else: 
                    self.createDialog('Wrong password')
            return

        else:
            
            role = self.callDB(username, 2)
            if(role == None):
                return
            schash = self.callDB(username, 3)
            errorcount = self.callDB(username, 4)
            container = self.callDB(username, 1)

            if(schash != None):

                try:
                    if('True' in self.checkhash(inputpw,schash)):
                        self.generatebodyandupdateDB(username, container, self.callDB(username, 0), 0)

                        self.window = QMainWindow()
                        self.appui = appui()

                        if 'ZHTW' in self.label_lang.text():
                            self.createDialog('登入成功')
                            self.appui.openappwindow(self.window, username, role, 'ZHTW')
                        elif 'ZHCN' in self.label_lang.text():
                            self.createDialog('登入成功')
                            self.appui.openappwindow(self.window, username, role, 'ZHCN')
                        else: 
                            self.createDialog('Login success')
                            self.appui.openappwindow(self.window, username, role, 'ENG')

                        self.destroy()
                    else:
                        self.generatebodyandupdateDB(username, container, self.callDB(username, 0), 1)
                        if 'ZHTW' in self.label_lang.text():
                            self.createDialog("狀態202: 密碼錯誤，錯誤次數: "+str(int(errorcount)+1))
                        elif 'ZHCN' in self.label_lang.text():
                            self.createDialog("状态202: 密码错误，错误次数: "+str(int(errorcount)+1))
                        else: 
                            self.createDialog("Status 202: Wrong password. Error count: "+str(int(errorcount)+1))
                except Exception as e:
                    if 'ZHTW' in self.label_lang.text():
                        self.createDialog("狀態500: 請聯絡IT團隊")
                    elif 'ZHCN' in self.label_lang.text():
                        self.createDialog("状态500: 请联络IT团队")
                    else: 
                        self.createDialog("Status 500: Contact IT support")

    def getEmailfromDBAndSendEmail(self):
        
        body = ''
        username = str(self.textEdit_username.toPlainText())
        msg = str(self.code)

        client = cosmos_client.CosmosClient(appui.hruri, appui.hrrkey) 
        database = client.get_database_client('hrmanagement')
        container = database.get_container_client('staff1')
        try:
            body = container.read_item(username,username)['body']
        except:
            if 'ZHTW' in self.label_lang.text():
                self.createDialog('狀態404: 找不到使用者，請聯繫IT團隊')
            elif 'ZHCN' in self.label_lang.text():
                self.createDialog('状态404: 找不到使用者，请联系IT团队')
            else: 
                self.createDialog('Status 404: User not found. Contact IT support')
        if('Email' in body and 'ZHTW' in self.label_lang.text()):
            email = ((body.split(',')[13]).split(':')[1]).replace("\"","")
            if(email != None and email != '' and msg != ''):
                msg = '<strong>'+str(msg)+'</strong>'
                message = Mail(
                from_email='webservice0023@gmail.com',
                to_emails=email,
                subject='您的chain驗證碼',
                html_content='您的驗證碼為'+ msg +'。\n\n請在15分鐘內輸入驗證碼'
                )
                try:
                    sg = SendGridAPIClient(appui.sgkey)
                    response = sg.send(message)
                    self.createDialog('請確認您的電子郵件。您的驗證碼將在15分鐘後失效')
                except Exception as e:
                    self.createDialog('狀態500: 請聯絡IT團隊')

        elif('Email' in body and 'ZHCN' in self.label_lang.text()):
            email = ((body.split(',')[13]).split(':')[1]).replace("\"","")
            if(email != None and email != '' and msg != ''):
                msg = '<strong>'+str(msg)+'</strong>'
                message = Mail(
                from_email='webservice0023@gmail.com',
                to_emails=email,
                subject='您的chain验证码',
                html_content='您的验证码为'+ msg +'。\n\n请在15分钟内输入验证码'
                )
                try:
                    sg = SendGridAPIClient(appui.sgkey)
                    response = sg.send(message)
                    self.createDialog('请确认您的电子邮件。您的验证码将在15分钟后失效')
                except Exception as e:
                    self.createDialog('状态500: 请联络IT团队')

        elif('Email' in body):
            email = ((body.split(',')[13]).split(':')[1]).replace("\"","")
            if(email != None and email != '' and msg != ''):
                msg = '<strong>'+str(msg)+'</strong>'
                message = Mail(
                from_email='webservice0023@gmail.com',
                to_emails=email,
                subject='Your security code is delivered.',
                html_content='Your security code is '+ msg +'.\n\nPlease enter your code within 15 min.'
                )
                try:
                    sg = SendGridAPIClient(appui.sgkey)
                    response = sg.send(message)
                    self.createDialog('Please check your inbox. The security code is valid for 15 min.')
                except Exception as e:
                    self.createDialog('Status 500: Contact IT support')
    
    def verifyPassWord(self):

        if(self.lineEdit_pw1.text() == self.lineEdit_pw2.text() and self.isverifiedPassWord(self.lineEdit_pw1.text())):
            self.callUpdatePassword()
        else:
            if 'ZHTW' in self.label_lang.text():
                self.createDialog('無效密碼，請重設')   
            elif 'ZHCN' in self.label_lang.text():
                self.createDialog('无效密码，请重设')
            else: 
                self.createDialog('Invalid password. Please reset.')                  

    def isverifiedPassWord(self, password):
        a = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        b = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        c = ['#','$','%','!','^','&','*','~','`','"','/',',','.']

        b1, b2, b3 = False,False,False
        
        for i in range(len(password)):

            if(password[i] in a):
                b1 = True
            elif(password[i] in b):
                b2 = True
            elif(password[i] in c):
                b3 = True

            if (b1 == True and b2 == True and b3 == True):
                break

        return b1 == True and b2 == True and b3 == True

    def callDB(self, username, d):

        client = cosmos_client.CosmosClient(appui.hruri, appui.hrrkey) 
        database = client.get_database_client('hrmanagement')
        df = pd.DataFrame()
        body = None
        container = None

        try:

            for cr in database.list_containers():
                    
                if('staff' in cr['id']):

                    container = database.get_container_client(cr['id'])
                    body = container.read_item(username,username)['body']
                    jsondisplay = json.loads(body)
                    df = json_normalize(jsondisplay)
                    break
        except:
            if 'ZHTW' in self.label_lang.text():
                self.createDialog("狀態404: 找不到使用者，請聯繫IT團隊")
            elif 'ZHCN' in self.label_lang.text():
                self.createDialog("状态404: 找不到使用者，请联系IT团队")
            else: 
                self.createDialog("Status 404: User not found. Contact IT support")
            return
        try:
            if(len(df)>0):
                if(d==0):
                    return body
                elif(d==1):
                    return container
                elif(d==2):
                    return str(df.at[0,'Access'])
                elif(d==3):
                    return str(df.at[0,'Hash'])
                elif(d==4):
                    return str(df.at[0,'ErrorCount'])
            else:
                return None
        except Exception as e: 
            if 'ZHTW' in self.label_lang.text():
                self.createDialog('請重設密碼')
            elif 'ZHCN' in self.label_lang.text():
                self.createDialog('请重设密码')
            else: 
                self.createDialog('Please reset password.')

    def generatebodyandupdateDB(self, username, container, data, add):

        df = pd.read_json(data,orient='index')
        df = df.transpose()
        if add == 1:
            df['ErrorCount'] = int(df['ErrorCount'])+add
        else:
            df['ErrorCount'] = 0
        
        body = df.iloc[0].to_json(orient='columns')

        try:
      
            if (username != '' and username != 'Demo' and container != None and container != '' and container != 'null' and container != 'NULL'):

                key = username
                container.upsert_item({'id': key, 'body':body})    

        except: 
            pass               
    
    def checkhash(self, inputpw, schash):
        back = 'False'
        try:
            back = str(bcrypt.checkpw(inputpw.encode('utf-8'), schash.encode('utf-8')))
        except:
            pass
            #return 'Status 423: Please reset password.'
        return back
   
    #------------------------------Call Methods (APP UI)------------------------------
    
    def get_upload_csv_file_name(self):

        file_filter = 'Data File (*.csv)'
        response = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Select a Data File (*.csv) to open',
            directory = os.getcwd(),
            filter = file_filter,
            initialFilter=file_filter
        )
        return response[0]
    
    def get_save_csv_file_name(self, type):

        filename = 'Listing'+'_'+date.today().strftime("%d-%b-%y")

        if(type != ''):
            filename = type+'_'+filename

        file_filter = 'Data File (*.csv)'
        response = QFileDialog.getSaveFileName(
            parent = self,
            caption = 'Select a data file',
            directory = filename,
            filter = file_filter,
            initialFilter=file_filter
        )
        return response[0]

    def get_save_png_file_name(self, number):

        filename = 'Barcode'

        if(number != ''):
            filename = number +'_'+filename

        file_filter = 'Image File (*.png)'

        response = QFileDialog.getSaveFileName(
            parent = self,
            caption = 'Select a image file',
            directory = filename,
            filter = file_filter,
            initialFilter=file_filter
        )
        return response[0]

    def display_on_table(self, table, df):

        final_df = pd.DataFrame(df)

        if(len(final_df)==0):
            if('ZHTW' in self.label_username.text()):
                self.createDialog('找不到資料') 
            elif('ZHCN' in self.label_username.text()):
                self.createDialog('找不到资料') 
            else: 
                self.createDialog('No data found.')   

        else:
            table.setColumnCount(len(final_df.columns))     
            table.setRowCount(len(final_df))
            table.setHorizontalHeaderLabels(list(final_df.columns))
            table.horizontalHeader().setStretchLastSection(True)
            #table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            table.verticalHeader().setDefaultSectionSize(30)

            for i in range(len(final_df)):
                for j in range(len(final_df.columns)):
                    table.setItem(i,j, QTableWidgetItem(str(final_df.iloc[i,j])))

            table.resizeRowsToContents()
            table.resizeColumnsToContents()    

    def isValidEntry(self, text):

        if('str' in str(type(text)) and text != '' and text != 'None' and text != 'none' and text != 'NULL' and text != 'null'):
            return 'True'
        else: 
            return 'False'

    def isSupplierExisted(self, id, username):
       
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            for cr in database.list_containers():
                
                if(appui.suppliercr in cr['id']):

                    container = database.get_container_client(cr['id'])

                    if(len(id)==12 and isinstance(int(id), int)):

                        item = container.read_item(id,id)

                        if item != None and item != '' and item != 'null':
                            return 'True'
           
        except Exception as e:
            pass

        return 'False'
    
    def isVendorExisted(self, id, username):
       
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demovendordb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.vendordb)

        try:

            for cr in database.list_containers():
                
                if(appui.vendorcr in cr['id']):

                    container = database.get_container_client(cr['id'])

                    if(len(id)==7 and isinstance(int(id), int)):

                        item = container.read_item(id,id)

                        if item != None and item != '' and item != 'null':
                            return 'True'
           
        except Exception as e:
            pass

        return 'False'
    
    def isProductCategoryExisted(self, id, username):
       
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)

        try:

            for cr in database.list_containers():
                
                if(appui.productcategorycr in cr['id']):

                    container = database.get_container_client(cr['id'])

                    if(len(id)==12 and isinstance(int(id), int)):

                        item = container.read_item(id,id)

                        if item != None and item != '' and item != 'null':
                            return 'True'
           
        except Exception as e:
            pass

        return 'False'  

    def isProductExisted(self, id, username):
       
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demoproductdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.productdb)

        try:

            for cr in database.list_containers():
                
                if(appui.productcategorycr not in cr['id'] and appui.productcr in cr['id']):

                    container = database.get_container_client(cr['id'])

                    if(len(id)==12 and isinstance(int(id), int)):

                        item = container.read_item(id,id)

                        if item != None and item != '' and item != 'null':
                            return 'True'
           
        except Exception as e:
            pass

        return 'False'
    
    def isOrderExisted(self, id, username):
       
        if('Demo' in username):
            client = cosmos_client.CosmosClient(appui.demouri, appui.demorkey) 
            database = client.get_database_client(appui.demosupplierdb)

        else:
            client = cosmos_client.CosmosClient(appui.uri, appui.rkey) 
            database = client.get_database_client(appui.supplierdb)

        try:

            for cr in database.list_containers():
                
                if(appui.ordercr in cr['id']):

                    container = database.get_container_client(cr['id'])

                    if(len(id)==7 and isinstance(int(id), int)):

                        item = container.read_item(id,id)

                        if item != None and item != '' and item != 'null':
                            return 'True'
           
        except Exception as e:
            pass

        return 'False'
    
    def createPostLabel(self, text):
        self.exPopup = postlabel(text)
        #self.exPopup.setGeometry(100, 200, 800, 400)
        self.exPopup.setFixedWidth(800)
        self.exPopup.show()	

    def createDialog(self, text):

        self.newdialog = dialog(text)
        self.newdialog.show()

    def createDetailWindow(self, id, df, title):
        self.newwidget = detailwindow(id, df, title)
        self.newwidget.show()

class postlabel(QWidget):

    def __init__(self, text):
        super().__init__()

        #self.name = 'Post Label'
        self.setWindowTitle('Post Label')
        self.setWindowIcon(QIcon('logo.ico'))
        self.setMinimumHeight(200)
        self.setMaximumHeight(600)
        self.raise_()

        layout = QVBoxLayout(self)

        postLabel1 = QLabel(text, self)
        postLabel1.setFont(QFont('', 14))
        
        copybtn = QPushButton('Copy', self)

        layout.addWidget(postLabel1)
        layout.addWidget(QLabel('', self))
        layout.addWidget(QLabel('', self))
        layout.addWidget(copybtn)
        layout.setAlignment(Qt.AlignTop)

        copybtn.clicked.connect(lambda: self.click_copy(text))

    def click_copy(self, _str):
        pyperclip.copy(_str)
    
class dialog(QDialog):
    
    def __init__(self, text):

        super().__init__()

        self.setWindowTitle('Dialog')
        self.setWindowIcon(QIcon('logo.ico'))
        self.setMinimumHeight(100)
        self.raise_()

        layout = QVBoxLayout(self)

        dialogLabel = QLabel(text, self)
        dialogLabel.setFont(QFont('MV Boli', 14))
        
        okbtn = QPushButton('OK', self)
        okbtn.setFont(QFont('MV Boli', 14))
        okbtn.setMaximumWidth = 20

        layout.addWidget(dialogLabel)
        #layout.addWidget(QLabel('', self))
        #layout.addWidget(QLabel('', self))
        layout.addWidget(okbtn)
        layout.setAlignment(Qt.AlignTop)

        okbtn.clicked.connect(self.click_ok)
 
    def click_ok(self):
        self.destroy()       

class detailwindow(QWidget):

    def __init__(self, id, df, title):

        super().__init__()

        self.setWindowTitle(title+id)
        self.setWindowIcon(QIcon('logo.ico'))
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)      
        self.raise_() 

        final_df = pd.DataFrame(df)

        layout = QVBoxLayout(self)

        table = QTableWidget(self)

        if(len(final_df)==0):
            if('ZHTW' in self.label_username.text()):
                self.createDialog('找不到資料') 
            elif('ZHCN' in self.label_username.text()):
                self.createDialog('找不到资料') 
            else: 
                self.createDialog('No data found.')   

        else:
            table.setColumnCount(len(final_df.columns))     
            table.setRowCount(len(final_df))
            table.setHorizontalHeaderLabels(list(final_df.columns))
            table.horizontalHeader().setStretchLastSection(True)
            #table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            table.verticalHeader().setDefaultSectionSize(30)
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            #table.setSelectionMode(QAbstractItemView.SelectRows)

            for i in range(len(final_df)):
                for j in range(len(final_df.columns)):
                    table.setItem(i,j, QTableWidgetItem(str(final_df.iloc[i,j])))

            table.resizeRowsToContents()
            table.resizeColumnsToContents()    
        
        okbtn = QPushButton('OK', self)

        layout.addWidget(table)
        layout.addWidget(QLabel('', self))
        layout.addWidget(QLabel('', self))
        layout.addWidget(okbtn)
        layout.setAlignment(Qt.AlignTop)

        okbtn.clicked.connect(lambda: self.click_ok())

    def click_ok(self):
        self.destroy()

'''
if __name__ == '__main__': 
    app = QApplication(sys.argv)
    UIWindow = appui()
    UIWindow.openappwindow(QMainWindow(),'Demo','ReadWrite')
    app.exec_()
    sys.exit(app.exec_())
'''
        
    