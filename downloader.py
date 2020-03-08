import imaplib, email, os
import datetime
import pdfkit
from bs4 import BeautifulSoup
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
    with open("index.html", 'w') as f:
        f.write(body)
        file_name = str(num.decode('utf-8'))
        pdfkit.from_file('index.html', f'receipts/{num}.pdf')
        # make_html_images_inline("index.html", "receipts/uber.pdf")
    # with open("receipts/" + str(num.decode('utf-8')) + ".pdf", "w") as f:
    #     f.write(subject)
    #     f.write("\n\n")
    #     f.write(body)
def guess_type(filepath):
    """
    Return the mimetype of a file, given it's path.
    This is a wrapper around two alternative methods - Unix 'file'-style
    magic which guesses the type based on file content (if available),
    and simple guessing based on the file extension (eg .jpg).
    :param filepath: Path to the file.
    :type filepath: str
    :return: Mimetype string.
    :rtype: str
    """
    try:
        import magic  # python-magic
        return magic.from_file(filepath, mime=True)
    except ImportError:
        import mimetypes
        return mimetypes.guess_type(filepath)[0]

def file_to_base64(filepath):
    """
    Returns the content of a file as a Base64 encoded string.
    :param filepath: Path to the file.
    :type filepath: str
    :return: The file content, Base64 encoded.
    :rtype: str
    """
    import base64
    with open(filepath, 'rb') as f:
        encoded_str = base64.b64encode(f.read())
    return encoded_str
def make_html_images_inline(in_filepath, out_filepath):
    """
    Takes an HTML file and writes a new version with inline Base64 encoded
    images.
    :param in_filepath: Input file path (HTML)
    :type in_filepath: str
    :param out_filepath: Output file path (HTML)
    :type out_filepath: str
    """
    basepath = os.path.split(in_filepath.rstrip(os.path.sep))[0]
    soup = BeautifulSoup(open(in_filepath, 'r'), 'html.parser')
    for img in soup.find_all('img'):
        img_path = os.path.join(basepath, img.attrs['src'])
        mimetype = guess_type(img_path)
        img.attrs['src'] = \
            "data:%s;base64,%s" % (mimetype, file_to_base64(img_path))

    with open(out_filepath, 'w') as of:
        of.write(str(soup))
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

def parse_html(message):
    '''parse a message and return html_content'''
    content = ''
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/html':
                content += part.get_payload(None, True).decode('utf-8')
        html_content = content
    else:
        content = message.get_payload(None, True)
        html_content = content.decode('utf-8')
    return html_content

def get_emails(conn):
    count = 0
    result, data  = conn.search(None, '(SINCE "01-Feb-2020" BEFORE "01-Mar-2020" From "uber.bangladesh@uber.com" Subject "[Business]")')
    # data = search('FROM', 'Uber Receipts', conn)
    try:
        for num in data[0].split():
            try:
                _, msg_data = conn.fetch(num, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1].decode("utf-8"))
                        
                        subject = msg['subject']
                        body = parse_html(msg)
                        # payload = msg.get_payload()
                        # body = extract_body(payload)
                        save_email(num, subject, body)
                        count += 1
                        print(count, "Messages saved")
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
    user = input("Your email id: ")
    password = input("Your password: ")
    imap_url = 'imap.gmail.com'
    con = auth(user, password, imap_url)
    con.select('INBOX')
    get_emails(con)


if __name__ == '__main__':
    main()