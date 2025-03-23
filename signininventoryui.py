from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QPushButton, QTableWidget, QDialog, QTableWidgetItem, QAbstractItemView
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
#from loginui import loginui
import req
import requests, json, math
from pandas import json_normalize
from datetime import date
import azure.cosmos.cosmos_client as cosmos_client
import pandas as pd

class signininventoryui(QWidget):

    uri = req.azure_supplychain_uri
    rkey = req.azure_supplychain_readkey
    rwkey = req.azure_supplychain_readwritekey

    demouri = req.demo_azure_supplychain_uri
    demorkey = req.demo_azure_supplychain_readkey
    demorwkey = req.demo_azure_supplychain_readwritekey

    username = 'Demo'
    
    def openform(self, QWidget, username, role, lang):

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.start(1800000)

        self.setWindowIcon(QIcon('logo.ico'))

        if lang == 'ZHTW':
            uic.loadUi("SignInInventory_UI_ZHTW.ui",self)
            stlan = ', ZHTW繁中'
        elif lang == 'ZHCN':
            uic.loadUi("SignInInventory_UI_ZHCN.ui",self)
            stlan = ', ZHCN简中'
        else:    
            uic.loadUi("SignInInventory_UI.ui",self)
            stlan = ''
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle('Sign In Inventory')

        self.username = username

        if('Demo' not in username):
            self.signin_label_demo.setText(username+stlan)
        else:
            self.signin_label_demo.setText('Demo'+stlan)

        table = self.signin_tableWidget
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(50)
        table.verticalHeader().setDefaultSectionSize(5)

        self.signin_pushButton_search.clicked.connect(self.click_signin_pushButton_search)
        self.signin_pushButton_viewDetails.clicked.connect(self.click_signin_pushButton_viewDetails)
        self.signin_pushButton_signInAll.clicked.connect(self.click_signin_pushButton_signInAll)
        self.signin_pushButton_generateCSV.clicked.connect(self.click_signin_pushButton_generateCSV)

        self.show()      

    def click_signin_pushButton_search(self):

        self.timer.start(1800000)
        username = self.signin_label_demo.text()

        destination = str(self.signin_textEdit_warehouse.toPlainText())
        vendorID = str(self.signin_textEdit_vendorID.toPlainText()) 
        vendorEN = str(self.signin_textEdit_vendorEN.toPlainText())  
        orderID = str(self.signin_textEdit_orderID.toPlainText())
        trackNumber = str(self.signin_textEdit_trackingNumber.toPlainText()) 
        vendorOL = str(self.signin_textEdit_vendorOL.toPlainText())  

        final_df = pd.DataFrame()

        print(trackNumber)

        if('Demo' in username):
            client = cosmos_client.CosmosClient(signininventoryui.demouri, signininventoryui.demorkey) 
            database = client.get_database_client('demovendormanagement')

        else:
            client = cosmos_client.CosmosClient(signininventoryui.uri, signininventoryui.rkey) 
            database = client.get_database_client('vendormanagement')

        try:

            for cr in database.list_containers():
                
                if('logistics' in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(orderID)==7 and isinstance(int(orderID), int)):
                        body = container.read_item(orderID,orderID)['body']
                        jsondisplay = json.loads(body)
                        final_df = json_normalize(jsondisplay)
                        break

                    elif(trackNumber != ""  or  vendorOL != ""):

                        df_list, df_list2 = [], []
                        
                        for item in container.query_items(
                        query = 'SELECT * FROM c',
                        enable_cross_partition_query = True,
                        ):
                            
                            body = item['body']
                            df_list2 = json.loads(body)
                            track = df_list2['TrackingNumber']
                            vendorname = df_list2['VendorName']

                            if('True' in self.isValidEntry(track)):
                                print(track)

                            if('True' in self.isValidEntry(track) and 'True' in self.isValidEntry(vendorname) and trackNumber != '' and vendorOL != '' and trackNumber in track and vendorOL in vendorname):
                                df_list.append(df_list2)
                            elif(trackNumber != '' and 'True' in self.isValidEntry(track) and vendorOL == '' and trackNumber in track):
                                df_list.append(df_list2)
                            elif(trackNumber == '' and vendorOL != '' and 'True' in self.isValidEntry(vendorname) and vendorOL in vendorname):
                                df_list.append(df_list2)
                        
                        final_df = pd.DataFrame(df_list)
                        break

                    elif (orderID != "" or vendorID != "" or vendorEN != "" or destination != ""):
                        
                        querystr = 'SELECT * FROM c'

                        if (orderID != ""):

                            if("%" not in querystr):
                                querystr += f" WHERE c.body LIKE '%{orderID}%'"
                            else:
                                querystr += f" AND c.body LIKE '%{orderID}%'"

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
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.signin_label_demo.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        table = self.signin_tableWidget

        self.display_on_table(table, final_df)

    def click_signin_pushButton_viewDetails(self):
        self.timer.start(1800000)
        try: 
            row = self.signin_tableWidget.currentRow()

            #[{"ProductID":"102010000012","Quantity":"3","UnitPrice":"15"},{"ProductID":"105010000003","Quantity":"6","UnitPrice":"25"},{"ProductID":"105010000005","Quantity":"3","UnitPrice":"40"},{"ProductID":"105010000006","Quantity":"3","UnitPrice":"40"}]
            # [{"ProductID":"102010000012","Quantity":"5","UnitPrice":"45.6"},{"ProductID":"105010000005","Quantity":"6","UnitPrice":"45.6"}]
            detail = self.signin_tableWidget.item(row,16).text()
            id = self.signin_tableWidget.item(row,3).text()
        except:
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.signin_label_demo.text():
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

    def click_signin_pushButton_signInAll(self):
        self.timer.start(1800000)
        username = self.signin_label_demo.text()
        try:
            row = self.signin_tableWidget.currentRow()
            orderid = self.signin_tableWidget.item(row,3).text()
            detail = self.signin_tableWidget.item(row,16).text()
        except:
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.signin_label_demo.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return

        logistics_df, inventory_df = pd.DataFrame(), pd.DataFrame()
        destination, cargostatus, updatedat, updatedby = '', '', '', ''

        # update logistics
        if('Demo' in username):
            client = cosmos_client.CosmosClient(signininventoryui.demouri, signininventoryui.demorwkey) 
            database = client.get_database_client('demovendormanagement')

        else:
            client = cosmos_client.CosmosClient(signininventoryui.uri, signininventoryui.rwkey) 
            database = client.get_database_client('vendormanagement')

        try:

            for cr in database.list_containers():
                
                if('logistics' in cr['id']):
                    container = database.get_container_client(cr['id'])

                    if (len(orderid)==7 and isinstance(int(orderid), int)):
                        body = container.read_item(orderid,orderid)['body']
                        jsondisplay = json.loads(body)
                        logistics_df = json_normalize(jsondisplay)
                        break

        except Exception as e:
            pass
        
        if(len(logistics_df)>0):

            destination = str(logistics_df.at[0,'Destination'])
            cargostatus = str(logistics_df.at[0,'CargoStatus'])

            if(cargostatus != ''):
                cargostatus += '_'

            cargostatus += 'Fulfilled:'+date.today().strftime("%d-%b-%y")

            updatedat = date.today().strftime("%d-%b-%y")
            updatedby = username

            logistics_df.at[0,'CargoStatus'] = cargostatus
            logistics_df.at[0,'LastUpdatedAt'] = updatedat
            logistics_df.at[0,'LastUpdatedBy'] = updatedby

            try:

                key = logistics_df['OrderID'][0]
                data = logistics_df.iloc[0].to_json(orient='columns')
                container.upsert_item({'id': key, 'body':data})

            except: 
                if 'ZHTW' in self.signin_label_demo.text():
                    self.createDialog('系統錯誤，請聯繫IT團隊')
                elif 'ZHCN' in self.signin_label_demo.text():
                    self.createDialog('系统错误，请联繫IT团队')
                else: 
                    self.createDialog('System error. Contact IT support.')
   
        # update inventory

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

        if('Demo' in username):
            client = cosmos_client.CosmosClient(signininventoryui.demouri, signininventoryui.demorwkey) 
            database = client.get_database_client('demoinventorymanagement')

        else:
            client = cosmos_client.CosmosClient(signininventoryui.uri, signininventoryui.rwkey) 
            database = client.get_database_client('inventorymanagement')

        try:

            if(len(df)>0):

                for i in range(len(df)):

                    productid = str(df.at[i,'ProductID'])
                    quantity = str(df.at[i,'Quantity'])

                    if (destination != '' and len(productid)==12 and isinstance(int(productid), int)):

                        if(len(inventory_df) > 0):
                            inventory_df = inventory_df.drop(0)

                        for cr in database.list_containers():
                
                            if('inventory' in cr['id']):
                                container = database.get_container_client(cr['id'])

                                body = container.read_item(productid,productid)['body']
                                jsondisplay = json.loads(body)
                                inventory_df = json_normalize(jsondisplay)

                                inventory_df.at[0,'AtTransit'] = str(int(str(inventory_df.at[0,'AtTransit']))-int(quantity))
                                inventory_df.at[0,destination+'_Warehouse'] = str(int(str(inventory_df.at[0,destination+'_Warehouse']))+int(quantity))
                                inventory_df.at[0,'LastUpdatedAt'] = date.today().strftime("%d-%b-%y")
                                inventory_df.at[0,'LastUpdatedBy'] = username

                                if(len(inventory_df) > 0):
                                    try:

                                        key = inventory_df['ProductID'][0]
                                        data = inventory_df.iloc[0].to_json(orient='columns')
                                        container.upsert_item({'id': key, 'body':data})
                                        break

                                    except: 
                                        if 'ZHTW' in self.signin_label_demo.text():
                                            self.createDialog('系統錯誤，請聯繫IT團隊')
                                        elif 'ZHCN' in self.signin_label_demo.text():
                                            self.createDialog('系统错误，请联繫IT团队')
                                        else: 
                                            self.createDialog('System error. Contact IT support.')
                if 'ZHTW' in self.signin_label_demo.text():
                    self.createDialog('系統更新成功')
                elif 'ZHCN' in self.signin_label_demo.text():
                    self.createDialog('系统更新成功')
                else: 
                    self.createDialog('System update completes.')

            else:
                if 'ZHTW' in self.signin_label_demo.text():
                    self.createDialog('找不到產品，請重試')
                elif 'ZHCN' in self.signin_label_demo.text():
                    self.createDialog('找不到产品，请重试')
                else: 
                    self.createDialog('Product not found. Please retry.') 

        except Exception as e:
            pass

    def click_signin_pushButton_generateCSV(self):
        self.timer.start(1800000)
        table = self.signin_tableWidget

        col_count = table.columnCount()
        row_count = table.rowCount()
        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.signin_label_demo.text():
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
            filepath = self.get_save_csv_file_name('SignInInventory')
                
            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')

            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('CSV檔已儲存')
            elif 'ZHCN' in self.signin_label_demo.text():
                self.createDialog('CSV档已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('不正確的檔案路徑或是csv檔沒有關閉')
            elif 'ZHCN' in self.signin_label_demo.text():
                self.createDialog('不正确的档案路径或是csv档没有关闭')
            else: 
                self.createDialog('Please make sure you select a valid directory and the .csv file to be overwritten is closed.')
            return

    def isValidEntry(self, text):
        
        if('str' in str(type(text)) and text != '' and text != 'None' and text != 'none' and text != 'NULL' and text != 'null'):
            return 'True'
        else: 
            return 'False'

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
        
    def display_on_table(self, table, df):

        final_df = pd.DataFrame(df)

        if(len(final_df)==0):
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.signin_label_demo.text():
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

    def createDialog(self, text):

        self.newdialog = dialog(text)
        self.newdialog.show()
        
    def createDetailWindow(self, id, df, title):
        self.newwidget = detailwindow(id, df, title)
        self.newwidget.show()
    
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
            if 'ZHTW' in self.signin_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.signin_label_demo.text():
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
    UIWidget = signininventoryui()
    UIWidget.openform(QWidget(),'Demo','ReadWrite')
    app.exec_()
    sys.exit(app.exec_())
'''

