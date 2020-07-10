import pyodbc
import os


def connect_database():
    connection_string = os.environ["SQLCONNSTR_python"]
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    return connection, cursor


def close_database(connection):
    connection.commit()
    connection.close()