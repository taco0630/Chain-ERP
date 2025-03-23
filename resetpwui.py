from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QDialog, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
#from loginui import loginui
from appui import appui
import req
import requests, json
from datetime import datetime
import time
import sys, os, random, pyotp
import bcrypt
from pandas import json_normalize
import azure.cosmos.cosmos_client as cosmos_client
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
# AES 256 encryption/dpycryptoecryption using  library
import base64, hashlib
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

#encryptkey = os.getenv('ENCRYPTO_KEY')
#uri = os.getenv('URI')
#key = os.getenv('KEY')
# pad with spaces at the end of the text
# beacuse AES needs 16 byte blocks

class resetpwui(QMainWindow):
    
    totpkey = pyotp.random_base32().replace("'","")
    totp = pyotp.TOTP(totpkey, interval=900)
    code = totp.at(int(time.time()))

    apptitle = req.apptitle

    getaccessurl = req.gcp_getaccesslevel_url
    setaccessurl = req.gcp_setpassword_url
    hrdbname = req.azure_hrmanagement_db
    hruri = req.azure_hrmanagement_uri
    hrrkey = req.azure_hrmanagement_readkey
    hrrwkey = req.azure_hrmanagement_readwritekey
    sgkey = req.sendgrid_key2
    supportemail = req.supportemail
    
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
        self.setWindowTitle(resetpwui.apptitle)
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

    def closeEvent(self, event):

        sys.exit()

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
                self.setWindowTitle(resetpwui.apptitle)
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

        client = cosmos_client.CosmosClient(resetpwui.hruri, resetpwui.hrrwkey) 
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
                    self.openZHTWWindow()
                elif 'ZHCN' in self.label_lang.text():
                    self.createDialog('密码已重设，请重新登入')
                    self.openZHCNWindow
                else: 
                    self.createDialog('Password is reset. Please log in again.')
                    self.openEngWindow

                self.setWindowIcon(QIcon('logo.ico'))
                self.setWindowTitle(resetpwui.apptitle)
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
        self.setWindowTitle(resetpwui.apptitle)
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
        self.setWindowTitle(resetpwui.apptitle)
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
        self.setWindowTitle(resetpwui.apptitle)
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
                            from_email=resetpwui.supportemail,
                            to_emails=resetpwui.supportemail,
                            subject='Take action. User: '+username,
                            html_content='User '+msg+ ' had too many attempts.\n\nPlease lock this account'
                            )
                            sg = SendGridAPIClient(resetpwui.sgkey)
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
       
    def getEmailfromDBAndSendEmail(self):
        
        body = ''
        username = str(self.textEdit_username.toPlainText())
        msg = str(self.code)

        client = cosmos_client.CosmosClient(resetpwui.hruri, resetpwui.hrrkey) 
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
                from_email= resetpwui.supportemail,
                to_emails=email,
                subject='您的chain驗證碼',
                html_content='您的驗證碼為'+ msg +'。\n\n請在15分鐘內輸入驗證碼'
                )
                try:
                    sg = SendGridAPIClient(resetpwui.sgkey)
                    response = sg.send(message)
                    self.createDialog('請確認您的電子郵件。您的驗證碼將在15分鐘後失效')
                except Exception as e:
                    self.createDialog('狀態500: 請聯絡IT團隊')

        elif('Email' in body and 'ZHCN' in self.label_lang.text()):
            email = ((body.split(',')[13]).split(':')[1]).replace("\"","")
            if(email != None and email != '' and msg != ''):
                msg = '<strong>'+str(msg)+'</strong>'
                message = Mail(
                from_email= resetpwui.supportemail,
                to_emails=email,
                subject='您的chain验证码',
                html_content='您的验证码为'+ msg +'。\n\n请在15分钟内输入验证码'
                )
                try:
                    sg = SendGridAPIClient(resetpwui.sgkey)
                    response = sg.send(message)
                    self.createDialog('请确认您的电子邮件。您的验证码将在15分钟后失效')
                except Exception as e:
                    self.createDialog('状态500: 请联络IT团队')

        elif('Email' in body):
            email = ((body.split(',')[13]).split(':')[1]).replace("\"","")
            if(email != None and email != '' and msg != ''):
                msg = '<strong>'+str(msg)+'</strong>'
                message = Mail(
                from_email= resetpwui.supportemail,
                to_emails=email,
                subject='Your security code is delivered.',
                html_content='Your security code is '+ msg +'.\n\nPlease enter your code within 15 min.'
                )
                try:
                    sg = SendGridAPIClient(resetpwui.sgkey)
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

        client = cosmos_client.CosmosClient(resetpwui.hruri, resetpwui.hrrkey) 
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
        """
        for cr in database.list_containers():
                    
                if('staff' in cr['id']):

                    container = database.get_container_client(cr['id'])
                    body = container.read_item(username,username)['body']
                    jsondisplay = json.loads(body)
                    df = json_normalize(jsondisplay)
                    break
        """

        df = pd.read_json(data,orient='index')
        df = df.transpose()
        print(df)
        if add == 1:
            df.at[0,'ErrorCount'] = int(df.at[0,'ErrorCount'])+add
            print(str(int(df['ErrorCount'])))
            print(str(add))
        else:
            df.at[0,'ErrorCount'] = 0
        
        body = df.iloc[0].to_json(orient='columns')
        print(body)

        try:
      
            if (username != '' and username != 'Demo' and container != None and container != '' and container != 'null' and container != 'NULL'):

                key = username
                container.upsert_item({'id': key, 'body':body})    
                print(key)
                print(body)

        except Exception as e:
            print(e)            
    
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
        