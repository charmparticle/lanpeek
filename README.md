# lanpeek
A simple script to make network traffic going through rsyslog to your machine more readable

Usage:

First, enable rsyslog on your computer:

    vim /etc/rsyslog.conf
    #uncomment these lines (remove the leading '#'):
    #module(load="imudp")
    #input(type="imudp" port="514")
    
Then, enable rsyslog in your router, and have it send udp packets to your computer.

Now you are ready to parse packets. Install the necessary python libraries:

    sudo pip install colored

if you have a 'bin' folder in your $HOME that is also in your $PATH, simply copy lanpeek and lanpeek.py to ~/bin, then type `lanpeek`. `lanpeek -h` gives more options.
