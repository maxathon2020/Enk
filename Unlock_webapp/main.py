#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os

import webapp3
import jinja2

# from google.appengine.ext import ndb

# class Settings(ndb.Model):
#   name = ndb.StringProperty()
#   value = ndb.StringProperty()

#   @staticmethod
#   def get(name):
#     NOT_SET_VALUE = "NOT SET"
#     retval = Settings.query(Settings.name == name).get()
#     if not retval:
#       retval = Settings()
#       retval.name = name
#       retval.value = NOT_SET_VALUE
#       retval.put()
#     if retval.value == NOT_SET_VALUE:
#       raise Exception(('Setting %s not found in the database. A placeholder ' +
#         'record has been created. Go to the Developers Console for your app ' +
#         'in App Engine, look up the Settings record with name=%s and enter ' +
#         'its value in that record\'s value field.') % (name, name))
#     return retval.value

# AWS_ACCESS_KEY_ID = Settings.get('AWSAccessKeyId')
# AWS_SECRET_ACCESS_KEY = Settings.get('AWSSecretAccessKey')

# import boto3

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

cred = credentials.ApplicationDefault()
# cred = credentials.Certificate("./unlock490firebase-firebase-adminsdk-68d2x-c3d8e0d547.json")
firebase_admin.initialize_app(cred, {
  "projectId": "unlock490firebase",
})

db = firestore.client()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

