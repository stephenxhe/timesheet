# using neuftech RFID card reader
# card reader provides keyboard input: {ID num} followed by {ENTER}

from pynput import keyboard
import threading
import csv
import os, time, datetime
import win32gui

# open files
file_name = r".\files\timesheet_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m') + ".csv"
try:
    log_file = open(file_name)
    # open file in append mode
    log_file.close()
    log_file = open(file_name,"a+")
except IOError:
    print("create new time tracking file")
    log_file = open(file_name, "w+")
    log_file.write("Name,Date,Time,In/Out\n")
    log_file.flush()

file_name = r".\files\employee_data.csv"
with open(file_name, newline='') as f:
    reader = csv.reader(f)
    directory = list(reader)
    # print("read data")
    # print(directory)

# esc detection thread
thisWindow = win32gui.GetForegroundWindow()
def on_press(key):
    pass

def on_release(key):
    focusWindow = win32gui.GetForegroundWindow()
    if thisWindow == focusWindow:
        if str(key) == 'Key.esc':
            log_file.flush()
            print('Exiting...')
            os._exit(1)

def sleeper():
    global escapePressed
    escapePressed = False
    with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
        escapePressed = True
        listener.join()

esc_detect = threading.Thread(target = sleeper, name = 'esc_detection_thread')
esc_detect.start()

# employee data management
def update_employee_data():
    directory_file = open(file_name, "w+")
    for j in range(len(directory)):
        directory_file.write("{0},{1},{2}\n".format(directory[j][0],
                                                directory[j][1],
                                                directory[j][2]))
    directory_file.flush()
    directory_file.close()

def getName(ID):
    for i in range(len(directory)):
        if directory[i][0] == ID:
            return directory[i][1]

def getStatus(ID):
    for i in range(len(directory)):
        if directory[i][0] == ID:
            return int(directory[i][2])

def findID(ID):
    out = False
    for i in range(len(directory)):
        if directory[i][0] == ID:
            out = True
    return out

def tap(ID):
    for i in range(len(directory)):
        if directory[i][0] == ID:
            directory[i][2] = 0 if int(directory[i][2]) == 1 else 1
    update_employee_data()

    _name = getName(ID)
    _date = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
    _time = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")
    _stat = "Clock in" if getStatus(ID) == 1 else "Clock out"
    print("{0} {1}\n".format(_name,_stat))
    log_file.write("{0},{1},{2},{3}\n".format(_name,_date,_time,_stat))
    log_file.flush()

# clear console
clear = lambda: os.system('cls') #on Windows System

# modes
def main():
    clear()
    print("Reading ...")
    while True:
        focusWindow = win32gui.GetForegroundWindow()
        if thisWindow == focusWindow:
            input1 = input()
            # print(getName(input1),end='')
            # print(getStatus(input1))
            if findID(input1):
                tap(input1)

def add():
    print("Add user ...")
    newID = input("Scan ID card: ")
    if findID(newID):
        print("Already registered to: {0}".format(getName(newID)))
    else:
        _name = input("Name: ")
        directory_file = open(file_name, "a+")
        directory_file.write("{0},{1},{2}\n".format(newID,_name,0))
    time.sleep(5)
    clear()

def remove():
    remID = input("Scan card: ")
    if findID(remID):
        print("Implement this later")
    else:
        print("No user with that ID")
    input("\nPress any key to continue ...")
    clear()

def showUsers():
    print("ID\t\tName\n")
    for i in range(len(directory)):
        _ID = directory[i][0]
        _name = directory[i][1]
        print("{0}\t{1}".format(_ID,_name))
    input("\nPress any key to continue ...")
    clear()

def menu():
    print("\nAdd user\t- /add\nRemove user\t- /remove\nShow users\t- /list\nTap in/out\t- hit ENTER\n")
    action = input("Action: ")

    clear()
    if action == "/add":
        add()
    elif action == "/remove":
        remove()
    elif action =="/list":
        showUsers()
    else:
        main()
    menu()
menu()
