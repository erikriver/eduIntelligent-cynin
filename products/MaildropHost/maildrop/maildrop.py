#!/usr/bin/env python

#####################################################################
#
# maildrop  A daemon to handle mail delivery for the MaildropHost
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################
__version__ = "$Revision: 1618 $"[11:-2]

from email.Utils import make_msgid
from stringparse import parse_assignments
from stringparse import ParserSyntaxError
import smtplib
import os
import sys
import time
import rfc822
import atexit
import signal

FATAL_ERROR_CODES = ('500', '501', '502', '503', '504', '550', '551', '553')
MaildropError = 'Maildrop Error'

def usage():
    print 'Usage: maildrop.py /path/to/config'


def mainloop():                   
    while 1:
        # Are there any files in the spool directory?
        to_be_sent = []
        all_files = []

        for spool in MAILDROP_SPOOLS:
            all_files.extend([os.path.join(spool, x) for x in os.listdir(spool)])

        # Remove lock files
        clean_files = [x for x in all_files 
                         if not x.endswith('.lck')]

        # Remove files that were locked by the previously removed lock files
        clean_files = [x for x in clean_files 
                         if not '%s.lck' % x in all_files]

        # Remove directories
        to_be_sent = [x for x in clean_files if not os.path.isdir(x)]
        
        if len(to_be_sent) > 0:
            # Open the log file
            time_stamp = time.strftime('%Y/%m/%d %H:%M:%S')
            log_file = open(MAILDROP_LOG_FILE, 'a')
            msg = '\n### Started at %s...' % time_stamp
            log_file.write(msg)
            if DEBUG: print msg
    
            while len(to_be_sent) > 0:
                if (MAILDROP_BATCH == 0) or (MAILDROP_BATCH > len(to_be_sent)):
                    batch = len(to_be_sent)
                else:
                    batch = MAILDROP_BATCH
                    
                # Send mail
                try:
                    smtp_server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                    #smtp_server.set_debuglevel(1)
                    smtp_server.ehlo()
                except smtplib.SMTPConnectError:
                    # SMTP server did not respond. Log it and stop processing.
                    time_stamp = time.strftime('%Y/%m/%d %H:%M:%S')
                    err_msg = '!!!!! Connection error at %s' % time_stamp
                    finish_msg = '### Finished at %s' % time_stamp
                    log_file.write(err_msg)
                    if DEBUG: print err_msg
                    log_file.write(finish_msg)
                    if DEBUG: print finish_msg
                    log_file.close()
                    break
    
                if MAILDROP_TLS > 0:
                    if (MAILDROP_TLS > 1 and 
                         not smtp_server.has_extn('starttls')):
                        # Problem: TLS is required but the server does not 
                        # offer it We stop processing here.
                        time_stamp = time.strftime('%Y/%m/%d %H:%M:%S')
                        err_msg = '!!!!! TLS unavailable at %s' % time_stamp
                        finish_msg = '### Finished at %s' % time_stamp
                        log_file.write(err_msg)
                        if DEBUG: print err_msg
                        log_file.write(finish_msg)
                        if DEBUG: print finish_msg
                        log_file.close()
                        break
    
                    smtp_server.starttls()

                    # We have to say Hello again after starting TLS
                    smtp_server.ehlo()
    
                if MAILDROP_LOGIN != '' and MAILDROP_PASSWORD != '':
                    # Login is required to send mail
                    if not smtp_server.has_extn('auth'):
                        # The server does not offer authentication but we want it
                        # We stop processing here.
                        time_stamp = time.strftime('%Y/%m/%d %H:%M:%S')
                        err_msg = '!!!!! Authentication unavailable at %s' % time_stamp
                        finish_msg = '### Finished at %s' % time_stamp
                        log_file.write(err_msg)
                        if DEBUG: print err_msg
                        log_file.write(finish_msg)
                        if DEBUG: print finish_msg
                        log_file.close()
                        break
    
                    try:
                        smtp_server.login(MAILDROP_LOGIN, MAILDROP_PASSWORD)
                    except smtplib.SMTPAuthenticationError:
                        # Authentication with the given credentials fails.
                        # We stop processing here.
                        time_stamp = time.strftime('%Y/%m/%d %H:%M:%S')
                        err_msg = '!!!!! Authentication failed at %s' % time_stamp
                        finish_msg = '### Finished at %s' % time_stamp
                        log_file.write(err_msg)
                        if DEBUG: print err_msg
                        log_file.write(finish_msg)
                        if DEBUG: print finish_msg
                        log_file.close()
                        break
    
                for file_path in to_be_sent[0:batch]:
                    mail_dict = read_mail(file_path)
                    if not mail_dict: 
                        continue

                    # Create mail and send it off
                    h_from = mail_dict.get('From')
                    h_to = mail_dict.get('To')
                    h_to_list = []
                    for item in rfc822.AddressList(h_to):
                        h_to_list.append(item[1])
                    h_body = mail_dict.get('body')

                    if ADD_MESSAGEID:
                        h_body = 'Message-Id: %s\n%s' % (make_msgid(), h_body)
    
                    try:
                        smtp_server.sendmail(h_from, h_to_list, h_body)
                        stat = 'OK'
                        os.remove(file_path)
                    except smtplib.SMTPRecipientsRefused, e:
                        stat = 'FATAL: ', str(e)
                        for (addr, error) in e.recipients.items():
                             if str(error[0]) in FATAL_ERROR_CODES:
                                 os.remove(file_path)
                                 break
                    except smtplib.SMTPException, e:
                        stat = 'BAD: ', str(e)
    
                    mail_msg = '\n%s\t %s' % (stat, h_to)
                    log_file.write(mail_msg)
                    if DEBUG: print mail_msg
                    log_file.flush()
                    if WAIT_INTERVAL:
                        time.sleep(WAIT_INTERVAL)
    
                to_be_sent = to_be_sent[batch:]

                try:
                    smtp_server.quit()
                except smtplib.SMTPServerDisconnected:
                    pass
    
            time_stamp = time.strftime('%Y/%m/%d %H:%M:%S')
            finish_msg = '\n### Finished at %s\n' % time_stamp
            log_file.write(finish_msg)
            if DEBUG: print finish_msg
            log_file.close()
            
        time.sleep(MAILDROP_INTERVAL)


