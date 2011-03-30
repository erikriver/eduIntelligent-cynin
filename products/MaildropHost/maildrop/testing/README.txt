Testing package

  This folder contains a configuration and start/stop scripts that
  help you test out the maildrop daemon given various
  configurations. Tweak the config to your heart's content and see the
  results by running the start/stop scripts.

  To create "fake" email traffic there is a script called "make_emails.py"
  that can be used to fill the spool directory ($MAILDROP_SPOOL or
  $MAILDROP_HOME/spool) with fake email messages. You need to specify how
  many messages to generate in total, how many of those are in "locked"
  status as if they are still being generated, and the recipient
  email(s). The script will randomly choose a recipient from the list of
  given email addresses.

  The main purpose is to make sure that...

  - your configuration is correct so that the maildrop daemon succeeds
    in getting mail to the given recipient

  - no email gets "lost" by the maildrop machinery (simple test: the
    total number of received messages by the list of provided recipients
    must match the total number of fake emails minus the number of locked
    emails!)

  - only "unlocked" emails get sent. "Locked" emails will be recognizable
    by their subject line.

  THE PURPOSE OF THESE SCRIPTS IS NOT TO ANNOY OTHERS! DO NOT SEND TO
  ADDRESSES THAT ARE NOT AWARE YOU ARE DOING IT!

