# using neuftech RFID card reader
# card reader provides keyboard input: {ID num} followed by {ENTER}

from pynput import keyboard
import threading
import csv
import os, time, datetime
import win32gui

# clear console
clear = lambda: os.system('cls') # on Windows System
clear()

# open files
year = int(datetime.datetime.fromtimestamp(time.time()).strftime('%Y'))
month = int(datetime.datetime.fromtimestamp(time.time()).strftime('%m'))
day = int(datetime.datetime.fromtimestamp(time.time()).strftime('%d'))

week = int(datetime.date(year, month, day).isocalendar()[1])

timesheetFilePath = r".\files\timesheets\timesheet_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y') + "-" + str(week) + ".csv"
try:
    log_file = open(timesheetFilePath)
    # open file in append mode
    log_file.close()
    log_file = open(timesheetFilePath,"a+")
except IOError:
    print("create new time tracking file")
    log_file = open(timesheetFilePath, "w+")
    log_file.write("Name,Date,Time,In/Out,Total (hrs)\n")
    log_file.flush()

employeeFilePath = r".\files\employee_data.csv"
try:
    temp_file = open(employeeFilePath)
    # open file in append mode
    temp_file.close()
except IOError:
    print("create new employee data file")
    temp_file = open(employeeFilePath, "w+")
with open(employeeFilePath, newline='') as f:
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
    directory_file = open(employeeFilePath, "w+")
    for j in range(len(directory)):
        directory_file.write("{0},{1},{2},{3}\n".format(directory[j][0],
                                                directory[j][1],
                                                directory[j][2],
                                                directory[j][3]))
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
            time_in = directory[i][3]
            directory[i][3] = time.time() if int(directory[i][2]) == 1 else "out"
    update_employee_data()

    _name = getName(ID)
    _date = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
    _time = datetime.datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")
    _stat = "Clock in" if getStatus(ID) == 1 else "Clock out"
    if _stat == "Clock in":
        _total = ""
    else:
        _total = round((time.time() - float(time_in))/3600,3)
    print("{0} {1} at {2} {3}\n".format(_name,_stat,_time,_date))
    log_file.write("{0},{1},{2},{3},{4}\n".format(_name,_date,_time,_stat,_total))
    log_file.flush()

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
        time.sleep(5)
        clear()
    else:
        _name = input("Name: ")
        directory_file = open(employeeFilePath, "a+")
        directory_file.write("{0},{1},{2},{3}\n".format(newID,_name,0,"out"))
        directory_file.flush()
        directory_file.close()
        print("Script must restart")
        time.sleep(1)
        os._exit(1)

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

def generateTotals():
    with open(timesheetFilePath, newline='') as f:
        reader = csv.reader(f)
        timesheet_data = list(reader)
    with open(employeeFilePath, newline='') as f:
        reader = csv.reader(f)
        employee_data = list(reader)

    num_employees = len(employee_data)

    totalsFilePath = r".\files\timesheets\timesheet_" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y') + "-" + str(week) + "_totals.csv"
    totals_file = open(totalsFilePath, "w+")
    for i in range(num_employees):
        totals_file.write("{0},".format(employee_data[i][1]))
    totals_file.write("\n")

    for i in range(len(timesheet_data)):
        if timesheet_data[i][3] == "Clock out":
            for j in range(num_employees):
                if employee_data[j][1] == timesheet_data[i][0]:
                    totals_file.write("{0}".format(timesheet_data[i][4]))
                else:
                    totals_file.write(" ")
                totals_file.write(",")
            totals_file.write("\n")

    print("Generated {0}".format(totalsFilePath))
    time.sleep(2)
    totals_file.flush()
    clear()

def menu():
    print("\nAdd user\t- /add\nRemove user\t- /remove\nShow users\t- /list\nGenerate totals\t- /totals\nTap in/out\t- hit ENTER\n")
    action = input("Action: ")

    clear()
    if action == "/add":
        add()
    elif action == "/remove":
        remove()
    elif action =="/list":
        showUsers()
    elif action == "/totals":
        generateTotals()
    else:
        main()
    menu()

menu()
