from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QPushButton, QDialog
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 

import req
import requests, math
from datetime import date
import sys, os, random, pyotp, json
import azure.cosmos.cosmos_client as cosmos_client
import pandas as pd
from pandas import json_normalize

class logisticsformui(QWidget):

    uri = req.azure_supplychain_uri
    rkey = req.azure_supplychain_readkey
    rwkey = req.azure_supplychain_readwritekey

    demouri = req.demo_azure_supplychain_uri
    demorkey = req.demo_azure_supplychain_readkey
    demorwkey = req.demo_azure_supplychain_readwritekey

    username = 'Demo'
    
    def openform(self, QWidget, username, role, lang):

        if lang == 'ZHTW':
            uic.loadUi("LogisticsForm_UI_ZHTW.ui",self)
            stlan = ', ZHTW繁中'
        elif lang =='ZHCN':
            uic.loadUi("LogisticsForm_UI_ZHCN.ui",self)
            stlan = ', ZHCN简中'
        else:       
            uic.loadUi("LogisticsForm_UI.ui",self)
            stlan = ''
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle('New Logisitics')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.start(1800000)

        self.username = username

        self.logistics_label_destination.setVisible(False)
        self.logistics_label_vendorName.setVisible(False)

        if('Demo' not in username):
            self.logistics_label_demo.setText(username+stlan)
        else:
            self.logistics_label_demo.setText('Demo'+stlan)

        table = self.logistics_tableWidget
        table.setHorizontalHeaderLabels(['ProductID','Quantity','UnitPrice'])
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(50)
        table.verticalHeader().setDefaultSectionSize(5)

        self.logistics_pushButton_autoFill.clicked.connect(self.click_autoFill)
        self.logistics_pushButton_generateCSV.clicked.connect(self.click_generateCSV)
        self.logistics_pushButton_updateSystem.clicked.connect(self.click_updateSystem)

        self.show()      

    def click_autoFill(self):

        username = self.logistics_label_demo.text()
        orderID = self.logistics_textEdit_orderID.toPlainText()
        vendorID = self.logistics_textEdit_vendorID.toPlainText()
        destination, vendorname = '', ''


        if('Demo' in username):
            client = cosmos_client.CosmosClient(self.demouri, self.demorkey) 
            orderdatabase = client.get_database_client('demosuppliermanagement')
            vendordatabase = client.get_database_client('demovendormanagement')

        else:
            client = cosmos_client.CosmosClient(self.uri, self.rkey) 
            orderdatabase = client.get_database_client('suppliermanagement')
            vendordatabase = client.get_database_client('vendormanagement')

        try:

            for cr in orderdatabase.list_containers():
                
                if('order' in cr['id']):
                    container = orderdatabase.get_container_client(cr['id'])

                    if (len(orderID)==7 and isinstance(int(orderID), int)):
                        body = container.read_item(orderID,orderID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        destination = str(final_df.at[0,'Destination'])
                        break


            for cr in vendordatabase.list_containers():
                
                if('vendor' in cr['id']):
                    container = vendordatabase.get_container_client(cr['id'])

                    if (len(vendorID)==7 and isinstance(int(vendorID), int)):
                        body = container.read_item(vendorID,vendorID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        vendorname = str(final_df.at[0,'Name'])
                        break
        except:
            pass

        if(vendorname != ''):
            self.logistics_label_vendorName.setText('Vender:'+vendorname)
            self.logistics_label_vendorName.setStyleSheet("color:gray")
            self.logistics_label_vendorName.setVisible(True)
        else:
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('請輸入正確物流商編號')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('请输入正确物流商编号')
            else: 
                self.createDialog('Please enter valid vendorID.')


        if(destination != ''):
            self.logistics_label_destination.setText('Destination:'+destination)
            self.logistics_label_destination.setStyleSheet("color:gray")
            self.logistics_label_destination.setVisible(True)
        else:
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('請輸入正確訂單編號')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('请输入正确订单编号')
            else: 
                self.createDialog('Please enter valid orderID.')

    def click_generateCSV(self):

        orderid = self.logistics_textEdit_orderID.toPlainText()
        vendorid = self.logistics_textEdit_vendorID.toPlainText()

        if(orderid == '' or len(orderid) != 7 or not isinstance(int(orderid),int)):
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('請輸入正確訂單編號')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('请输入正确订单编号')
            else: 
                self.createDialog('Please enter valid orderID.')
            return
        elif(vendorid == '' or len(vendorid) != 7 or not isinstance(int(vendorid),int)):
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('請輸入正確物流商編號')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('请输入正确物流商编号')
            else: 
                self.createDialog('Please enter valid vendorID.')
            return


        filepath = self.get_save_csv_file_name()

        action = 'New'
        actionnote = ''
        status = 'Approved'
        
        supplierid = str(self.get_supplier_name(0))
        suppliername = str(self.get_supplier_name(1))
        suppliernameen = str(self.get_supplier_name(2))
        destination = str(self.logistics_label_destination.text()).replace('Destination:','')
        
        posttype =''

        if(self.logistics_checkBox_air.isChecked()):
            posttype = 'Air'
        elif(self.logistics_checkBox_surface.isChecked()):
            posttype = 'Surface'

        vendorname = self.get_vendor_name(0)
        vendornameen = self.get_vendor_name(1)
        vendorclientaccount = self.get_vendor_name(2)
        tracknumber = self.logistics_textEdit_trackingNumber.toPlainText()
        trackurl = self.logistics_textEdit_trackingURL.toPlainText()

        cargostatus = ''

        if(self.logistics_checkBox_posted.isChecked()):
            cargostatus = 'Posted:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_exportCustom.isChecked()):
            cargostatus = 'ExportCustom:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_international.isChecked()):
            cargostatus = 'International:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_importCustom.isChecked()):
            cargostatus = 'ImportCustom:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_delivering.isChecked()):
            cargostatus = 'LocalDelivering:'+date.today().strftime("%d-%b-%y")

        eta = (self.logistics_dateEdit_ETA.date()).toPyDate().strftime("%d-%b-%y")
        postat = (self.logistics_dateEdit_postedAt.date()).toPyDate().strftime("%d-%b-%y")
        postby = self.logistics_textEdit_postedBy.toPlainText()
        createdat = date.today().strftime("%d-%b-%y")
        createdby = self.username
        updatedat = date.today().strftime("%d-%b-%y")
        updatedby = self.username
        approveat = date.today().strftime("%d-%b-%y")
        approveby = self.username

        table = self.logistics_tableWidget

        row_count = table.rowCount()
       
        sum1 =0.0
        list1 = ['ProductID','Quantity','UnitPrice']
        df1 = pd.DataFrame(columns= list1)

        for row in range(row_count):

            item = '' if table.item(row,0) is None or not str.isnumeric(str(table.item(row,0).text())) else str(table.item(row,0).text())

            if(item != ''):
                sku = '' if item is '' or table.item(row,1) is None else str(table.item(row,1).text()) 
                unitprice ='' if item is '' or table.item(row,2) is None else str(table.item(row,2).text())
                if(sku != '' and unitprice != ''):
                    sum1 += float(sku) * float(unitprice)
                    df1.loc[len(df1)] = [item,sku,unitprice]
        
        json1 = df1.to_json(orient='records')

        details = json1														

        list = ['Action', 'ActionNote', 'Status', 'OrderID', 'SupplierID', 'SupplierName', 'SupplierName(EN)', 'Destination', 'PostType' ,'VendorID', 'VendorName', 'VendorName(EN)', 'VendorClientAccount', 'TrackingNumber', 'TrackingURL', 'CargoStatus', 'Details', 'ETA', 'PostedAt', 'PostedBy', 'CreatedAt', 'CreatedBy', 'LastUpdatedAt', 'LastUpdatedBy', 'ChangesApprovedAt', 'ChangesApprovedBy']
        list2 = [action, actionnote, status, orderid, supplierid, suppliername, suppliernameen, destination, posttype , vendorid, vendorname, vendornameen, vendorclientaccount, tracknumber, trackurl, cargostatus, details, eta, postat, postby, createdat, createdby, updatedat, updatedby, approveat, approveby]
        df = pd.DataFrame(columns = list)
        df.loc[len(df)] = list2
        
        try: 
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('CSV檔案已儲存')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('CSV档案已储存')
            else: 
                self.createDialog('CSV file generated!')
        except: 
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('不正確的檔案路徑或是csv檔沒有關閉')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('不正确的档案路径或是csv档没有关闭')
            else: 
                self.createDialog('Please make sure you select a valid directory and the .csv file to be overwritten is closed.')
            return

    def click_updateSystem(self):

        orderid = self.logistics_textEdit_orderID.toPlainText()
        vendorid = self.logistics_textEdit_vendorID.toPlainText()
        username = self.logistics_label_demo.text()
        final_df = pd.DataFrame()
        cargostatus = ''

        if(orderid == '' or len(orderid) != 7 or not isinstance(int(orderid),int)):
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('請輸入正確訂單編號')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('请输入正确订单编号')
            else: 
                self.createDialog('Please enter valid order ID.')
            return
        elif(vendorid == '' or len(vendorid) != 7 or not isinstance(int(vendorid),int)):
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('請輸入正確物流商編號')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('请输入正确物流商编号')
            else: 
                self.createDialog('Please enter valid vendor ID.')
            return

        if('Demo' in username):
            client = cosmos_client.CosmosClient(self.demouri, self.demorwkey) 
            database = client.get_database_client('demovendormanagement')

        else:
            client = cosmos_client.CosmosClient(self.uri, self.rwkey) 
            database = client.get_database_client('vendormanagement')
        try:

            for cr in database.list_containers():
                        
                if('logistics' in cr['id']):
                    container = database.get_container_client(cr['id'])

                    body = container.read_item(orderid,orderid)['body']
                    jsondisplay = json.loads(body)
                    final_df = json_normalize(jsondisplay)
                    break

        except Exception as e:
            pass

        if(len(final_df)>0):
            cargostatus = str(final_df.at[0,'CargoStatus'])

        action = 'New'
        actionnote = ''
        status = 'Approved'
        supplierid = str(self.get_supplier_name(0))
        suppliername = str(self.get_supplier_name(1))
        suppliernameen = str(self.get_supplier_name(2))
        destination = str(self.logistics_label_destination.text()).replace('Destination:','')
        
        posttype =''

        if(self.logistics_checkBox_air.isChecked()):
            posttype = 'Air'
        elif(self.logistics_checkBox_surface.isChecked()):
            posttype = 'Surface'

        vendorname = self.get_vendor_name(0)
        vendornameen = self.get_vendor_name(1)
        vendorclientaccount = self.get_vendor_name(2)
        tracknumber = self.logistics_textEdit_trackingNumber.toPlainText()
        trackurl = self.logistics_textEdit_trackingURL.toPlainText()

        if(self.logistics_checkBox_posted.isChecked()):
            if(cargostatus != ''):
                cargostatus += '_'
            cargostatus += 'Posted:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_exportCustom.isChecked()):
            if(cargostatus != ''):
                cargostatus += '_'
            cargostatus += 'ExportCustom:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_international.isChecked()):
            if(cargostatus != ''):
                cargostatus += '_'
            cargostatus += 'International:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_importCustom.isChecked()):
            if(cargostatus != ''):
                cargostatus += '_'
            cargostatus += 'ImportCustom:'+date.today().strftime("%d-%b-%y")
        elif(self.logistics_checkBox_delivering.isChecked()):
            if(cargostatus != ''):
                cargostatus += '_'
            cargostatus += 'LocalDelivering:'+date.today().strftime("%d-%b-%y")

        eta = (self.logistics_dateEdit_ETA.date()).toPyDate().strftime("%d-%b-%y")
        postat = (self.logistics_dateEdit_postedAt.date()).toPyDate().strftime("%d-%b-%y")
        postby = self.logistics_textEdit_postedBy.toPlainText()
        createdat = date.today().strftime("%d-%b-%y")
        createdby = self.username
        updatedat = date.today().strftime("%d-%b-%y")
        updatedby = self.username
        approveat = date.today().strftime("%d-%b-%y")
        approveby = self.username

        table = self.logistics_tableWidget

        row_count = table.rowCount()
       
        sum1 =0.0
        list1 = ['ProductID','Quantity','UnitPrice']
        df1 = pd.DataFrame(columns= list1)

        for row in range(row_count):

            item = '' if table.item(row,0) is None or not str.isnumeric(str(table.item(row,0).text())) else str(table.item(row,0).text())

            if(item != ''):
                sku = '' if item is '' or table.item(row,1) is None else str(table.item(row,1).text()) 
                unitprice ='' if item is '' or table.item(row,2) is None else str(table.item(row,2).text())
                if(sku != '' and unitprice != ''):
                    sum1 += float(sku) * float(unitprice)
                    df1.loc[len(df1)] = [item,sku,unitprice]
        
        json1 = df1.to_json(orient='records')

        details = json1														

        if(len(final_df)==0):
            list = ['Action', 'ActionNote', 'Status', 'OrderID', 'SupplierID', 'SupplierName', 'SupplierName(EN)', 'Destination', 'PostType' ,'VendorID', 'VendorName', 'VendorName(EN)', 'VendorClientAccount', 'TrackingNumber', 'TrackingURL', 'CargoStatus', 'Details', 'ETA', 'PostedAt', 'PostedBy', 'CreatedAt', 'CreatedBy', 'LastUpdatedAt', 'LastUpdatedBy', 'ChangesApprovedAt', 'ChangesApprovedBy']
            list2 = [action, actionnote, status, orderid, supplierid, suppliername, suppliernameen, destination, posttype , vendorid, vendorname, vendornameen, vendorclientaccount, tracknumber, trackurl, cargostatus, details, eta, postat, postby, createdat, createdby, updatedat, updatedby, approveat, approveby]
            df = pd.DataFrame(columns = list)
            df.loc[len(df)] = list2
        else:
            df = final_df
            df.at[0,'CargoStatus'] = cargostatus
        
        try: 

            key = df['OrderID'][0]
            data = df.iloc[0].to_json(orient='columns')
            container.upsert_item({'id': key, 'body':data})
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('系統更新完成')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('系统更新完成')
            else: 
                self.createDialog('Update completes.')

        except: 
            if 'ZHTW' in self.logistics_label_demo.text():
                self.createDialog('系統錯誤，請聯繫IT團隊')
            elif 'ZHCN' in self.logistics_label_demo.text():
                self.createDialog('系统错误，请联繫IT团队')
            else: 
                self.createDialog('System error. Contact IT support.')

    def timeout(self):
        #self.exit()
        #self.visibility = False
        self.destroy()
    #------------------------------Call Methods------------------------------

    def get_supplier_name(self, d):
        
        id, name, name1= '', '', ''

        orderID = self.logistics_textEdit_orderID.toPlainText()

        if('Demo' in self.username):
            client = cosmos_client.CosmosClient(self.demouri, self.demorkey) 
            database = client.get_database_client('demosuppliermanagement')

        else:
            client = cosmos_client.CosmosClient(self.uri, self.rkey) 
            database = client.get_database_client('suppliermanagement')


        if(orderID != '' and len(orderID)==7 and isinstance(int(orderID),int)):

            try:

                for cr in database.list_containers():
                    
                    if('order' in cr['id']):
                        container = database.get_container_client(cr['id'])

                        body = container.read_item(orderID,orderID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        id = str(final_df.at[0,'SupplierID'])
                        name = str(final_df.at[0,'SupplierName'])
                        name1 = str(final_df.at[0,'SupplierName(EN)'])
                        break

            except:
                pass

        if (d ==0):
            return id
        elif(d ==1):
            return name
        else:
            return name1

    def get_vendor_name(self, d):

        name, name1, name2 = '', '',''
        id = str(self.logistics_textEdit_vendorID.toPlainText())

        if('Demo' in self.username):
            client = cosmos_client.CosmosClient(self.demouri, self.demorkey) 
            database = client.get_database_client('demovendormanagement')

        else:
            client = cosmos_client.CosmosClient(self.uri, self.rkey) 
            database = client.get_database_client('vendormanagement')

        if(id != '' and len(id)==7 and isinstance(int(id),int)):

            try:

                for cr in database.list_containers():
                    
                    if('vendor' in cr['id']):
                        container = database.get_container_client(cr['id'])

                        body = container.read_item(id,id)['body']
                        final_df = json_normalize(json.loads(body))
                        name = str(final_df.at[0,'Name'])
                        name1 = str(final_df.at[0,'Name(EN)'])
                        name2 = str(final_df.at[0,'ClientAccount'])
                            
            except:
                pass
        if (d ==0):
            return name
        elif (d==1):
            return name1
        else: 
            return name2
      
    def get_existed_df(self, database, orderid):

        final_df = pd.DataFrame()

        try:

            if(orderid != '' and len(orderid)==7 and isinstance(int(orderid),int)):

                for cr in database.list_containers():
                    
                    if('logistics' in cr['id']):
                        container = database.get_container_client(cr['id'])

                        body = container.read_item(orderid,orderid)['body']
                        print(body)
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        print(final_df)
                        break

        except Exception as e:
            print(repr(e))

        return final_df

    def get_save_csv_file_name(self):

        filename = 'New Logistics_Order'

        orderid = str(self.logistics_textEdit_orderID.toPlainText())

        if(orderid != ''):
            filename += '_'+orderid
        filename += '_'+date.today().strftime("%d-%b-%y")

        file_filter = 'Data File (*.csv)'
        response = QFileDialog.getSaveFileName(
            parent = self,
            caption = 'Select a data file',
            directory = filename,
            filter = file_filter,
            initialFilter=file_filter
        )
        return response[0]

    def createDialog(self, text):

        self.newdialog = dialog(text)
        self.newdialog.raise_()
        self.newdialog.show()

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

'''
if __name__ == '__main__': 

    app = QApplication(sys.argv)
    UIWidget = logisticsformui()
    UIWidget.openform(QWidget(),'Demo','ReadWrite')
    app.exec_()
    sys.exit(app.exec_())
'''

