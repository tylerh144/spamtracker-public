import os, re

class EmailData:
    def __init__(self, sender_name, sender_email, date, subject, body):
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.date = date
        self.subject = subject
        self.body = body
        self.risk = 0
        self.spam = False

    def __str__(self):
        return f"Risk: {self.risk}\nSender: {self.sender_name}\nEmail: {self.sender_email}\nDate: {self.date}\nSubject: {self.subject}\nContents:\n{self.body}\n\n"

#color stuff
RED = '\033[91m'
MAGENTA = '\033[95m'
GREEN = '\033[32m'
RESET = '\033[0m'


path = os.path.dirname(os.path.abspath(__file__))
print(path)

emails = os.listdir(path + "\\Emails\\")

emailData = []

#collect data
for file in emails:
    eml = open(path + "\\Emails\\" + file)

    curLine = eml.readline()

    while curLine.split(":")[0] != "Date":
        curLine = eml.readline()
    
    date = curLine.split(": ")[1].rstrip()
  

    # DATE and FROM are ordered differently sometimes, return to start
    eml.seek(0)

    while curLine.split(":")[0] != "Subject":
        curLine = eml.readline()
    
    subject = curLine[curLine.index(":")+2:].rstrip()



    eml.seek(0)

    while curLine.split(":")[0] != "From":
        curLine = eml.readline()

    idx = curLine.index("<")
    name = curLine[6:idx].rstrip()

    sender = curLine[idx+1:len(curLine)-2].rstrip()
    

    #inconsistent position again
    eml.seek(0)
    while curLine.split(":")[0] != "Content-Type":
        curLine = eml.readline()

    body = ""
    bodytype = curLine.split(": ")[1]

    if "multipart" in bodytype:
        if "boundary" in bodytype:
            boundary = curLine[curLine.index("=")+2:len(curLine)-2]
        else:
            #some boundaries are on the next line
            curLine = eml.readline()
            boundary = curLine[curLine.index("=")+2:len(curLine)-2]
        
        #skip past some stuff (skip to open boundary, skip to new line/contents)
        curLine = eml.readline()
        while boundary not in curLine:
            curLine = eml.readline()
        while curLine != "\n":
            curLine = eml.readline()

        curLine = eml.readline()

        while boundary not in curLine:
            body+=curLine
            curLine = eml.readline()
            

    elif "text" in bodytype:
        while curLine != "\n":
            curLine = eml.readline()

        for line in eml:
            body+=line
    else:
        body = "not found"


    #create on object based on the data
    emailData.append(EmailData(name, sender, date, subject, body))

    #print("closed")
    eml.close()



    
#reads spamkeywords, trustedemails, and blockedemails
file = open(path + "\\spamkeywords.txt")
contents = file.read()
file.close()
spamwords = contents.split("\n")

file = open(path + "\\trusted.txt")
contents = file.read()
file.close()
trusted = contents.split("\n")

file = open(path + "\\blocked.txt")
contents = file.read()
file.close()
blocked = contents.split("\n")

for eml in emailData:
    #find spam ratio
    sc = 0
    for word in spamwords:
        matchlist = re.findall(word, eml.body, flags=re.IGNORECASE) + re.findall(word, eml.subject, flags=re.IGNORECASE)
        sc+=len(matchlist)
    
    wc = len(re.findall("\\s", eml.body))

    #ratio of spam keywords to words
    ratio=sc/wc
    #add risk based on spam word ratio
    eml.risk+=ratio*100

    #print(str(sc) + "/" + str(wc) + "=" + str(ratio))

    #check sender email in trusted/blocked
    if eml.sender_email in trusted:
        eml.risk-=50
        eml.sender_email = GREEN + eml.sender_email + RESET

    if eml.sender_email in blocked:
        eml.risk+=50
        eml.sender_email = RED  + eml.sender_email + RESET


    #check hour sent
    hour = int(re.search("\\d+(?=:)",  eml.date).group())
    if hour < 6 or hour > 20:
        eml.risk+=20
        eml.date = RED + eml.date + RESET
    

    #final verdict
    if eml.risk >= 30:
        eml.spam = True
    
    #ALL RISK VALUES ARE SUBJECT TO CHANGE


toOpen = 1
toggle = False

while toOpen != -1:
    print()
    print(MAGENTA + "Emails in " + path + ":" + RESET)
    print()

    for i in range(len(emailData)):
        eml = emailData[i]
        j = str(i+1)
        if eml.spam:
            if toggle:
                print(RED + j + ". " + eml.subject + RESET + " - " + eml.sender_name + " <" + eml.sender_email + ">")
        else:
            print(j + ". " + eml.subject + " - " + eml.sender_name + " <" + eml.sender_email + ">")
    toOpen = int(input("Open email (-1 to exit, 0 to toggle spam): "))
    if (toOpen > 0):
        print()
        print(emailData[toOpen-1])
        input("Return")
    elif (toOpen == 0):
        toggle= not toggle

print("I hope this email finds you well")