import re
def valid_username(username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return username and USER_RE.match(username)

def valid_password(password):
        PASS_RE = re.compile(r"^.{8,50}$")
        return password and PASS_RE.match(password) and ("A" in password or "B" in password or "C" in password or "D" in password or "E" in password or "F" in password or "G" in password or "H" in password or "I" in password or "J" in password or "K" in password or "L" in password or "M" in password or "N" in password or "O" in password or "P" in password or "Q" in password or "R" in password or "S" in password or "T" in password or "U" in password or "V" in password or "W" in password or "X" in password or "Y" in password or "Z" in password) and ("1" in password or "2" in password or "3" in password or "4" in password or "5" in password or "6" in password or "7" in password or "8" in password or "9" in password or "0" in password)

def valid_email(email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        return not email or EMAIL_RE.match(email)

import random
import string
import hashlib

def get_random_string(N):
    result_str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
    return result_str

def make_salt():
    return ''.join(random.choice(string.ascii_letters) for x in range(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name.encode('utf-8') + pw.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    ###Your code here
    if make_pw_hash(name, pw, h.split(",")[1]) == h:
        return True

from pywebpush import webpush, WebPushException
from datetime import timezone
import datetime
import time
import math
  
dt = datetime.datetime.now()
utc_time = dt.replace(tzinfo = timezone.utc) 
utc_timestamp = utc_time.timestamp()
 
VAPID_PRIVATE_KEY = open("private_key.txt", "r").readline().strip("\n")
VAPID_PUBLIC_KEY = open("public_key.txt", "r").read().strip("\n")

def push_notification(endpoint, p256dh, auth):
    VAPID_CLAIMS = {
        "aud": '/'.join((endpoint.split('/'))[:3]),  
        "exp": math.floor(utc_timestamp / 1000) + (12 * 60 * 60),
        "sub": "mailto:hello@unlock490.com"
    }
    webpush(
        subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}},
        data=json.dumps({
            "notification": {
            "title": "You have 1 therapy ready for pickup today",
            "body": "Go to the hospital by xx:xx to pick it up",
            "icon": 'images/900x900.svg',
            "vibrate": [100, 50, 100],
            "data": { "primaryKey": 1 },
            "actions": [
                {"action": "explore", "title": "Open pickup page", "icon": "static/img/boxwithpin.svg"},
                {"action": "close", "title": "Close", "icon": "static/img/close.svg"},
            ]
        }}),
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
all_users_ref = db.collection('users').stream()
for user in all_users_ref:
    user_dict = user.to_dict()
    if 'endpoint' in user_dict and 'p256dh' in user_dict and 'auth' in user_dict:
        subscription_info_dict = db.collection('users').document(user.id).get({'endpoint', 'p256dh', 'auth'}).to_dict()
        scheduler.add_job(push_notification, 'interval', args=[subscription_info_dict['endpoint'], subscription_info_dict['p256dh'], subscription_info_dict['auth']], seconds=5)
scheduler.start()

class MainPage(webapp3.RequestHandler):
        def get(self):
            self.response.out.write(jinja_env.get_template('base.html').render())

class SignupHandler(webapp3.RequestHandler):
        def write_form(self, username="", email="", username_error="", password_error="", verify_error="", email_error=""):
                self.response.out.write(jinja_env.get_template('signup.html').render())
                # self.response.out.write(signupform%{"username": username,
                #                                                                                 "email": email,
                #                                                                                 "username_error": username_error,
                #                                                                                 "password_error": password_error,
                #                                                                                 "verify_error": verify_error,
                #                                                                                 "email_error": email_error})
        def get(self):
                self.write_form()
        def post(self, username_error="", password_error="", verify_error=""):
                username = self.request.get("username")
                password = self.request.get("password")
                verify = self.request.get("verify")
                if (valid_username(username) and valid_password(password) and password == verify):
                        #if len(db.Query(User).filter("username =", username).fetch(limit=1))==0:
                        if db.collection('users') and (not db.collection('users').document(username).get().exists or len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) != 2):
                                password = make_pw_hash(username, password)
                                #u = User(username=username, password=password, email=email)
                                #u.put()
                                doc_ref = db.collection('users').document(username)
                                doc_ref.set({
                                    'password': password,
                                    'signup_date': firestore.SERVER_TIMESTAMP
                                })
                                self.response.headers.add_header('Content-Type', 'application/json')
                                result = {
                                    'message': 'Login information gathered successfully.'
                                  }
                                self.response.write(json.dumps(result))
                                return
                        else:
                                username_error = "The provided username has already been registered."
                if not valid_username(username):
                        username_error = "The provided username is not valid."
                if not valid_password(password):
                        password_error = "The provided password is not valid."
                if not password == verify:
                        verify_error = "The passwords don't match."
                self.response.write("<ul style='list-style-type:none;padding:0;'><li>"+username_error+"</li><li>"+password_error+"</li><li>"+verify_error+"</li></ul>")
                self.response.set_status(400, "<ul style='list-style-type:none;padding:0;'><li>"+username_error+"</li><li>"+password_error+"</li><li>"+verify_error+"</li></ul>")

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
class EmailPhoneSignupHandler(webapp3.RequestHandler):
        def write_form(self, username="", email="", username_error="", password_error="", verify_error="", email_error=""):
                self.response.out.write(jinja_env.get_template('emailphonesignup.html').render())
                # self.response.out.write(signupform%{"username": username,
                #                                                                                 "email": email,
                #                                                                                 "username_error": username_error,
                #                                                                                 "password_error": password_error,
                #                                                                                 "verify_error": verify_error,
                #                                                                                 "email_error": email_error})
        def get(self):
                self.write_form()
        def post(self):

            email_verification_code = get_random_string(6)

            sender_email = "unlock490app@gmail.com"
            receiver_email = self.request.get("email")
            f = open("emailpassword.txt", "r")
            email_password = f.read()

            message = MIMEMultipart("alternative")
            message["Subject"] = "Codice di verifica"
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            The email address """+receiver_email+""" has been chosen to be registered on the UNLOCK 4/90 service.
            In order to confirm your email address, use the following code:
            """+email_verification_code+"""
            If it wasn't you to request the registration on UNLOCK 4/90, we kindly ask you to skip this message."""
            html = """\
            <div style="overflow: hidden;">
                <font size="-1">
                    <u></u>
                    <div marginwidth="0" marginheight="0" style="padding:0">
                        <div id="m_-2024486289125691792wrapper" dir="ltr" style="background-color:#ffffff;margin:0;padding:70px 0;width:100%">
                            <font color="#888888">
                            </font>
                            <table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%">
                                <tbody>
                                    <tr>
                                        <td align="center" valign="top">
                                            <div id="m_-2024486289125691792template_header_image">
                                                <p style="margin-top:0">
                                                    <img src="https://unlock490firebase.ew.r.appspot.com/static/img/logo.png" alt="UNLOCK 4/90" style="border:none;display:inline-block;font-size:14px;font-weight:bold;height:auto;outline:none;text-decoration:none;text-transform:capitalize;vertical-align:middle;max-width:100%;margin-left:0;margin-right:0">
                                                </p>
                                            </div>
                                            <font color="#888888">
                                            </font>
                                            <font color="#888888">
                                            </font>
                                            <table border="0" cellpadding="0" cellspacing="0" width="600" id="m_-2024486289125691792template_container" style="background-color:#f7f7f7;border:1px solid #e5e5e5;border-radius:3px">
                                                <tbody>
                                                    <tr>
                                                        <td align="center" valign="top">
                                                            <table border="0" cellpadding="0" cellspacing="0" width="100%" id="m_-2024486289125691792template_header" style="background-color:#0048af;color:#ffffff;border-bottom:0;font-weight:bold;line-height:100%;vertical-align:middle;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;border-radius:3px 3px 0 0">
                                                                <tbody>
                                                                    <tr>
                                                                        <td id="m_-2024486289125691792header_wrapper" style="padding:36px 48px;display:block">
                                                                            <h1 style="font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:30px;font-weight:300;line-height:150%;margin:0;text-align:left;color:#ffffff">Verifica email per UNLOCK 4/90</h1>
                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td align="center" valign="top">
                                                            <font color="#888888">
                                                            </font>
                                                            <table border="0" cellpadding="0" cellspacing="0" width="600" id="m_-2024486289125691792template_body">
                                                                <tbody>
                                                                    <tr>
                                                                        <td valign="top" id="m_-2024486289125691792body_content" style="background-color:#f7f7f7">
                                                                            <font color="#888888">
                                                                            </font>
                                                                            <table border="0" cellpadding="20" cellspacing="0" width="100%">
                                                                                <tbody>
                                                                                    <tr>
                                                                                        <td valign="top" style="padding:48px 48px 32px">
                                                                                            <div id="m_-2024486289125691792body_content_inner" style="color:#636363;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:14px;line-height:150%;text-align:left">
                                                                                                <p style="margin:0 0 16px">The email address """+receiver_email+""" has been chosen to be registered on the UNLOCK 4/90 service.</p>
                                                                                                <p style="margin:0 0 16px">In order to confirm your email address, use the following code:</p>
                                                                                                <h1 style="margin:0 0 16px; font-weight: 900">"""+email_verification_code+"""</h1>
                                                                                                <p style="margin:0 0 16px">If it wasn't you to request the registration on UNLOCK 4/90, we kindly ask you to skip this message.</p>
                                                                                                <font color="#888888">
                                                                                                </font>
                                                                                            </div>
                                                                                            <font color="#888888">
                                                                                            </font>
                                                                                        </td>
                                                                                    </tr>
                                                                                </tbody>
                                                                            </table>
                                                                            <font color="#888888">
                                                                            </font>
                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                            <font color="#888888">
                                                            </font>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                            <font color="#888888">
                                            </font>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" valign="top">
                                            <table border="0" cellpadding="10" cellspacing="0" width="600" id="m_-2024486289125691792template_footer">
                                                <tbody>
                                                    <tr>
                                                        <td valign="top" style="padding:0;border-radius:6px">
                                                            <table border="0" cellpadding="10" cellspacing="0" width="100%">
                                                                <tbody>
                                                                    <tr>
                                                                        <td colspan="2" valign="middle" id="m_-2024486289125691792credit" style="border-radius:6px;border:0;color:#8a8a8a;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:12px;line-height:150%;text-align:center;padding:24px 0">
                                                                            <p style="margin:0 0 16px">UNLOCK 4/90</p>
                                                                        </td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </font>
            </div>
            """

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            message.attach(part1)
            message.attach(part2)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, email_password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )

            phone = self.request.get("phoneNumber")
            sms_verification_code = get_random_string(6)
            doc_ref = db.collection('users').document(self.request.get("username"))
            doc_ref.set({
                'email_verification_code': email_verification_code,
                'sms_verification_code': sms_verification_code
            }, merge=True)
            f = open("semysmskey.txt", "r")
            url = 'https://semysms.net/api/3/sms.php?token='+f.read()+'&device=249608&phone=%2B39'+phone+'&msg=%5BUNLOCK%204%2F90%5D%20Use%20the%20code%20'+sms_verification_code+'%20to%20continue%20with%20the%20signup%20process.'
            response = requests.get(url)
            if response.status_code == 200:
                self.response.headers.add_header('Content-Type', 'application/json')
                result = {
                    'email': receiver_email,
                    'phone': phone,
                    'message': 'Verification SMS sent.'
                  }
                self.response.write(json.dumps(result))
                return
            else:
                self.response.write("An error has been encountered while sending the verification SMS.")
                self.response.set_status(response.status_code, "An error has been encountered while sending the verification SMS.")
                

class VerifyEmailHandler(webapp3.RequestHandler):
        def write_form(self, username="", email="", username_error="", password_error="", verify_error="", email_error=""):
                self.response.out.write(jinja_env.get_template('verifyemail.html').render())
                # self.response.out.write(signupform%{"username": username,
                #                                                                                 "email": email,
                #                                                                                 "username_error": username_error,
                #                                                                                 "password_error": password_error,
                #                                                                                 "verify_error": verify_error,
                #                                                                                 "email_error": email_error})
        def get(self):
                self.write_form()
        def post(self):
            if self.request.get("email_code_input") == (db.collection('users').document(self.request.get("username")).get({'email_verification_code'}).to_dict())['email_verification_code']:
                doc_ref = db.collection('users').document(self.request.get("username"))
                doc_ref.set({
                    'email': self.request.get("email")
                }, merge=True)
                self.response.headers.add_header('Content-Type', 'application/json')
                result = {
                    'message': 'Email verified and registered successfully.'
                  }
                self.response.write(json.dumps(result))
                return
            else:
                self.response.write("The wrong code has been entered for email verification.")
                self.response.set_status(400, "The wrong code has been entered for email verification.")

class VerifyPhoneHandler(webapp3.RequestHandler):
        def write_form(self, username="", email="", username_error="", password_error="", verify_error="", email_error=""):
                self.response.out.write(jinja_env.get_template('verifyphone.html').render())
                # self.response.out.write(signupform%{"username": username,
                #                                                                                 "email": email,
                #                                                                                 "username_error": username_error,
                #                                                                                 "password_error": password_error,
                #                                                                                 "verify_error": verify_error,
                #                                                                                 "email_error": email_error})
        def get(self):
                self.write_form()
        def post(self):
            if self.request.get("sms_code_input") == (db.collection('users').document(self.request.get("username")).get({'sms_verification_code'}).to_dict())['sms_verification_code']:
                doc_ref = db.collection('users').document(self.request.get("username"))
                doc_ref.set({
                    'phone': self.request.get("phone")
                }, merge=True)
                self.response.headers.add_header('Content-Type', 'application/json')
                result = {
                    'message': 'Phone number verified and registered successfully.'
                  }
                self.response.write(json.dumps(result))
                return
            else:
                self.response.write("The wrong code has been entered for phone number verification.")
                self.response.set_status(400, "The wrong code has been entered for phone number verification.")

class TutorialHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('tutorial.html').render())

class SuccessHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('success.html').render())

class NewPasswordHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('newpassword.html').render())
    def post(self, cf_error="", phone_error=""):
            username = self.request.get("username")
            cf = self.request.get("cf")
            phone = self.request.get("phone")
            if username == "":
                self.response.write("Enter the username.")
                self.response.set_status(400, "Enter the username.")
            else:
                if db.collection('users'):
                    if db.collection('users').document(username).get().exists:
                        if len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2:
                            if cf == "242436562" and phone == db.collection('users').document(username).get({'phone'}).to_dict()['phone']:
                                
                                email_verification_code = get_random_string(6)

                                sender_email = "unlock490app@gmail.com"
                                receiver_email = db.collection('users').document(username).get({'email'}).to_dict()['email']
                                f = open("emailpassword.txt", "r")
                                email_password = f.read()

                                message = MIMEMultipart("alternative")
                                message["Subject"] = "Codice di verifica"
                                message["From"] = sender_email
                                message["To"] = receiver_email

                                # Create the plain-text and HTML version of your message
                                text = """\
                                The account with the username """+username+""", registered with this email address on the UNLOCK 4/90 service, has requested to reset the password.
                                To comfirm the request, use the following code:
                                """+email_verification_code+"""
                                If it wasn't you to request the reset of the password for accessing UNLOCK 4/90, we kindly ask you to skip this message."""
                                html = """\
                                <div style="overflow: hidden;">
                                    <font size="-1">
                                        <u></u>
                                        <div marginwidth="0" marginheight="0" style="padding:0">
                                            <div id="m_-2024486289125691792wrapper" dir="ltr" style="background-color:#ffffff;margin:0;padding:70px 0;width:100%">
                                                <font color="#888888">
                                                </font>
                                                <table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%">
                                                    <tbody>
                                                        <tr>
                                                            <td align="center" valign="top">
                                                                <div id="m_-2024486289125691792template_header_image">
                                                                    <p style="margin-top:0">
                                                                        <img src="https://unlock490firebase.ew.r.appspot.com/static/img/logo.png" alt="UNLOCK 4/90" style="border:none;display:inline-block;font-size:14px;font-weight:bold;height:auto;outline:none;text-decoration:none;text-transform:capitalize;vertical-align:middle;max-width:100%;margin-left:0;margin-right:0">
                                                                    </p>
                                                                </div>
                                                                <font color="#888888">
                                                                </font>
                                                                <font color="#888888">
                                                                </font>
                                                                <table border="0" cellpadding="0" cellspacing="0" width="600" id="m_-2024486289125691792template_container" style="background-color:#f7f7f7;border:1px solid #e5e5e5;border-radius:3px">
                                                                    <tbody>
                                                                        <tr>
                                                                            <td align="center" valign="top">
                                                                                <table border="0" cellpadding="0" cellspacing="0" width="100%" id="m_-2024486289125691792template_header" style="background-color:#0048af;color:#ffffff;border-bottom:0;font-weight:bold;line-height:100%;vertical-align:middle;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;border-radius:3px 3px 0 0">
                                                                                    <tbody>
                                                                                        <tr>
                                                                                            <td id="m_-2024486289125691792header_wrapper" style="padding:36px 48px;display:block">
                                                                                                <h1 style="font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:30px;font-weight:300;line-height:150%;margin:0;text-align:left;color:#ffffff">Verifica email per UNLOCK 4/90</h1>
                                                                                            </td>
                                                                                        </tr>
                                                                                    </tbody>
                                                                                </table>
                                                                            </td>
                                                                        </tr>
                                                                        <tr>
                                                                            <td align="center" valign="top">
                                                                                <font color="#888888">
                                                                                </font>
                                                                                <table border="0" cellpadding="0" cellspacing="0" width="600" id="m_-2024486289125691792template_body">
                                                                                    <tbody>
                                                                                        <tr>
                                                                                            <td valign="top" id="m_-2024486289125691792body_content" style="background-color:#f7f7f7">
                                                                                                <font color="#888888">
                                                                                                </font>
                                                                                                <table border="0" cellpadding="20" cellspacing="0" width="100%">
                                                                                                    <tbody>
                                                                                                        <tr>
                                                                                                            <td valign="top" style="padding:48px 48px 32px">
                                                                                                                <div id="m_-2024486289125691792body_content_inner" style="color:#636363;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:14px;line-height:150%;text-align:left">
                                                                                                                    <p style="margin:0 0 16px">The account with the username """+username+""", registered with this email address on the UNLOCK 4/90 service, has requested to reset the password.</p>
                                                                                                                    <p style="margin:0 0 16px">To comfirm the request, use the following code:</p>
                                                                                                                    <h1 style="margin:0 0 16px; font-weight: 900">"""+email_verification_code+"""</h1>
                                                                                                                    <p style="margin:0 0 16px">If it wasn't you to request the reset of the password for accessing UNLOCK 4/90, we kindly ask you to skip this message.</p>
                                                                                                                    <font color="#888888">
                                                                                                                    </font>
                                                                                                                </div>
                                                                                                                <font color="#888888">
                                                                                                                </font>
                                                                                                            </td>
                                                                                                        </tr>
                                                                                                    </tbody>
                                                                                                </table>
                                                                                                <font color="#888888">
                                                                                                </font>
                                                                                            </td>
                                                                                        </tr>
                                                                                    </tbody>
                                                                                </table>
                                                                                <font color="#888888">
                                                                                </font>
                                                                            </td>
                                                                        </tr>
                                                                    </tbody>
                                                                </table>
                                                                <font color="#888888">
                                                                </font>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td align="center" valign="top">
                                                                <table border="0" cellpadding="10" cellspacing="0" width="600" id="m_-2024486289125691792template_footer">
                                                                    <tbody>
                                                                        <tr>
                                                                            <td valign="top" style="padding:0;border-radius:6px">
                                                                                <table border="0" cellpadding="10" cellspacing="0" width="100%">
                                                                                    <tbody>
                                                                                        <tr>
                                                                                            <td colspan="2" valign="middle" id="m_-2024486289125691792credit" style="border-radius:6px;border:0;color:#8a8a8a;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:12px;line-height:150%;text-align:center;padding:24px 0">
                                                                                                <p style="margin:0 0 16px">UNLOCK 4/90</p>
                                                                                            </td>
                                                                                        </tr>
                                                                                    </tbody>
                                                                                </table>
                                                                            </td>
                                                                        </tr>
                                                                    </tbody>
                                                                </table>
                                                            </td>
                                                        </tr>
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    </font>
                                </div>
                                """

                                # Turn these into plain/html MIMEText objects
                                part1 = MIMEText(text, "plain")
                                part2 = MIMEText(html, "html")

                                # Add HTML/plain-text parts to MIMEMultipart message
                                # The email client will try to render the last part first
                                message.attach(part1)
                                message.attach(part2)

                                # Create secure connection with server and send email
                                context = ssl.create_default_context()
                                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                                    server.login(sender_email, email_password)
                                    server.sendmail(
                                        sender_email, receiver_email, message.as_string()
                                    )

                                sms_verification_code = get_random_string(6)
                                doc_ref = db.collection('users').document(self.request.get("username"))
                                doc_ref.set({
                                    'email_verification_code': email_verification_code,
                                    'sms_verification_code': sms_verification_code
                                }, merge=True)
                                f = open("semysmskey.txt", "r")
                                url = 'https://semysms.net/api/3/sms.php?token='+f.read()+'&device=249608&phone=%2B39'+phone+'&msg=%5BUNLOCK%204%2F90%5D%20Enter%20the%20code%20'+sms_verification_code+'%20to%20continue%20with%20the%20reset%20of%20the%20password.'
                                response = requests.get(url)
                                if response.status_code == 200:
                                    self.response.headers.add_header('Content-Type', 'application/json')
                                    result = {
                                        'email': db.collection('users').document(username).get({'email'}).to_dict()['email'],
                                        'message': 'Password reset process started.'
                                    }
                                    self.response.write(json.dumps(result))
                                    return
                                else:
                                    self.response.write("An error was encountered while sending the verification SMS.")
                                    self.response.set_status(response.status_code, "An error was encountered while sending the verification SMS.")
                            else:
                                if not cf == "242436562":
                                        cf_error = "The Social Security Number for this username is incorrect."
                                if not phone == db.collection('users').document(username).get({'phone'}).to_dict()['phone']:
                                        phone_error = "The phone number for this username is incorrect."
                                self.response.write("<ul style='list-style-type:none;padding:0;'><li>"+cf_error+"</li><li>"+phone_error+"</li></ul>")
                                self.response.set_status(400, "<ul style='list-style-type:none;padding:0;'><li>"+cf_error+"</li><li>"+phone_error+"</li></ul>")
                        else:
                            self.response.write("The signup process has not been completed yet.")
                            self.response.set_status(400, "The signup process has not been completed yet.")
                    else:
                        self.response.write("The username you entered does not exist.")
                        self.response.set_status(400, "The username you entered does not exist.")
                else:
                    self.response.write("The username you entered does not exist.")
                    self.response.set_status(400, "The username you entered does not exist.")

class VerifyEmailForRecoveryHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('verifyemailforrecovery.html').render())
    def post(self):
        if self.request.get("email_code_input") == (db.collection('users').document(self.request.get("username")).get({'email_verification_code'}).to_dict())['email_verification_code']:
            doc_ref = db.collection('users').document(self.request.get("username"))
            doc_ref.set({
                'email_verified': 1
            }, merge=True)
            self.response.headers.add_header('Content-Type', 'application/json')
            result = {
                'message': 'Email verified successfully.'
              }
            self.response.write(json.dumps(result))
            return
        else:
            self.response.write("A wrong code has been entered for email verification.")
            self.response.set_status(400, "A wrong code has been entered for email verification.")

class VerifyPhoneForRecoveryHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('verifyphoneforrecovery.html').render())
    def post(self):
        if self.request.get("sms_code_input") == (db.collection('users').document(self.request.get("username")).get({'sms_verification_code'}).to_dict())['sms_verification_code']:
            doc_ref = db.collection('users').document(self.request.get("username"))
            doc_ref.set({
                'phone_verified': 1
            }, merge=True)
            self.response.headers.add_header('Content-Type', 'application/json')
            result = {
                'message': 'Phone number verified successfully.'
              }
            self.response.write(json.dumps(result))
            return
        else:
            self.response.write("A wrong code has been entered for phone number verification.")
            self.response.set_status(400, "A wrong code has been entered for phone number verification.")

class ChooseNewPasswordHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('choosenewpassword.html').render())
    def post(self, password_error="", verify_error=""):
            username = self.request.get("username")
            password = self.request.get("password")
            verify = self.request.get("verify")
            oldpassword = self.request.get("oldpassword")
            if oldpassword == "":
                if db.collection('users').document(username).get({'email_verified'}).to_dict()['email_verified'] == 1 and db.collection('users').document(username).get({'phone_verified'}).to_dict()['phone_verified'] == 1:
                    if (valid_password(password) and password == verify):
                        password = make_pw_hash(username, password)
                        doc_ref = db.collection('users').document(username)
                        doc_ref.set({
                            'email_verified': 0,
                            'phone_verified': 0,
                            'password': password
                        }, merge=True)
                        self.response.headers.add_header('Content-Type', 'application/json')
                        result = {
                            'message': 'Password modified successfully'
                          }
                        self.response.write(json.dumps(result))
                        return
                    if not valid_password(password):
                            password_error = "You entered an invalid password."
                    if not password == verify:
                            verify_error = "Passwords don't match."
                    self.response.write("<ul style='list-style-type:none;padding:0;'><li>"+password_error+"</li><li>"+verify_error+"</li></ul>")
                    self.response.set_status(400, "<ul style='list-style-type:none;padding:0;'><li>"+password_error+"</li><li>"+verify_error+"</li></ul>")
                else:
                    self.response.write("Email address and phone number verification codes must be entered.")
                    self.response.set_status(400, "Email address and phone number verification codes must be entered.")
            else:
                if db.collection('users') and db.collection('users').document(username).get().exists and len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2 and oldpassword == db.collection('users').document(username).get({'password'}).to_dict()['password']:
                    if (valid_password(password) and password == verify):
                        password = make_pw_hash(username, password)
                        doc_ref = db.collection('users').document(username)
                        doc_ref.set({
                            'password': password
                        }, merge=True)
                        self.response.headers.add_header('Content-Type', 'application/json')
                        result = {
                            'message': 'Password modified successfully.'
                          }
                        self.response.write(json.dumps(result))
                        return
                    if not valid_password(password):
                            password_error = "You entered an invalid password."
                    if not password == verify:
                            verify_error = "Passwords don't match."
                    self.response.write("<ul style='list-style-type:none;padding:0;'><li>"+password_error+"</li><li>"+verify_error+"</li></ul>")
                    self.response.set_status(400, "<ul style='list-style-type:none;padding:0;'><li>"+password_error+"</li><li>"+verify_error+"</li></ul>")
                else:
                    self.response.write("The logged in user information is wrong.")
                    self.response.set_status(400, "The logged in user information is wrong.")

class RecoverySuccessHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('recoverysuccess.html').render())

class ProfileHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('profile.html').render())

class PickupHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('pickup.html').render())

class CheckPickupHandler(webapp3.RequestHandler):
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        if db.collection('users') and db.collection('users').document(username).get().exists and len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2 and password == db.collection('users').document(username).get({'password'}).to_dict()['password']:
            pickupdict = db.collection('users').document(username).get({'day_for_pickup', 'hour_for_pickup'}).to_dict()
            if len(pickupdict) == 2:
                self.response.headers.add_header('Content-Type', 'application/json')
                result = {
                    'redirectToLogin': 0,
                    'day_for_pickup': pickupdict['day_for_pickup'],
                    'hour_for_pickup': pickupdict['hour_for_pickup'],
                    'message': "The user has already chosen a pickup time."
                  }
                self.response.write(json.dumps(result))
            else:
                self.response.headers.add_header('Content-Type', 'application/json')
                result = {
                    'redirectToLogin': 0,
                    'day_for_pickup': "",
                    'hour_for_pickup': "",
                    'message': "A pickup time has not been chosen yet."
                  }
                self.response.write(json.dumps(result))
        else:
            self.response.headers.add_header('Content-Type', 'application/json')
            result = {
                'redirectToLogin': 1,
                'message': "The user hasn't logged in or the cookie is incorrect. Redirect user to login page."
              }
            self.response.write(json.dumps(result))

class PickupHourHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('pickuphour.html').render())

class ConfirmPickupHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('confirmpickup.html').render())
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        day_for_pickup = self.request.get("day_for_pickup")
        hour_for_pickup = self.request.get("hour_for_pickup")
        if db.collection('users') and db.collection('users').document(username).get().exists and len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2 and password == db.collection('users').document(username).get({'password'}).to_dict()['password']:
            doc_ref = db.collection('users').document(username)
            doc_ref.set({
                'day_for_pickup': day_for_pickup,
                'hour_for_pickup': hour_for_pickup
            }, merge=True)
            self.response.headers.add_header('Content-Type', 'application/json')
            result = {
                'redirectToLogin': 0,
                'day_for_pickup': day_for_pickup,
                'hour_for_pickup': hour_for_pickup,
                'message': "Pickup time registered successfully."
              }
            self.response.write(json.dumps(result))
        else:
            self.response.headers.add_header('Content-Type', 'application/json')
            result = {
                'redirectToLogin': 1,
                'message': "The user hasn't logged in or the cookie is incorrect. Redirect user to login page."
              }
            self.response.write(json.dumps(result))

class ReadyForPickupHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('readyforpickup.html').render())

class GuideHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('guide.html').render())

class SettingsHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('settings.html').render())

class CalendarHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('calendar.html').render())

class HospitalInfoHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('hospitalinfo.html').render())

class DashboardHandler(webapp3.RequestHandler):
    def get(self):
        self.response.out.write(jinja_env.get_template('dashboard.html').render())

class SubscribeToPushHandler(webapp3.RequestHandler):
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        endpoint = self.request.get("endpoint")
        p256dh = self.request.get("p256dh")
        auth = self.request.get("auth")
        if db.collection('users'):
            if db.collection('users').document(username).get().exists:
                if len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2:
                    if password == db.collection('users').document(username).get({'password'}).to_dict()['password']:
                        doc_ref = db.collection('users').document(username)
                        doc_ref.set({
                            'endpoint': endpoint,
                            'p256dh': p256dh,
                            'auth': auth
                        }, merge=True)
                        self.response.headers.add_header('Content-Type', 'application/json')
                        result = {
                            'message': "The user has subscribed to the push notifications successfully"
                          }
                        self.response.write(json.dumps(result))
                    else:
                        self.response.write("The password hash memorized in the cookie doesn't match.")
                        self.response.set_status(400, "The password hash memorized in the cookie doesn't match.")
                else:
                    self.response.write("The signup process must be completed before logging in.")
                    self.response.set_status(400, "The signup process must be completed before logging in.")
            else:
                self.response.write("The username you entered doesn't exist.")
                self.response.set_status(400, "The username you entered doesn't exist.")
        else:
            self.response.write("The username you entered doesn't exist.")
            self.response.set_status(400, "The username you entered doesn't exist.")

def render_str(template, **params):
                t = jinja_env.get_template(template)
                return t.render(params)

class Handler(webapp3.RequestHandler):
        def write(self, *a, **kw):
                self.response.out.write(*a, **kw)
        def render_str(self, template, **params):
                return render_str(template, **params)
        def render(self, template, **kw):
                self.write(self.render_str(template, **kw))

