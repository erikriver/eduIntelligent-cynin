==============
 MaildropHost
==============

The MaildropHost product provides support for sending email from
within the Zope environment using Maildrop Host objects. Unlike the 
built-in MailHost object, the sending is done asynchronously from 
a separate process.

The advantage is that sending mail from within web pages becomes 
much faster because invoking the mail machinery can be slow. With 
Maildrop Host the web page will return immediately.

Maildrop Host uses a separate Python process to monitor the mail 
spool inside the product and handle mail in intervals that can be
set by the administrator. There are separate start scripts included
with the product which can be used to start this monitor process. 

Mails that cannot be sent successfully stay in the internal spool. 
Every attempt to send email is logged to a log file kept by the 
monitor process. This log file is closed after each maildrop run,
so it is safe to rotate it without sending any special signals to
the maildrop daemon.

The maildrop daemon that delivers mail supports StartTLS and even
authenticated SMTP.

Starting with Zope version 2.11.0-beta the standard MailHost 
implementation does asynchronous mail handling as well. If you run 
Zope 2.11 and up you should look at the standard MailHost product 
first and see if it fits your requirement before installing the 
MaildropHost product.


Requirements
============

- a working SMTP server

- Zope 2.8.0 or higher

- A UNIX operating system if you run the maildrop daemon.


Usage
=====

Follow these steps to use the product after you followed the
procedures outlined in INSTALL.txt:

- edit the "config" configuration script in the toplevel
  MaildropHost folder to reflect your particular needs, or
  (optionally) add your own config file in a different location
  on the filesystem.

- start the mail spool checker by running the "start_maildrop"
  script or with the other start scripts included in the package,
  which can be found in maildrop/bin underneath the toplevel
  MaildropHost folder.

- instantiate a Maildrop Host instance in your ZODB; if you
  created a config file in a different location, specify the
  filesystem path in a 'config_path' attribute on the Maildrop
  Host object.

- Now you can create emails using e.g. the dtml-sendmail tag and 
  point the sendmail tag to the Maildrop Host instance using the 
  mailhost="XYZ" argument inside the sendmail tag, or by using
  the MailHost API (see the Zope Help System).

Instead of using dtml-sendmail and a Maildrop Host instance you can
create email messages any way you like. As long as the formatting is
correct (so that the mail spool checker can parse it, see the file
SAMPLE_MAIL.txt for an example) and you write it to the spool
directory which is at $MAILDROP_HOME/spool (or $MAILDROP_SPOOL if
defined) then the mail spool checker will pick it up and try to
deliver it.


Mail file format
================

The format for a mail file (see SAMPLE_MAIL.txt) is very simple. The
first line contains the recipient address, prefixed by "##To:". The
second line is the sender address, prefixed by "##From:". These are
equivalent to the "envelope" sender and receiver addresses.

The next few lines are headers that become part of the message body, 
they are "To: <recipient>", "From: <sender>" and "Subject: <subject>".

The actual message is separated from the headers by a blank line.

