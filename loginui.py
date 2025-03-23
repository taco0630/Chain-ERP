from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QDialog, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from resetpwui import resetpwui
from appui import appui
from datetime import datetime

import requests
import sys
import req
import os, logging, random, json
import bcrypt
import azure.cosmos.cosmos_client as cosmos_client
# AES 256 encryption/decryption using pycrypto library
import base64, hashlib
import pandas as pd
from pandas import json_normalize
import ctypes
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2

class loginui(QMainWindow):

    apptitle = req.apptitle

    hashkey = req.hashkey
    getaccessurl = req.gcp_getaccesslevel_url
    hrdbname = req.azure_hrmanagement_db
    hrcrname = req.azure_hrmanagement_cr
    hruri = req.azure_hrmanagement_uri
    hrrkey = req.azure_hrmanagement_readkey
    hrrwkey = req.azure_hrmanagement_readwritekey
    sgkey = req.sendgrid_key2
    supportemail = req.supportemail
    
    def openloginwindow(self):
        super(loginui, self).__init__()
        self.openEngWindow()

    def openEngWindow(self):
        uic.loadUi("LoginPage_UI.ui",self)
        self.label_lang.setVisible(False)
        self.label_lang.setText('ENG')
        self.setWindowIcon(QIcon('logo.ico'))
        self.setWindowTitle(loginui.apptitle)
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
        self.setWindowTitle(loginui.apptitle)
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
        self.setWindowTitle(loginui.apptitle)
        self.setFixedSize(800,500)
        
        self.lineEdit_pw.setEchoMode(QLineEdit.Password)
        self.show()
        self.pushButton_eng.clicked.connect(self.openEngWindow)
        self.pushButton_zhtw.clicked.connect(self.openZHTWWindow)
        self.pushButton_zhcn.clicked.connect(self.openZHCNWindow)

        self.pushButton_register.clicked.connect(self.openresetpwwindow)
        self.pushButton_submit.clicked.connect(self.click_submit_login)

    def openresetpwwindow(self):
        
        self.window = QMainWindow()
        self.resetpwui = resetpwui()
        self.resetpwui.openresetpwwindow(self.window, self.label_lang.text())
        self.destroy()
    
    def closeEvent(self, event):

        sys.exit()

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
                        self.generatebodyandupdateDB(username, 0)

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

                    elif (int(errorcount) >=4):
                        self.generatebodyandupdateDB(username, 1)
                        try:
                            msg = '<strong>'+username+'</strong>'
                            message = Mail(
                            from_email=loginui.supportemail,
                            to_emails=loginui.supportemail,
                            subject='Take action. User: '+username,
                            html_content='User '+msg+ ' had too many attempts.\n\nPlease lock this account'
                            )
                            sg = SendGridAPIClient(loginui.sgkey)
                            response = sg.send(message)
                        except Exception as e:
                            pass

                        if 'ZHTW' in self.label_lang.text():
                            self.createDialog("狀態202: 密碼錯誤次數過多，請重設密碼")
                        elif 'ZHCN' in self.label_lang.text():
                            self.createDialog("状态202: 密码错误次数过多，请重设密码")
                        else: 
                            self.createDialog("Status 202: Too many unsuccessful attempts. Please reset password.")

                    elif (int(errorcount) >=2):
                        self.generatebodyandupdateDB(username, 1)
                        if 'ZHTW' in self.label_lang.text():
                            self.createDialog("狀態202: 密碼錯誤次數過多，請重設密碼")
                        elif 'ZHCN' in self.label_lang.text():
                            self.createDialog("状态202: 密码错误次数过多，请重设密码")
                        else: 
                            self.createDialog("Status 202: Too many unsuccessful attempts. Please reset password.")
                    
                    else:
                        self.generatebodyandupdateDB(username, 1)
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
                    pass
       
    def callDB(self, username, d):

        client = cosmos_client.CosmosClient(loginui.hruri, loginui.hrrkey) 
        database = client.get_database_client(loginui.hrdbname)
        df = pd.DataFrame()
        body = None
        container = None

        try:

            for cr in database.list_containers():
                    
                if(loginui.hrcrname in cr['id']):

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

    def generatebodyandupdateDB(self, username, add):
        
        client = cosmos_client.CosmosClient(loginui.hruri, loginui.hrrwkey) 
        database = client.get_database_client(loginui.hrdbname)
        
        for cr in database.list_containers():
                    
            if(loginui.hrcrname in cr['id']):

                container = database.get_container_client(cr['id'])
                body = container.read_item(username,username)['body']
                jsondisplay = json.loads(body)
                df = json_normalize(jsondisplay)
                break

        body = container.read_item(username,username)['body']

        df = json_normalize(json.loads(body))
        df.at[0,'ErrorCount'] = str(int(df.at[0,'ErrorCount'])+add)
        body = df.iloc[0].to_json(orient='columns')
        key = username

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
      
    
    
    def createDialog(self, text):

        self.newdialog = dialog(text)
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
    
if __name__ == '__main__': 
    app = QApplication(sys.argv)
    UIWindow = loginui()
    UIWindow.openloginwindow()
    app.exec_()