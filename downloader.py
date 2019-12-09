import imaplib, email, os
import datetime
# user = 'your_email'
# password = 'your_password'
# imap_url = 'imap.gmail.com'
#Where you want your attachments to be saved (ensure this directory exists) 
attachment_dir = '/Users/shovon/Scripts/Uber-Receipts/receipts'
# sets up the auth
def auth(user,password,imap_url):
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user,password)
    return con
# extracts the body from the email
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None,True)


def save_email(num, subject, body):
    with open("receipts/" + str(num.decode('utf-8')) + ".txt", "w") as f:
        f.write(subject)
        f.write("\n\n")
        f.write(body)

# allows you to download attachments
def get_attachments(msg, con):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()

        if bool(fileName):
            filePath = os.path.join(attachment_dir, fileName)
            with open(filePath,'wb') as f:
                f.write(part.get_payload(decode=True))
#search for a particular email
def search(key,value,con):
    result, data  = con.search(None,key,'"{}"'.format(value))
    return data


def extract_body(payload):
    """
    returns the email body from the payload
    """
    if isinstance(payload, str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])


def get_emails(conn):
    count = 0
    data = search('FROM', 'Uber Receipts', conn)
    try:
        for num in reversed(data[0].split()):
            print(count)
            try:
                _, msg_data = conn.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1].decode("utf-8"))
                        subject = msg['subject']
                        payload = msg.get_payload()
                        body = extract_body(payload)
                        save_email(num, subject, body)
                        count += 1
                        print(count, "Messages saved")
                        if count > 60:
                            break
            except Exception as e:
                print("Couldnt Parse message:", num, e)
                pass
    except Exception as e:
        print("EXCEPTION OCCURED:", e)
        pass
        conn.logout()
    finally:
            conn.close()
# con = auth(user,password,imap_url)
# con.select('INBOX')

# result, data = con.fetch(b'10','(RFC822)')
# raw = email.message_from_bytes(data[0][1])
# get_attachments(raw)

def get_last_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    return lastMonth.strftime("%m %Y")

def main():
    user = raw_input("Your email id: ")
    password = raw_input("Your password: ")

    imap_url = 'imap.gmail.com'
    con = auth(user, password, imap_url)
    con.select('INBOX')
    get_emails(con)


if __name__ == '__main__':
    main()