def read_mail(file_path):
    """ Reads in a mail from a file, returns a dictionary with keys
    for headers and body 
    """    
    # Read in file
    file_handle = open(file_path, 'r')
    file_contents = file_handle.read()
    file_handle.close()
    
    # Is this a real mail turd?
    if not file_contents.startswith('##To:'):
        return
    
    # Parse and handle content (mail it out)
    mail_dict = {}
    file_lines = file_contents.split('\n')
    
    for i in range(len(file_lines)):
        if file_lines[i].startswith('##'):
            header_line = file_lines[i][2:]
            header_key, header_val = header_line.split(':', 1)
            mail_dict[header_key] = header_val
        else:
            mail_dict['body'] = '\n'.join(file_lines[i:])
            break

    return mail_dict
    

def write_pid(pidfile_path, pid):
    """ Write the daemon pid to our pid file """
    pid_file = open(pidfile_path, 'w')
    pid_file.write(str(pid))
    pid_file.close()


def exit_function(pidfile_path):
    # Remove the daemon pid file
    try: 
        os.unlink(pidfile_path)
    except: 
        pass


def handle_sigterm(signum, frame):
    sys.exit(0)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            usage()
            sys.exit(1)
    
        c_dir, c_file = os.path.split(sys.argv[1])
    
        try:
            c_file = open(sys.argv[1])
        except IOError:
            raise MaildropError, 'Cannot find config file "%s"' % c_file

        try:
            config = dict(parse_assignments(c_file.read()))
        except ParserSyntaxError:
            raise MaildropError, 'Cannot load config from "%s"' % c_file
    
        MAILDROP_HOME = config['MAILDROP_HOME']
        MAILDROP_INTERVAL = config['MAILDROP_INTERVAL']
        MAILDROP_BATCH = config['MAILDROP_BATCH']
        MAILDROP_TLS = config['MAILDROP_TLS']
        MAILDROP_LOGIN = config['MAILDROP_LOGIN']
        MAILDROP_PASSWORD = config['MAILDROP_PASSWORD']
        SMTP_HOST = config['SMTP_HOST']
        SMTP_PORT = config['SMTP_PORT']
        DEBUG = config['DEBUG']
        WAIT_INTERVAL = config['WAIT_INTERVAL']
        SUPERVISED_DAEMON = config['SUPERVISED_DAEMON']

        # Windows does not support the detaching process below, so it is
        # always forced into debug mode.
        if sys.platform.startswith('win'):
            DEBUG = 1

        MAILDROP_SPOOL = config.get('MAILDROP_SPOOL')
        if MAILDROP_SPOOL:
            MAILDROP_SPOOLS = [x.strip() for x in MAILDROP_SPOOL.split(';')]
        else:
            MAILDROP_SPOOLS = [os.path.join(MAILDROP_HOME, 'spool')]

        MAILDROP_VAR = config.get('MAILDROP_VAR',
                                  os.path.join(MAILDROP_HOME, 'var'))
        MAILDROP_LOG_FILE = config.get('MAILDROP_LOG_FILE',
                                       os.path.join(MAILDROP_VAR, 'maildrop.log'))
        MAILDROP_PID_FILE = config.get('MAILDROP_PID_FILE',
                                       os.path.join(MAILDROP_VAR, 'maildrop.pid'))

        ADD_MESSAGEID = config.get('ADD_MESSAGEID', False)

        for spool in MAILDROP_SPOOLS:
            if not os.path.isdir(spool):
                os.makedirs(spool)
    
        if not os.path.isdir(MAILDROP_VAR):
            os.makedirs(MAILDROP_VAR)
    
        try:
            mail_server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            mail_server.ehlo()
    
            if MAILDROP_TLS > 1:
                mail_server.starttls()
                mail_server.ehlo()
    
            if MAILDROP_LOGIN != '' and MAILDROP_PASSWORD != '':
                mail_server.login(MAILDROP_LOGIN, MAILDROP_PASSWORD)
    
            mail_server.quit()
        except:
            if DEBUG: import traceback; traceback.print_exc()
            msg = 'Invalid SMTP server "%s:%d"' % (SMTP_HOST, SMTP_PORT)
            raise MaildropError, msg

    except SystemExit: 
        sys.exit(0)
    except:
        usage()
        print 
        print 'An error occured, aborting...'
        print "%s: %s" % (sys.exc_type, sys.exc_value)
        print
        sys.exit(1)
    
    if not (DEBUG or SUPERVISED_DAEMON):
        # Do the Unix double-fork magic; see Stevens's book "Advanced
        # Programming in the UNIX Environment" (Addison-Wesley) for details
        # In DEBUG mode we do not fork/detach from the terminal!
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (
                e.errno, e.strerror)
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent; print eventual PID before exiting
                if DEBUG:
                    print "maildrop daemon PID %d" % pid
                write_pid(MAILDROP_PID_FILE, pid)
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (
                e.errno, e.strerror)
            sys.exit(1)
        atexit.register(exit_function,MAILDROP_PID_FILE)
        signal.signal(signal.SIGTERM,handle_sigterm)
    elif DEBUG:
        print '*****          Starting in DEBUG mode           *****'
        print '***** All log messages are shown on the console *****'
        sys.stdout.flush()

    # Start the daemon main loop
    mainloop()

