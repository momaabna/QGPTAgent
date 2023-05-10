import requests
import processing
import io
import contextlib
import platform
import traceback
import qgis.utils
import tempfile
import os
import subprocess
import sys
from qgis.PyQt.QtCore import QThreadPool
from PyQt5.QtCore import QThread, pyqtSignal
from qgis.utils import *
import sqlite3
# code containerization
def containerize_code(code_string):
    code_string ="""from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import processing
from qgis.utils import *
import tempfile
""" +code_string +"""# refresh the canvas
iface.mapCanvas().refresh()"""
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

# Get completion from OpenAI API
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
    try:
        # Send the API request and get the response
        response = requests.post('https://api.openai.com/v1/completions', json=data, headers=headers)
        #print(response)
        if response.status_code==200:
            
            # Parse the response to get the text completion
            completion = response.json()['choices'][0]['text']
        else:
            completion ='code_error'
    except:
        completion='connection_error'
    return completion

#Get completion thread
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

# Run code in a thread
class CodeRunner(QThread):
    finished_signal = pyqtSignal(str)
    def __init__(self, code_string):
        super().__init__()
        self.code_string = code_string
    
    def run(self):
        success, code_printout = containerize_code(self.code_string)
        # emit binary success and code printout
        self.finished_signal.emit(str(success) + '|||' + code_printout)

#Sqlite 3 database class
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def close(self):
        self.conn.close()
    def setSettingsValue(self, key, value):
        self.execute('INSERT OR REPLACE INTO settings VALUES ((SELECT id FROM settings WHERE key = ?), ?, ?)', (key, key, value))
        self.conn.commit()
    def getSettingsValue(self, key):
        self.execute('SELECT value FROM settings WHERE key = ?', (key,))
        return self.fetchone()[0]
    def getHistory(self):
        self.execute('SELECT * FROM history')
        return self.fetchall()
    def addHistory(self,command, code, datetime, success, printout):
        #print(command, code, datetime, success, printout)
        #auto increment id is the last id + 1
        self.execute('INSERT INTO history VALUES ((SELECT id FROM history ORDER BY id DESC LIMIT 1)+1, ?, ?, ?, ?, ?)', (command, code, datetime, success, printout))
        self.conn.commit()
    def deleteHistory(self, id):
        self.execute('DELETE FROM history WHERE id = ?', (id,))
        self.conn.commit()
    def deleteAllHistory(self):
        self.execute('DELETE FROM history')
        self.conn.commit()
   
    def createTable(self, table_name, columns):
        self.execute(f'CREATE TABLE {table_name} ({columns})')
    
    def createAllTables(self):
        #settings table id,key,value
        self.createTable('settings', 'id INTEGER PRIMARY KEY, key TEXT, value TEXT')
        #history table id,command,code,datetime,success,printout
        self.createTable('history', 'id INTEGER PRIMARY KEY, command TEXT, code TEXT, datetime TEXT, success TEXT, printout TEXT')
        #commit changes
        self.conn.commit()
