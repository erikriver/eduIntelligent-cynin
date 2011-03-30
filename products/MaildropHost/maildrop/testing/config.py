# This file contains configuration data, some of which may be shared
# between the maildrop daemon and the MaildropHost object.
#
# IMPORTANT NOTE: This file is also sourced by a couple shell scripts,
#                 which means you must not have any whitespace around
#                 equal (=) signs!
#

# Which python interpreter to use for running the maildrop daemon
PYTHON="/usr/bin/python"

# The working directory keeping the spool and var directories
MAILDROP_HOME="/tmp/maildrop"

# You can override the spool directory with this directive
# Without it, it'll be the "spool" subdirectory of $MAILDROP_HOME
MAILDROP_SPOOL="/tmp/maildrop/spool"

# You can override the var directory with this directive
# Without it, it'll be the "var" subdirectory of $MAILDROP_HOME
# MAILDROP_VAR="/tmp/maildrop/var"

# You can override the pid file with this directive
# Without it, it'll be the "maildrop.pid" file of $MAILDROP_VAR
MAILDROP_PID_FILE="/tmp/maildrop.pid"

# You can override the log file with this directive
# Without it, it'll be the "maildrop.log" file of $MAILDROP_VAR
MAILDROP_LOG_FILE="/tmp/maildrop.log"

# The SMTP server to be used for sending out email (e.g. smtp-relay.domain.com)
SMTP_HOST="localhost"

# The SMTP server port used for sending out email
SMTP_PORT=25

# How long to wait between spool checks
MAILDROP_INTERVAL=10

# Set debug mode. This will PREVENT the daemon from detaching from
# the controlling terminal! Do not use in production!
DEBUG=1

# Debug Receiver is used for specific debug/testing situations where emails
# are created normally, but the envelope receiver is set to the value of
# DEBUG_RECEIVER so email ends up in one mailbox but looks exactly like the
# actual receiver would see it. Use for debugging purposes only. The value
# is a string containing one or more comma-separated addresses. 
DEBUG_RECEIVER=""

# Batch size for smtp-connection
# = 0 means bulk all mails at once
# > 0 means close/reopen connection after BATCH mails
MAILDROP_BATCH=10

# TLS usage. The values available are...
#   0 : Don't try to us TLS
#   1 : Try to use TLS if possible, but don't fail if TLS is not available
#   2 : Force TLS and fail if TLS is not available
# If a username/password is specified for the SMTP server, it is recommended
# to set the value to "2" to prevent password sniffing.
MAILDROP_TLS=2

# SMTP Authentication
# If the login and password are provided, authentication is attempted.
# If the authentication attempt fails, mail processing stops. Beware.
MAILDROP_LOGIN=""
MAILDROP_PASSWORD=""

# Wait between sending two mails, to avoid overloading the mail server
# This should be a float, in seconds
WAIT_INTERVAL=1.0
