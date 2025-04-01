import sqlite3
import uuid

class SQLConnection:
    dbname= 'RAGchunkstore.db'
    tablename='chunks'
    contentColumn='content'
    idColumn='id'

    def __init__(self):        
        with sqlite3.connect(self.dbname) as connection:
            cursor = connection.cursor()
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename}({self.contentColumn} TEXT)')
            connection.commit()
    def addText(self,text):        
        text=self.removeQuotes(text)
        with sqlite3.connect(self.dbname) as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO {self.tablename} VALUES (\'{text}\')')
            connection.commit()
            return cursor.lastrowid
        return -1
    def getText(self,id):        
        with sqlite3.connect(self.dbname) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT {self.contentColumn} FROM {self.tablename} WHERE rowid={id}')
            result=cursor.fetchone()
            if(len(result)>0):
                return self.addQuotes(result[0])
        return ""
    
    def removeQuotes(self,text):
        return text.replace('\'','\'\'')
    def addQuotes(self,text):
        return text.replace('\'\'','\'')