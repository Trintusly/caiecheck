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
    "username": "ij******410",
    "password": "lM*****X"
}

# Meta data
# Check interval, private keys, webhooks, etc...
metaData = {
    "interval": 30.0,
    "discord": "https://discord.com/api/webhooks/929375****30981888/3f5F*******lT77uft_rUQ"
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
                    if newData['grade'] == "Results to be released":
                        # Grades are unreleased
                        print("Grades unreleased for " + str(newData['exam']))

                        requests.post(metaData["discord"], json = {
                            "embeds": [
                                {
                                    "description" : "Checked results. Results unreleased. Trying again in " + str(metaData["interval"]) +  " seconds.",
                                    "title" : str(newData['exam']),
                                    "footer": {
                                      "text": str(pd.to_datetime('today'))
                                    }
                                }
                            ]
                        })
                else:
                    # Moment of truth, grades have been updated!
                    # Now lets check if they are acceptable...
                    if newData['grade'] in acceptableGrades: 
                        # Congrats! You got your grades!
                        print("Grades updated for " + str(newData['exam']))

                        requests.post(metaData["discord"], json = {
                            "content": "@everyone Congrats!!!",
                            "embeds": [
                                {
                                    "description" : str(newData['grade']),
                                    "title" : str(newData['exam']),
                                    "footer": {
                                      "text": str(pd.to_datetime('today'))
                                    }
                                }
                            ]
                        })
                    else:
                        # Grades were not in the range. RIP
                        print("Grades released, " + str(newData['grade']) + " in " + str(newData['exam']))

                        requests.post(metaData["discord"], json = {
                            "content": "@everyone RIP",
                            "embeds": [
                                {
                                    "description" : str(newData['exam']),
                                    "title" : str(newData['grade']),
                                    "footer": {
                                      "text": str(pd.to_datetime('today'))
                                    }
                                }
                            ]
                        })
                    
                    # Update latest grades
                    lastKnownGrades = listToArray(getResults())

    updatedGrades = 0

    for exam in lastKnownGrades:
        if exam['grade'] != "Results to be released":
            updatedGrades += 1
    
    if updatedGrades == len(lastKnownGrades):
        # All grades have been released. Exit script
        requests.post(metaData["discord"], json = {
            "content": "All grades updated. Exiting script."
        })

        quit()

while True:
    checkResults()
    time.sleep(metaData["interval"] - ((time.time() - start) % metaData["interval"]))
