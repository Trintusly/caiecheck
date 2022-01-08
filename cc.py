import requests
import time
import pandas as pd

start = time.time()

# Grades that are acceptable to you
acceptableGrades = [
    "A*", "A"
]

# Replace this with your login info
loginInfo = {
    "username": "i*******410",
    "password": "lM****urEX"
}

def listToArray(table):
    exams = []
    eC = 0
    for e in table['Examination']:
        # Skip the last table row
        # It has nothing to do with results
        if e != "The results displayed are  provisional, and for information only":
            eC += 1
            exams.append({ "id": eC, "exam": e })
    
    grades = []
    gC = 0
    for g in table["Grade Awarded"]:
        gC += 1
        grades.append({ "id": gC, "grade": g })
    
    final = []
    for exam in exams:
        for grade in grades:
            if exam["id"] == grade["id"]:
                final.append({ "id": exam["id"], "exam": exam["exam"], "grade": grade["grade"] })

    return final

def getResults():
    r = requests.post(
        "https://myresults.cie.org.uk/cie-candidate-results/j_spring_security_check;jsessionid=414C496BC3D39567B73D65B4A422030D",
        data = {
            "j_username": loginInfo["username"],
            "j_password": loginInfo["password"]
        }
    )

    df_list = pd.read_html(r.text)
    df = df_list[0]

    return df

# Initialize current grades
lastKnownGrades = listToArray(getResults())

def checkResults():
    global lastKnownGrades

    for newData in listToArray(getResults()):
        for oldData in lastKnownGrades:
            if newData['id'] == oldData['id']:
                if newData['grade'] == oldData['grade']:
                    print("Grades same for " + str(newData['exam']))
                else:
                    # Moment of truth, grades have been updated!
                    # Now lets check if they are acceptable...
                    if newData['grade'] in acceptableGrades: 
                        # Congrats! You got your grades!
                        print("Grades updated for " + str(newData['exam']))
                    else:
                        # Grades were not in the range. RIP
                        print("Grades released, " + str(newData['grade']) + " in " + str(newData['exam']))
                    
                    # Update latest grades
                    lastKnownGrades = listToArray(getResults())

while True:
    checkResults()
    time.sleep(3.0 - ((time.time() - start) % 3.0))
