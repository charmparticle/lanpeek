# lanpeek
A simple script to make network traffic going through rsyslog to your machine more readable

Usage:

First, enable rsyslog on your computer:

    vim /etc/rsyslog.conf
    #uncomment the lines under "provides UDP syslog reception"
    
Then, enable rsyslog in your router, and have it send rsyslog packets to your computer.

if you have a 'bin' folder in your $HOME, simply copy lanpeek and lanpeek.py to ~/bin, then type `lanpeek`. `lanpeek -h` gives more options.
