from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QPushButton, QDialog
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 

import req
import requests, json, math
from pandas import json_normalize
from datetime import date
import azure.cosmos.cosmos_client as cosmos_client
import pandas as pd

class orderformui(QWidget):

    uri = req.azure_supplychain_uri
    rkey = req.azure_supplychain_readkey
    rwkey = req.azure_supplychain_readwritekey

    demouri = req.demo_azure_supplychain_uri
    demorkey = req.demo_azure_supplychain_readkey
    demorwkey = req.demo_azure_supplychain_readwritekey

    username = 'Demo'
    
    def openform(self, QWidget, username, role, lang):

        self.setWindowIcon(QIcon('logo.ico'))
        
        if lang == 'ZHTW':
            uic.loadUi("OrderForm_UI_ZHTW.ui",self)
            stlan = ', ZHTW繁中'
        elif lang =='ZHCN':
            uic.loadUi("OrderForm_UI_ZHCN.ui",self)
            stlan = ', ZHCN简中'
        else:       
            uic.loadUi("OrderForm_UI.ui",self)
            stlan = ''
        
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle('New Order')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.start(1800000)

        self.username = username

        self.neworder_label_supplierName.setVisible(False)
        self.neworder_label_totalPayToSupplier.setVisible(False)
        self.neworder_label_vendorName.setVisible(False)

        if('Demo' not in username):
            self.neworder_label_demo.setText(username+stlan)
        else:
            self.neworder_label_demo.setText('Demo'+stlan)

        table = self.neworder_tableWidget
        table.setHorizontalHeaderLabels(['ProductID','Quantity','UnitPrice'])
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(50)
        table.verticalHeader().setDefaultSectionSize(5)

        self.neworder_pushButton_autoFill.clicked.connect(self.click_autoFill)
        self.neworder_pushButton_generateCSV.clicked.connect(self.click_generateCSV)

        self.show()      

    def click_autoFill(self):

        self.timer.start(1800000)
        suppliername= self.get_supplier_name(0)
        vendorname = self.get_vendor_name(0) +'('+self.get_vendor_name(2)+')'

        if(suppliername != ''):
            self.neworder_label_supplierName.setText(suppliername)
            self.neworder_label_supplierName.setStyleSheet("color:gray")
            self.neworder_label_supplierName.setVisible(True)

        if(vendorname != ''):
            self.neworder_label_vendorName.setText(vendorname)
            self.neworder_label_vendorName.setStyleSheet("color:gray")
            self.neworder_label_vendorName.setVisible(True)

                
        table = self.neworder_tableWidget

        row_count = table.rowCount()
       
        sum =0.0

        for row in range(row_count):

            item = '' if table.item(row,0) is None or not str.isnumeric(str(table.item(row,0).text())) else str(table.item(row,0).text())

            if(item != ''):
                quantity = '' if item is '' or table.item(row,1) is None else str(table.item(row,1).text()) 
                unitprice ='' if item is '' or table.item(row,2) is None else str(table.item(row,2).text())
                if(quantity != '' and unitprice != ''):
                    sum += float(quantity) * float(unitprice)

        if (self.neworder_checkBox_payExportTaxToSupplier.isChecked()):

            exportTax = str(self.neworder_textEdit_exportTax.toPlainText())

            if(exportTax != ''):
                sum += float(exportTax)
                sum = round(sum,2)

        if (sum != 0):
            self.neworder_label_totalPayToSupplier.setText('TotalPayToSupplier:'+str(sum))
            self.neworder_label_totalPayToSupplier.setStyleSheet("color:red")
            self.neworder_label_totalPayToSupplier.setVisible(True)

    def click_generateCSV(self):
        self.timer.start(1800000)
        if (self.is_order_id_existed() == 'existed'):
            if 'ZHTW' in self.neworder_label_demo.text():
                self.createDialog('此訂單已存在，請更新')
            elif 'ZHCN' in self.neworder_label_demo.text():
                self.createDialog('此订单已存在，请更新')
            else: 
                self.createDialog('This order exists. Please update')
            return

        filepath = self.get_save_csv_file_name()

        if(filepath==''):
            return

        action = 'New'
        actionnote = ''
        status = 'Waiting for Approval'
        orderid = str(self.neworder_textEdit_orderID.toPlainText())
        supplierid = str(self.neworder_textEdit_supplierID.toPlainText())
        suppliername = str(self.neworder_label_supplierName.text())
        suppliernameen = str(self.get_supplier_name(1))
        currency = str(self.newoder_textEdit_supplierCurrency.toPlainText())

        exporttax = round(float(str(self.neworder_textEdit_exportTax.toPlainText())),2) if str(self.neworder_textEdit_exportTax.toPlainText()) != '' and str.isnumeric(str(self.neworder_textEdit_exportTax.toPlainText())) else ''

        exporttaxincluded = ''
        if(self.neworder_checkBox_exportTaxIncluded.isChecked()):
            exporttaxincluded = 'Y'
        else: 
            exporttaxincluded = 'N'
        
        totalpaysupplier = round(float(str(self.neworder_label_totalPayToSupplier.text()).replace('TotalPayToSupplier:','')),2) if str(self.neworder_label_totalPayToSupplier.text()).replace('TotalPayToSupplier:','') != '' else ''
        supplierpaymenttype = self.get_supplier_payment_type()

        importtaxcurrency = ''

        if(str(self.neworder_textEdit_destination.toPlainText()) != ''):

            country = str(self.neworder_textEdit_destination.toPlainText())

            if(country == 'AU'):
                importtaxcurrency = 'AUD'
            elif('US' in country or 'USA' in country):
                importtaxcurrency = 'USD'
            elif(country == 'CN'):
                importtaxcurrency = 'CNY'
            elif(country == 'CA'):
                importtaxcurrency = 'CAD'
            elif(country == 'NZ' or country == 'NZL'):
                importtaxcurrency = 'NZD'
            elif(country == 'TW'):
                importtaxcurrency = 'TWD'
            elif(country == 'Thai' or country == 'TH'):
                importtaxcurrency = 'THB'
            elif('EU'in country):
                importtaxcurrency = 'Euro'
            else:
                importtaxcurrency = 'Other'

        importtax = round(float(str(self.neworder_textEdit_importTax.toPlainText())),2) if str(self.neworder_textEdit_importTax.toPlainText()) != '' and str.isnumeric(str(self.neworder_textEdit_importTax.toPlainText())) else ''

        importtaxincluded = ''
        if(self.neworder_checkBox_importTaxIncluded.isChecked()):
            importtaxincluded = 'Y'
        else: 
            importtaxincluded = 'N'

        totalpayimporttax = round(float(str(self.neworder_textEdit_importTax.toPlainText())),2) if str(self.neworder_textEdit_importTax.toPlainText()) != '' and str.isnumeric(str(self.neworder_textEdit_importTax.toPlainText())) else ''
        importtaxpaymenttype = self.get_import_tax_payment_type()
        postcurrency = str(self.neworder_textEdit_vendorCurrency.toPlainText())
        postfee = round(float(str(self.neworder_textEdit_postFee.toPlainText())),2) if str(self.neworder_textEdit_postFee.toPlainText()) != '' and str.isnumeric(str(self.neworder_textEdit_postFee.toPlainText())) else ''

        postincluded = ''
        if(self.neworder_checkBox_postIncluded.isChecked()):
            postincluded = 'Y'
        else: 
            postincluded = 'N'

        totalpaypost = round(float(str(self.neworder_textEdit_postFee.toPlainText())),2) if str(self.neworder_textEdit_postFee.toPlainText()) != '' and str.isnumeric(str(self.neworder_textEdit_postFee.toPlainText())) else ''
        postpaymenttype = self.get_postage_payment_type()
        destination = str(self.neworder_textEdit_destination.toPlainText())
        vendorid = str(self.neworder_textEdit_vendorID.toPlainText())
        vendorname = self.get_vendor_name(0)
        vendornameen = self.get_vendor_name(1)
        vendorclientaccount = self.get_vendor_name(2)
        createdat = date.today().strftime("%d-%b-%y")
        createdby = self.username
        updatedat = date.today().strftime("%d-%b-%y")
        updatedby = self.username
        approveat = ''
        approveby = ''   

        table = self.neworder_tableWidget

        row_count = table.rowCount()
       
        sum1 =0.0
        list1 = ['ProductID','Quantity','UnitPrice']
        df1 = pd.DataFrame(columns= list1)

        for row in range(row_count):

            item = '' if table.item(row,0) is None or not str.isnumeric(str(table.item(row,0).text())) else str(table.item(row,0).text())

            if(item != ''):
                quantity = '' if item is '' or table.item(row,1) is None else str(table.item(row,1).text()) 
                unitprice ='' if item is '' or table.item(row,2) is None else str(table.item(row,2).text())
                if(quantity != '' and unitprice != ''):
                    sum1 += float(quantity) * float(unitprice)
                    df1.loc[len(df1)] = [item,quantity,unitprice]
        
        json = df1.to_json(orient='records')

        details = json
        sum = round(sum1,2)


        list = ['Action', 'ActionNote', 'Status', 'OrderID', 'SupplierID', 'SupplierName', 'SupplierName(EN)', 'Currency', 'Details' ,'Sum', 'ExportTax', 'ExportTaxIncluded(Y/N)', 'TotalPaySupplier', 'SupplierPaymentType', 'ImportTaxCurrency', 'ImportTax', 'ImportTaxIncluded(Y/N)', 'TotalPayImportTax', 'ImportTaxPaymentType', 'PostageCurrency', 'PostageFee', 'PostIncluded(Y/N)', 'TotalPayPostage', 'PostagePaymentType', 'Destination', 'VendorID', 'VendorName', 'VendorName(EN)', 'VendorClientAccount', 'CreatedAt',	'CreatedBy', 'LastUpdatedAt', 'LastUpdatedBy', 'ChangesApprovedAt', 'ChangesApprovedBy']
        list2 = [action, actionnote, status, orderid, supplierid, suppliername, suppliernameen, currency, details , sum, exporttax, exporttaxincluded, totalpaysupplier, supplierpaymenttype, importtaxcurrency, importtax, importtaxincluded, totalpayimporttax, importtaxpaymenttype, postcurrency, postfee, postincluded, totalpaypost, postpaymenttype, destination, vendorid, vendorname, vendornameen, vendorclientaccount, createdat, createdby, updatedat, updatedby, approveat, approveby]
        df = pd.DataFrame(columns = list)
        df.loc[len(df)] = list2
        
        try: 
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')
            if 'ZHTW' in self.neworder_label_demo.text():
                self.createDialog('CSV檔已儲存')
            elif 'ZHCN' in self.neworder_label_demo.text():
                self.createDialog('CSV档已储存')
            else: 
                self.createDialog('CSV file generated!')
        except: 
            if 'ZHTW' in self.neworder_label_demo.text():
                self.createDialog('不正確的檔案路徑或是csv檔沒有關閉')
            elif 'ZHCN' in self.neworder_label_demo.text():
                self.createDialog('不正确的档案路径或是csv档没有关闭')
            else: 
                self.createDialog('Please make sure you select a valid directory and the .csv file to be overwritten is closed.')
            return

    def get_supplier_name(self, d):
        
        name, name1= '', ''
        id = str(self.neworder_textEdit_supplierID.toPlainText())

        if('Demo' in self.username):
            client = cosmos_client.CosmosClient(orderformui.demouri, orderformui.demorkey) 
            database = client.get_database_client('demosuppliermanagement')

        else:
            client = cosmos_client.CosmosClient(orderformui.uri, orderformui.rkey) 
            database = client.get_database_client('suppliermanagement')
        if(id != ''):
            try:

                for cr in database.list_containers():
                    
                    if('supplier' in cr['id']):
                        container = database.get_container_client(cr['id'])

                        if(len(id)==12 and isinstance(int(id), int)):
                            body = container.read_item(id,id)['body']
                            final_df = json_normalize(json.loads(body))
                            name = final_df['Name'][0]
                            name1 = final_df['Name(EN)'][0]

            except:
                pass
        if (d ==0):
            return name
        else: 
            return name1

    def get_vendor_name(self, d):

        name, name1, name2 = '', '',''
        id = str(self.neworder_textEdit_vendorID.toPlainText())

        if('Demo' in self.username):
            client = cosmos_client.CosmosClient(orderformui.demouri, orderformui.demorkey) 
            database = client.get_database_client('demovendormanagement')

        else:
            client = cosmos_client.CosmosClient(orderformui.uri, orderformui.rkey) 
            database = client.get_database_client('vendormanagement')

        if(id != ''):
            try:

                for cr in database.list_containers():
                    
                    if('vendor' in cr['id']):
                        container = database.get_container_client(cr['id'])

                        if(len(id)==7 and isinstance(int(id), int)):
                            body = container.read_item(id,id)['body']
                            final_df = json_normalize(json.loads(body))
                            name = final_df['Name'][0]
                            name1 = final_df['Name(EN)'][0]
                            name2 = final_df['ClientAccount'][0]
                            
            except:
                pass
        if (d ==0):
            return name
        elif (d==1):
            return name1
        else: 
            return name2

    def is_order_id_existed(self):
       
        text = 'ok'

        id = str(self.neworder_textEdit_orderID.toPlainText())

        if('Demo' in self.username):
            client = cosmos_client.CosmosClient(orderformui.demouri, orderformui.demorkey) 
            database = client.get_database_client('demosuppliermanagement')

        else:
            client = cosmos_client.CosmosClient(orderformui.uri, orderformui.rkey) 
            database = client.get_database_client('suppliermanagement')

        try:
            for cr in database.list_containers():
                
                if('order' in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if(len(id)==7 and isinstance(int(id), int)):

                        item = container.read_item(id,id)

                        if item != None and item != '' and item != 'null':
                            text = 'existed'
                            break
            
        except Exception as e:
            pass

        return text
        
    def get_supplier_payment_type(self):

        type = ''

        if(self.neworder_checkBox_supplierCheck.isChecked()):
            type = 'Check'
        
        elif(self.neworder_checkBox_supplierTransfer.isChecked()):
            type = 'Transfer'
        
        elif(self.neworder_checkBox_supplierCard.isChecked()):
            type = 'Card'
        
        elif(self.neworder_checkBox_supplierOther.isChecked()):
            type = str(self.neworder_textEdit_supplierOtherSP.toPlainText())     

        return type

    def get_import_tax_payment_type(self):

        type = ''

        if(self.neworder_checkBox_importTaxCheck.isChecked()):
            type = 'Check'
        
        elif(self.neworder_checkBox_importTaxDebit.isChecked()):
            type = 'Debit'
        
        elif(self.neworder_checkBox_importTaxCard.isChecked()):
            type = 'Card'
        
        elif(self.neworder_checkBox_importTaxOther.isChecked()):
            type = str(self.neworder_textEdit_importTaxOtherSP.toPlainText())     

        return type

    def get_postage_payment_type(self):

        type = ''

        if(self.neworder_checkBox_postAccountDebit.isChecked()):
            type = 'AccountDebit'
        
        elif(self.neworder_checkBox_postCheck.isChecked()):
            type = 'Check'
        
        elif(self.neworder_checkBox_postCard.isChecked()):
            type = 'Card'
        
        elif(self.neworder_checkBox_postOther.isChecked()):
            type = str(self.neworder_textEdit_postOtherSP.toPlainText())     

        return type

    def get_save_csv_file_name(self):

        filename = 'Order'

        orderid = str(self.neworder_textEdit_orderID.toPlainText())

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
        self.newdialog.show()

    def timeout(self):
        #self.exit()
        #self.visibility = False
        self.destroy()
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
    UIWidget = orderformui()
    UIWidget.openform(QWidget(),'Demo','ReadWrite')
    app.exec_()
    sys.exit(app.exec_())

'''