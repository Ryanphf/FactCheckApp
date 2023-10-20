import g4f

from youtube_transcript_api import YouTubeTranscriptApi
import threading
from selenium import webdriver
import time
import re
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

chatInput = """You are an unbiased fact checker who is willing to help people.

Your role is to parse through the transcript of youtube videos to find any questionable statements to fact check. Information in the transcript may or may not be reliable; in general, assume everything said in the video is unverifiable.

A claim should be considered "unverifiable" unless you can use your knowledge from before September 2021 to fact-check, without relying on the transcript.

Make sure to use a numbered list of facts to check. You should fact check anywhere from 0-5 statements.

When fact-checking claims, assume the  claims stand on their own. Do not refer to "the video" or "the transcript"

More technically, your job is to parse the transcript I am attaching below and parse it as the input "str" to "initialize" in the following python code:

class claim:
    def __init__(self, info):
        self.str = None
        self.truthValue = None
        self.explanation = None
        strings = info.split(";")
        if len(strings) != 3:
            print("error")
        else:
            self.initialize(strings[0], strings[1], strings[2])

    def initialize(self, str, truthValue, explanation):
        self.str = str
        self.truthValue = truthValue
        self.explanation = explanation


def treatStatements(str):
    arr = str.split("\n")
    claims = []
    print(arr)
    for n in arr:
        claims.append(claim(n))

As such, your output should follow the format:

claim1; truthvalue1; explanation1
claim2; truthvalue2; explanation2
claim3; truthvalue3; explanation3

With no superfluous information. The output needs to follow that exact output so it can function as an input to my code.

I am now attaching the transcript.
 """
chatInput1 = """


Remember to parse key claims from the transcript(not the entire transcript) into the exact format I mentioned: ex:

Something being stated in the transcript is not sufficient to fact-check it.

2+2=4;true;that is the definition of 2+2
Donald Trump is the US president; unverifiable; I do not have access to current information to fact-check this.
Laphonza Butler was nominated as California's senator in 2023; unverifiable; please check a veritable news source to fact-check this.

remember, your output in its entirety will be pasted into my python code. Ensure the code will work with your input. This requires semicolons as delimiters and each claim on a new line.

Do not attempt to use colons, dashes, etcetera, as delimiters. This is of the utmost importance.

"""


def askWeb(question):
    try:
        # Initialize the webdriver
        # Set the path to ChromeDriver
        # Path to your Chrome user profile
        # Replace with your profile path

        # Initialize the Chrome driver with options\
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options)
        driver.get("https://komo.ai")
        print("searching the web...")
        # Refresh the page to apply the cookie
        driver.refresh()  # Navigate to the website

        # Wait for the page to load
        driver.implicitly_wait(10)
        # Find the input field
        input_field = driver.find_element(By.XPATH, '//input[@type="text"]')
        time.sleep(1)

        # Send the question to the input field

        input_field.send_keys(question)

        # Press the return key
        input_field.send_keys(Keys.RETURN)

        # Wait for the response to generate
        # Find all elements with the specified attribute
        # response_elements = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
        # time.sleep(10)
        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: len(driver.find_elements(By.XPATH, '//div[@dir="auto"]')) == 3)
        text = None
        while True:
            # Get the old text
            try:
                response_elements = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
                text = [element.text for element in response_elements]
            except:
                continue
            # Wait 1 second
            time.sleep(1)

            # Get the new text
            try:
                response_elements = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
                textNew = [element.text for element in response_elements]
            except:
                continue
            if text == textNew and text is not None:
                break

        # Close the webdriver

        return text[2]
    except:
        return askWeb(question)


def call(question):
    r = None
    while True:
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                stream=True
            )
            responses = []
            for m in response:
                responses.append(m)
            r = "".join(responses)
            #print(r)

            if r.find(';') and r.find('1'):
                break
            print("bad output")
        except:
            pass
    return r


def getTranscript(url):
    video_id = url.split('v=')[1]
    # print(video_id)
    captions = YouTubeTranscriptApi.get_transcript(video_id)
    list = []
    for entry in captions:
        list.append(entry['text'])
    return " ".join(list)


def getClaims(url):
    transcript = getTranscript(url)
    #print("")
    statements = call(chatInput + transcript+ chatInput1)
    #print(statements)
    statements = treatStatements(statements)
    return statements


"""question = input("Ask a statement to fact check: ")
a = call("Fact check the following statement: "+question)
print(a)

link = input("enter a youtube url to extract transcript from")
print(getTranscript(link))
"""


class claim:
    def __init__(self, info):
        #print("INFO: "+info)
        self.str = None
        self.truthValue = None
        self.explanation = None
        strings = info.split(";")
        #print(strings)
        if len(strings) > 3:
            print("error")
        while len(strings) < 3:
            strings.append("")
        else:
            self.initialize(strings[0], strings[1], strings[2])

    def initialize(self, str, truthValue, explanation):
        self.str = str
        self.truthValue = truthValue
        if len(self.truthValue)>15:
            self.truthValue = "unverifiable"
        self.explanation = explanation
    def isVerified(self):
        if len(self.truthValue)<3 or len(self.truthValue)>15 or "un" in self.truthValue:
            return False
        return True
    def __str__(self):
        return "Claim: "+self.str+"\nFact-check: "+self.truthValue+"\nExplanation: "+self.explanation


def treatStatements(str):
    arr = str.split("\n")
    filtered_arr = [line for line in arr if line.strip() and line[0].isdigit()]
    claims = []
    for n in filtered_arr:
        claims.append(claim(n[2:]))
    return claims

def verifyClaims(claims):
    threads = []
    for claim in claims:

        if not claim.isVerified():
            t = threading.Thread(target=verifyClaim, args=(claim,))
            t.start()
            # print(claim)
            threads.append(t)
    for t in threads:
        t.join()
    return claims

def verifyClaim(claim):
    initial = "You are a fact-checker. Your job is to fact-check statements and print out results with the following format: The first line of your response should be a truth-value (eg 'true', 'false', 'mostly true', 'misleading', etcetera). The rest of your response should be a brief explanation as to how you got your answer. Here is the claim to fact-check:"
    response = askWeb(initial+claim.str)
    # parse responses
    response = re.sub(r'\[\d+\]', '', response)

    value, explain = response.split('\n', 1) if '\n' in response else (response, "")
    claim.truthValue = value
    claim.explanation = explain

#print(getTranscript("https://www.youtube.com/watch?v=N4xS40PWhFg"))
claims = getClaims("https://www.youtube.com/watch?v=N4xS40PWhFg")
verifyClaims(claims)
for claim in claims:
    print(claims)