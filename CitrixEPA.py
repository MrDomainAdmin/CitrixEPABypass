import base64
import hashlib
import re
import time
from Crypto.Cipher import AES # pycryptodome -- untested with pycrypto/pycryptodomex
from Crypto.Util.Padding import pad, unpad
from datetime import datetime
import requests
import sys

if len(sys.argv) < 2:
    print("Please provide domain as a variable")
    print("Ex: python CitrixEPA.py citrix.example.com")
    sys.exit(1)

baseHOST = sys.argv[1]
NSC_EPAC = ""
hex_cookie = ""
big_data_energy = ""
epoch = ""
# First Request

headers = {
    "Host": baseHOST,
    "Content-Length": "0",
    "Content-Type": "text/html; charset=UTF-8",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "X-Citrix-Am-Labeltypes": "none, plain, heading, information, warning, error, confirmation, image, nsg-epa, nsg-epa-v2, nsg-epa-failure, nsg-login-label, tlogin-failure-msg, nsg-tlogin-heading, nsg-tlogin-single-res, nsg-tlogin-multi-res, nsg-tlogin, nsg-login-heading, nsg-fullvpn, nsg-l20n, nsg-l20n-error, certauth-failure-msg, dialogue-label, nsg-change-pass-assistive-text, nsg_confirmation, nsg_kba_registration_heading, nsg_email_registration_heading, nsg_kba_validation_question, nsg_sspr_success, nf-manage-otp",
    "Sec-Ch-Ua-Mobile": "?0",
    "X-Citrix-Isusinghttps": "Yes",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "X-Citrix-Am-Credentialtypes": "none, username, domain, password, newpassword, passcode, savecredentials, textcredential, webview, nsg-epa, nsg-epa-v2, nsg-x1, nsg-setclient, nsg-eula, nsg-tlogin, nsg-fullvpn, nsg-hidden, nsg-auth-failure, nsg-auth-success, nsg-epa-success, nsg-l20n, GoBack, nf-recaptcha, ns-dialogue, nf-gw-test, nf-poll, nsg_qrcode, nsg_manageotp, negotiate, nsg_push, nsg_push_otp, nf_sspr_rem",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Origin": f"https://{baseHOST}",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

# Make the POST request
response = requests.post(f'https://{baseHOST}/p/u/getAuthenticationRequirements.do', headers=headers)

# Check the response status code
if response.status_code == 200:
    response_str = str(response.headers)
    pattern = r'NSC_EPAC=([^;]+)'
    match = re.search(pattern, response_str)
    NSC_EPAC = match.group(1)
    print(f"Got cookie {NSC_EPAC}")

else:
    print(f"POST request failed with status code: {response.status_code}")

# Second and Third Request
epoch = str(int(time.time()))
headers = {
    "X-Citrix-NG-Capabilities": "extcookie",
    "Content-Type": "text/html; charset=UTF-8",
    "Cookie": f"NSC_EPAC={NSC_EPAC}",  # Replace {{cookie}} with your desired NSC_EPAC value
    "Date": epoch,  # Get the current epoch time as a rounded whole number
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; AGEE 8.0;) NAC/1.0 plugin 23.8.1.11",
    "Cache-Control": "no-cache",
    "Connection": "close",
}


requests.get(f'https://{baseHOST}/epatype', headers=headers)
response = requests.get(f'https://{baseHOST}/epaq', headers=headers)
big_data_energy = response.headers.get("CSEC")
print(f"Received encrypted data")
cookie = NSC_EPAC[:32]
hexcookie =bytes.fromhex(cookie)



keydata = b"NSC_EPAC=" + cookie.encode('utf-8') + b"\r\n" + epoch.encode('utf-8') + b"\r\n" + baseHOST.encode('utf-8') + b"\r\n" + hexcookie
print("Building key")
hashkey = hashlib.sha1(keydata).hexdigest()
key = bytes.fromhex(hashkey)
key=key[:16]


def decrypt(encrypted,key,iv): 

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decryptedtext = cipher.decrypt(base64.b64decode(encrypted))   # Base64 decode the ciphertext
    decryptedtextP = decryptedtext.rstrip(b'\0').decode('utf-8', errors='replace')  # remove the Zero padding
    return decryptedtextP.strip()
print("Decrypting...")
data = decrypt(big_data_energy, key, hexcookie)
split_data = data.split(";")
for item in split_data:
    print(item)
