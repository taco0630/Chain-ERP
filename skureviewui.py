from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QPushButton, QDialog
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 

import requests, json, math
from pandas import json_normalize
from datetime import date
import pandas as pd


class skureviewui(QWidget):

    username = 'Demo'
    
    def openform(self, QWidget, username, role, lang):

        if lang == 'ZHTW':
            uic.loadUi("SKUReview_UI_ZHTW.ui",self)
            stlan = ', ZHTW繁中'
        elif lang == 'ZHCN':
            uic.loadUi("SKUReview_UI_ZHCN.ui",self)
            stlan = ', ZHCN简中'
        else:
            uic.loadUi("SKUReview_UI.ui",self)
            stlan = ''
            
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle('Inventory Review')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.start(1800000)
        
        self.username = username

        if('Demo' not in username):
            self.skureview_label_demo.setText(username+stlan)
        else:
            self.skureview_label_demo.setText('Demo'+stlan)

        table = self.skureview_tableWidget
        table.setHorizontalHeaderLabels(['ProductID','Quantity'])
        table.horizontalHeader().setStretchLastSection(True)
        table.setRowCount(50)
        table.verticalHeader().setDefaultSectionSize(5)

        self.skureview_pushButton_add50Lines.clicked.connect(self.click_add50Lines)
        self.skureview_pushButton_generateCSV.clicked.connect(self.click_generateCSV)

        self.show()      

    def click_add50Lines(self):
        self.timer.start(1800000)
        table = self.skureview_tableWidget
        row_count = table.rowCount()
        table.setRowCount(row_count+50)

    def click_generateCSV(self):
        self.timer.start(1800000)
        addedat = date.today().strftime("%d-%b-%y")
        addedby = self.username

        warehouse = str(self.skureview_textEdit_warehouse.toPlainText())
        
        table = self.skureview_tableWidget

        col_count = table.columnCount()
        row_count = table.rowCount()
        try:
            headers = [str(table.horizontalHeaderItem(i).text()) for i in range(col_count)]
        except:
            if 'ZHTW' in self.skureview_label_demo.text():
                self.createDialog('找不到資料')
            elif 'ZHCN' in self.skureview_label_demo.text():
                self.createDialog('找不到资料')
            else: 
                self.createDialog('No data found.')
            return
        headers.append('AddedAt')
        headers.append('AddedBy')

        # df indexing is slow, so use lists
        df_list = []
        for row in range(row_count):
            df_list2 = []
            for col in range(col_count+2):

                productid = '' if table.item(row,0) is None or not str.isnumeric(str(table.item(row,0).text())) else str(table.item(row,0).text())

                if('True' in self.isValidEntry(productid)):
 
                    if(col <2):
                        table_item = table.item(row,col)
                        df_list2.append('' if table_item is None else str(table_item.text()))
                    elif(col ==2):
                        df_list2.append(addedat)
                    elif(col ==3):
                        df_list2.append(addedby)
            if(df_list2):
                df_list.append(df_list2)

        df = pd.DataFrame(df_list, columns=headers)

        filename = 'Inventory Review'

        if(warehouse != ''):
            filename = warehouse+'_'+filename
        try:
            filepath = self.get_save_csv_file_name(filename)

            df.to_csv(filepath, index=False, encoding = 'utf-8_sig')

            if 'ZHTW' in self.skureview_label_demo.text():
                self.createDialog('CSV檔已儲存')
            elif 'ZHCN' in self.skureview_label_demo.text():
                self.createDialog('CSV档已储存')
            else: 
                self.createDialog('CSV file is saved.')
        except:
            if 'ZHTW' in self.skureview_label_demo.text():
                self.createDialog('不正確的檔案路徑或是csv檔沒有關閉')
            elif 'ZHCN' in self.skureview_label_demo.text():
                self.createDialog('不正确的档案路径或是csv档没有关闭')
            else: 
                self.createDialog('Please make sure you select a valid directory and the .csv file to be overwritten is closed.')
            return

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

    def isValidEntry(self, text):

        if('str' in str(type(text)) and text != '' and text != 'None' and text != 'none' and text != 'NULL' and text != 'null'):
            return 'True'
        else: 
            return 'False'

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
    UIWidget = skureviewui()
    UIWidget.openform(QWidget(),'Demo','ReadWrite')
    app.exec_()
    sys.exit(app.exec_())
'''  