class LoginHandler(Handler):
        def get(self):
                self.render("login.html", username="", login_error="")
        def post(self):
                username = self.request.get("username")
                password = self.request.get("password")
                if username == "":
                    self.response.write("Enter the username.")
                    self.response.set_status(400, "Enter the username.")
                else:
                    if db.collection('users'):
                        if db.collection('users').document(username).get().exists:
                            if len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2:
                                if valid_pw(username, password, db.collection('users').document(username).get({'password'}).to_dict()['password']):
                                    self.response.headers.add_header("Set-Cookie", "userid=%s; Path=/"%(username+"|"+db.collection('users').document(username).get({'password'}).to_dict()['password']))
                                    self.response.headers.add_header('Content-Type', 'application/json')
                                    result = {
                                        'message': 'User logged in successfully.'
                                      }
                                    self.response.write(json.dumps(result))
                                else:
                                    self.response.write("The password you entered is wrong.")
                                    self.response.set_status(400, "The password you entered is wrong.")
                            else:
                                self.response.write("The signup process must be completed before logging in.")
                                self.response.set_status(400, "The signup process must be completed before logging in.")
                        else:
                            self.response.write("The username you entered doesn't exist.")
                            self.response.set_status(400, "The username you entered doesn't exist.")
                    else:
                        self.response.write("The username you entered doesn't exist.")
                        self.response.set_status(400, "The username you entered doesn't exist.")

class CheckLoginHandler(Handler):
        def post(self):
                username = self.request.get("username")
                password = self.request.get("password")
                if db.collection('users') and db.collection('users').document(username).get().exists and len(db.collection('users').document(username).get({'email', 'phone'}).to_dict()) == 2 and password == db.collection('users').document(username).get({'password'}).to_dict()['password']:
                    self.response.headers.add_header('Content-Type', 'application/json')
                    result = {
                        'redirectToLogin': 0,
                        'message': "The user has already logged in. Redirect user to pickup page."
                      }
                    self.response.write(json.dumps(result))
                else:
                    self.response.headers.add_header('Content-Type', 'application/json')
                    result = {
                        'redirectToLogin': 1,
                        'message': "The user hasn't logged in or the cookie is incorrect. Redirect user to login page."
                      }
                    self.response.write(json.dumps(result))

class LogoutHandler(Handler):
        def get(self):
                self.response.headers.add_header("Set-Cookie", "userid=; Path=/")
                self.redirect("/")

import mimetypes
class StaticFileHandler(webapp3.RequestHandler):
    def get(self, path):
        abs_path = os.path.abspath(os.path.join(self.app.config.get('webapp3_static.static_file_path', 'static'), path))
        if os.path.isdir(abs_path) or abs_path.find(os.getcwd()) != 0:
            self.response.set_status(403)
            return
        try:
            f = open(abs_path, 'r')
            self.response.headers.add_header('Content-Type', mimetypes.guess_type(abs_path)[0])
            self.response.headers['Content-Type'] = mimetypes.guess_type(abs_path)[0]
            self.response.out.write(f.read())
            f.close()
        except:
            self.response.set_status(404)

app = webapp3.WSGIApplication([
        ('/', MainPage),
        ('/index', MainPage),
        ('/index.html', MainPage),
        ('/tutorial', TutorialHandler),
        ('/login', LoginHandler),
        ('/checklogin', CheckLoginHandler),
        ('/logout', LogoutHandler),
        ('/signup', SignupHandler),
        ('/emailphonesignup', EmailPhoneSignupHandler),
        ('/verifyemail', VerifyEmailHandler),
        ('/verifyphone', VerifyPhoneHandler),
        ('/success', SuccessHandler),
        ('/newpassword', NewPasswordHandler),
        ('/verifyemailforrecovery', VerifyEmailForRecoveryHandler),
        ('/verifyphoneforrecovery', VerifyPhoneForRecoveryHandler),
        ('/choosenewpassword', ChooseNewPasswordHandler),
        ('/recoverysuccess', RecoverySuccessHandler),
        ('/profile', ProfileHandler),
        ('/pickup', PickupHandler),
        ('/checkpickup', CheckPickupHandler),
        ('/pickuphour', PickupHourHandler),
        ('/confirmpickup', ConfirmPickupHandler),
        ('/readyforpickup', ReadyForPickupHandler),
        ('/guide', GuideHandler),
        ('/settings', SettingsHandler),
        ('/calendar', CalendarHandler),
        ('/hospitalinfo', HospitalInfoHandler),
        ('/subscribetopush', SubscribeToPushHandler),
        ('/dashboard', DashboardHandler),
        (r'/static/(.+)', StaticFileHandler)
], debug = True)