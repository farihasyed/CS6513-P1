import pyodbc
import os


def connect_database():
    connection_string = os.environ["SQLAZURECONNSTR_python"]
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    return connection, cursor

execute_database(self, command):
        self.cursor.execute(command)

def close_database(self):
        self.connection.commit()
        self.connection.close()