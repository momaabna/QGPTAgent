# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGPTAgentDockWidget
                                 A QGIS plugin
 QGPT Agent is LLM Assistant that uses openai GPT model to automate QGIS processes
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-04-27
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Mohammed Nasser
        email                : mohammed.nasser@uofk.edu
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

import os
import subprocess
import sys
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
import requests
import subprocess
import io
import contextlib
import platform
import traceback
import qgis.utils
import tempfile
from qgis.utils import *
from PyQt5.QtCore import QThread, pyqtSignal

version =qgis.utils.Qgis.QGIS_VERSION 
from qgis.PyQt.QtCore import QThreadPool
from qgis.PyQt.QtWidgets import QLabel
from .prompts import *

def containerize_code(code_string):
    code_string ="""from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
""" +code_string
    # From Engshell
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            exec(code_string, globals())
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb = traceback.extract_tb(exc_traceback)
        filename, line, func, text = tb[-1]
        error_msg = f"{exc_type.__name__}: {str(e)}"
        return False, f'Error: {error_msg}. Getting the error from function: {func} (line: {line})'
    code_printout = output_buffer.getvalue()
    return True, code_printout
def get_completion(prompt,api_key,temprature=0.0):

    # Replace MODEL_ID with the ID of the OpenAI model you want to use
    model_id = 'text-davinci-003'
    max_tockens = 1000

    # Define the parameters for the API request
    data = {
        'model': model_id,
        'prompt': prompt,
        "max_tokens": max_tockens,
        "temperature": temprature,
        }

    # Define the headers for the API request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    # Send the API request and get the response
    response = requests.post('https://api.openai.com/v1/completions', json=data, headers=headers)
    #print(response)

    # Parse the response to get the text completion
    completion = response.json()['choices'][0]['text']

    return completion


class RequestWorker(QThread):
    # Define a custom signal to emit when the request is finished
    finished_signal = pyqtSignal(str)
    
    def __init__(self, prompt,api_key,temprature=0.0):
        super().__init__()
        self.prompt=prompt
        self.api_key =api_key
        self.temprature=temprature
    
    def run(self):
        completion =get_completion(self.prompt, self.api_key,self.temprature)
        self.finished_signal.emit(completion)







FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgpt_agent_dockwidget_base.ui'))


class QGPTAgentDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(QGPTAgentDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.agentName ='QGPT Agent'
        self.chat_text ='QGPT Agent  in Your Service  '
        self.mode =self.agentRadio.isChecked()
        try:
            self.apiTocken = os.environ['QGPT_AGENT_OPEN_AI_TOCKEN']
            self.tockenEdit.setText(self.apiTocken)
        except:
            os.environ['QGPT_AGENT_OPEN_AI_TOCKEN']=''
            self.apiTocken = os.environ['QGPT_AGENT_OPEN_AI_TOCKEN']
        try:

            self.userName =os.environ['QGPT_AGENT_USER']
            self.self.userEdit.setText(self.userName)
        except:
            os.environ['QGPT_AGENT_USER']=os.getlogin()
            self.userName =os.environ['QGPT_AGENT_USER']
            self.userEdit.setText(self.userName)


        self.setTockenButton.clicked.connect(self.set_tocken)
        self.setUserButton.clicked.connect(self.set_user)
        self.agentRadio.clicked.connect(self.check_mode)
        self.chatRadio.clicked.connect(self.check_mode)
        self.sendButton.clicked.connect(self.send)
        self.msgEdit.returnPressed.connect(self.send)
        self.update_chat()
        

    def install_library(self):
        try:
            print('Start installing OpenAI Library ...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'openai'])
            print('installed Successfully.')
        except subprocess.CalledProcessError:
            print("Installation failed.")
    
    def update_chat(self):
        self.chatEdit.setText(self.chat_text)
        self.chatEdit.verticalScrollBar().setValue(self.chatEdit.verticalScrollBar().maximum())
    def send(self):
        #check if there is text 
        # 
        if self.msgEdit.text() =='':
            return
        self.chat_text =self.chat_text+'\n'+self.userName +' : ' +self.msgEdit.text()
        if self.mode:
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Processing Your Order ...'
            self.update_chat()
            prompt = make_prompt(self.msgEdit.text())
            #print(prompt)
            #completion = get_completion()
            self.worker = RequestWorker(prompt, self.apiTocken)
            self.worker.finished_signal.connect(self.run_code)

            # Add the worker to a QThreadPool and start it
            self.worker.run()
            """ self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Compiling Code.'
            code = completion.split('[[[')[1].split(']]]')[0]
            if self.seeCodeCheckBox.isChecked():
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Code :\n'+code
                self.update_chat()

            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Running Code.'
            st,msg=containerize_code(code)
            if st:
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Done.'
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
            else:
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Found some prblems while execution.'
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
                # Correcting code to start and run it again
                prompt = make_debug_prompt(code,msg)
                #print(prompt)
                completion = get_completion(prompt, self.apiTocken)
                msg =completion.split('[[[')[1].split(']]]')[0]
                code = completion.split('[[[')[2].split(']]]')[0]
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Compiling New Code.'
                if self.seeCodeCheckBox.isChecked():
                    self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Edited Code :\n'+code
                    self.update_chat()
                self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Running Code.'
                st,msg=containerize_code(code)
                if st:
                    self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Done.'
                    self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
                else:
                    self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Found some prblems while execution.'
                    self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
            self.update_chat() """

        else:
            self.chat_text =self.chat_text+'\n'+self.agentName +' : '+self.msgEdit.text()
            prompt = make_chat_prompt(self.msgEdit.text())
            #completion = get_completion(prompt, self.apiTocken)
            worker = RequestWorker(prompt, self.apiTocken)
            worker.finished_signal.connect(self.run_chat)

            # Add the worker to a QThreadPool and start it
            worker.run()
            #self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +completion

        self.msgEdit.setText('')
        self.update_chat()
    def run_chat(self,completion):
        self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +completion
    def run_code(self,completion):
        self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Compiling Code.'
        code = completion.split('[[[')[1].split(']]]')[0]
        if self.seeCodeCheckBox.isChecked():
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Code :\n'+code
            self.update_chat()

        self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Running Code.'
        st,msg=containerize_code(code)
        if st:
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Done.'
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
        else:
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Found some prblems while execution.'
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
            # Correcting code to start and run it again
            prompt = make_debug_prompt(code,msg)
                #print(prompt)
            #completion = get_completion(prompt, self.apiTocken)
            self.worker = RequestWorker(prompt, self.apiTocken)
            self.worker.finished_signal.connect(self.debug_code)

            # Add the worker to a QThreadPool and start it
            
            self.worker.run()
            
    
    def debug_code(self,completion):
        msg =completion.split('[[[')[1].split(']]]')[0]
        code = completion.split('[[[')[2].split(']]]')[0]
        self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Compiling New Code.'
        if self.seeCodeCheckBox.isChecked():
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Edited Code :\n'+code
            self.update_chat()
        self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Running Code.'
        st,msg=containerize_code(code)
        if st:
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Done.'
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
        else:
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Found some prblems while execution.'
            self.chat_text =self.chat_text+'\n'+self.agentName +' : ' +'Output by system :\n'+msg
        self.update_chat()

    def check_mode(self):
        self.mode =self.agentRadio.isChecked()
        #print((self.mode))

    def set_tocken(self):
        os.environ['QGPT_AGENT_OPEN_AI_TOCKEN'] =self.tockenEdit.text()
        self.apiTocken = os.environ['QGPT_AGENT_OPEN_AI_TOCKEN']
        #print(os.environ['QGPT_AGENT_OPEN_AI_TOCKEN'])
    def set_user(self):
        os.environ['QGPT_AGENT_USER'] =self.userEdit.text()

        self.userName =os.environ['QGPT_AGENT_USER']
        #print(os.environ['QGPT_AGENT_USER'])


        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
