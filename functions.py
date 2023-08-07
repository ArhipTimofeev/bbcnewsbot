import pymysql
import datetime
from datetime import date
import json
def registerNewProfile(conn, username, EMail, password, telegramuserid):

        cur = conn.cursor()
        cur.execute(f"INSERT INTO `Users` (UserName, Password, EMail, Inventory, DataRegistration, StartSession, EndSession, LogInUser) VALUES ('{username}', '{password}', '{EMail}', '{{}}', '{datetime.datetime.now()}', '{datetime.datetime.now()}', '{datetime.datetime.now() + datetime.timedelta(days=7)}', {telegramuserid})")
        conn.commit()
        return True

def loginInProfile(conn, username, password, telegramuserid):
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `Users` WHERE `UserName` = '{username}'")
        result = cur.fetchone()
        if result != None and result['UserName'] == username and result['Password'] == password:
            cur.execute(f"UPDATE `Users` SET StartSession = '{datetime.datetime.now()}'")
            cur.execute(f"UPDATE `Users` SET EndSession = '{datetime.datetime.now() + datetime.timedelta(days=7)}'")
            cur.execute(f"UPDATE `Users` SET LogInUser = '{telegramuserid}'")
            conn.commit()
            return True
        else:
            return "Unknow user"

def GetAllInformation(conn, username):
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `Users` WHERE `UserName` = '{username}'")
        result = cur.fetchone()
        if result != None:
            return result
        else:
            return None

def GetAllInformationByID(conn, id):
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM `Users` WHERE `LogInUser` = '{id}'")
        result = cur.fetchone()
        if result != None:
            return result
        else:
            return None

def checkSession(conn, telegramuserid):
            cur = conn.cursor()
            cur.execute(f"SELECT `EndSession` FROM `Users` WHERE `LogInUser` = '{telegramuserid}'")
            result = cur.fetchone()
            if result != None:
                if result['EndSession'].date() <= date.today():
                    cur.execute(f"UPDATE `Users` SET LogInUser = Null")
                    conn.commit()
                    return "Session Ends"
                else:
                    return True
            elif result == None:
                return "LogIn required"
            
def banUser(conn, UserID):
    cur = conn.cursor()
    cur.execute(f"SELECT `ID` FROM `Users` WHERE `ID` = '{UserID}'")
    result = cur.fetchone()
    if(result != None):
        cur.execute(f"SELECT `LogInUser` FROM `Users` WHERE `ID` = '{UserID}'")
        result = cur.fetchone()['LogInUser']
        cur = conn.cursor()
        cur.execute(f"UPDATE `Users` SET `Status` = '⛔️ Заблокирован' WHERE `ID` = '{UserID}'")
        conn.commit()
        return result
    else:
         return False
    
def unbanUser(conn, UserID):
    cur = conn.cursor()
    cur.execute(f"SELECT `ID` FROM `Users` WHERE `ID` = '{UserID}'")
    result = cur.fetchone()
    if(result != None):
        cur.execute(f"SELECT `LogInUser` FROM `Users` WHERE `ID` = '{UserID}'")
        result = cur.fetchone()['LogInUser']
        cur = conn.cursor()
        cur.execute(f"UPDATE `Users` SET `Status` = 'Игрок' WHERE `ID` = '{UserID}'")
        conn.commit()
        return result
    else:
         return False