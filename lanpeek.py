#!/usr/bin/env python
import commands
import os
import sys
import pickle
from colored import fg, bg, attr


def show_help():
    me = sys.argv[0]
    print("""invocation:
cat /var/log/syslog | {} run with default settings, no arguments
cat /var/log/syslog | {} -t host1 host2 host3 ...: show only requests with one of the target host(s)
cat /var/log/syslog | {} -n: only show ipv4 addresses; don't try to covert to domain names.
cat /var/log/syslog | {} -p: output plain text, no colors.
cat /var/log/syslog | {} -h: show this help message.

""").format(me, me, me, me, me)
    exit(0)

def verify_compound(a, r):
    if r in a:
        x = a.index(r)
        #the array length needs to be at least 1 larger than the index
        #where the compound arg switch appears
        if len(a) > x:
            i = x + 1
            g = x + 1
            for arg in a[g:]:
                #have we encountered a new argument switch?
                if '-' in arg:
                    if i == x + 1:
                        #no, this switch came right after the compound
                        #argument switch, so it was a mistake.
                        show_help()
                    else:
                        #yup! Our journey ends here, then.
                        return [s.lower() for s in a[g:i]]
                else:
                    #keep processing compound args, right to the end.
                    i = i + 1
                    if i == len(a):
                        return [s.lower() for s in a[g:i]]
        else:
            return False
    else:
        return False

def verify_args(a, gs, cs):
    a = [s.lower() for s in a]
    #cut compound args out; these will be verified separately.
    for c in cs:
        cind = verify_compound(a, c)
        if cind:
            for x in cind:
                del a[a.index(x)]
            del a[a.index(c)]
    #now we see if the user entered invalid args
    if len(a) > 1:
        for arg in a[1:]:
            if arg in gs:
                pass
            else:
                show_help()

def parse_args(a):
    valid_singles = ['-h', '-n', '-p']
    valid_compounds = ['-t']
    verify_args(a, valid_singles, valid_compounds)
    r={'filter':False, 'resolv':True, 'color':True}
    if '-h' in a[1:]:
        show_help()
    if len(a) == 1:
        return(r)
    if '-t' in a[1:]:
        r['filter'] = verify_compound(a, '-t')
    if '-p' in a[1:]:
        r['color'] = False
    if '-n' in a[1:]:
        r['resolv'] = False
    return(r)

def load_cache_file(i):
    global lanhost_cache
    global remotehost_cache

    try:
        if i == 0:
            with open(lcache_file, 'r') as f:
                lanhost_cache = pickle.load(f)
        elif i == 1:
            with open(rcache_file, 'r') as f:
                remotehost_cache = pickle.load(f)
    #If the lcache or rcache file is empty, pickle.load throw an
    #EOF error, but the program will otherwise work fine, so ignore it
    except EOFError:
        pass

def load_caches():
    try:
        i = 0
        for cache_file in lcache_file, rcache_file:
            if os.path.isfile(cache_file):
                load_cache_file(cache_file)
            else:
                if os.path.isdir(os.path.dirname(cache_file)):
                    open(cache_file, 'a').close()
                else:
                    os.makedirs(os.path.dirname(cache_file))
                    open(cache_file, 'a').close()
            i = i+1
    #maybe we don't have permission or something
    except OSError, e:
        print(e)
        exit()

def get_host(ip):
    #starting to look a bit like BASH :-p
    h = commands\
            .getoutput("host {}"\
            .format(ip))\
            .split(' ')[4]\
            .split('\n')[0][:-1]
    if h == "3(NXDOMAIN" or h == "1(FORMERR" or h == '' or h == 'recor':
        h = ip
    return(h)

def update_cache_file(f, cache):
    with open(f, 'w') as cache_file:
        pickle.dump(cache, cache_file)

def get_tuple_index(l, index, value):
    for pos,t in enumerate(l):
        if t[index] == value:
            return pos

def set_host(ip, cache):
    try:
        if ip in [i[0] for i in cache]:
            host = [i[1] for i in cache if i[0] == ip][0]
        else:
            host = get_host(ip)
            if host in [i[1] for i in cache]:
                #host has changed its ip. Update the entry
                ix = get_tuple_index(cache, 1, host) 
                cache[ix] = (ip,host)
            else:
                cache.append((ip, host))
    except:
        print('in set_host')
        print(sys.exc_info())
        exit()
    return(host)

def main(targets, resolve, colors):
    try:
        if resolve:
            global lcache_file
            global rcache_file
            lcache_file = os.path.expanduser('~/.cache/lanpeek/lhosts.txt')
            rcache_file = os.path.expanduser('~/.cache/lanpeek/rhosts.txt')
            lanhost_cache = []
            remotehost_cache = []
            load_caches()
        else:
            iplist = []
    
        while True:
            line = sys.stdin.readline()
            line = [s for s in line.split(' ') if s.strip()]
            try:
                day = line[1]
                time = line[2]
                lanip = [s for s in line if 'SRC=' in s][0].replace('SRC=','')
                remoteip = [s for s in line if 'DST=' in s][0].replace('DST=','')
                remoteport = [s for s in line if 'DPT=' in s][0].replace('DPT=','')
                
                if resolve:
                    lanhost = set_host(lanip, lanhost_cache)
                    remotehost = set_host(remoteip, remotehost_cache)
                    lanhost_index = [i[1] for i in lanhost_cache].index(lanhost)
                else:
                    lanhost = lanip
                    remotehost = remoteip
                    if lanhost not in iplist:
                        iplist.append(lanhost)
                    lanhost_index = iplist.index(lanhost)
                lanhost_formatted = "{0: <31}".format(lanhost)
                rdest = '{}:{}'.format(remotehost, remoteport)
                rdest_formatted = '{:30}'.format(rdest)
                if colors:
                    lanhost_colors = [
                        'dark_cyan',
                        'light_gray',
                        'red',
                        'yellow',
                        'green',
                        'cyan',
                        'magenta',
                        'light_red',
                        'light_yellow',
                        'light_green',
                        'light_cyan',
                        'light_blue',
                        'light_magenta',
                        ]
                    color_index = lanhost_index % len(lanhost_colors)
                    lanhost_color = fg(lanhost_colors[color_index])
                    dark_bg = attr('underlined')
                    color_reset = attr(0)
                    headers = {'color': lanhost_color,
                               'dark_bg': dark_bg,
                               'reset': color_reset,
                               'time': time,
                               'lanhost': lanhost_formatted,
                               'rdest': rdest_formatted}
                    if not targets:
                        print('{color} {dark_bg}{time} {lanhost} => '
                              '{rdest} {reset}'.format(**headers))
                    else:
                        for target in targets:
                            if target in lanhost.lower() or target in rdest.lower():
                                print('{color} {dark_bg}{time} {lanhost} => '
                                      '{rdest} {reset}'.format(**headers))
                else:
                    headers = {'time': time,
                               'lanhost': lanhost_formatted,
                               'rdest': rdest_formatted}
                    if not targets:
                        print('{time} {lanhost} => '
                              '{rdest}'.format(**headers))
                    else:
                        for target in targets:
                            if target in lanhost.lower() or target in rdest.lower():
                                print('{time} {lanhost} => '
                                      '{rdest}'.format(**headers))
                #force the output buffer to flush, or nothing will be printed
                #since this is reading input from a stream
                sys.stdout.flush()
    
            #sometimes stuff from syslog doesn't have what we want.
            except IndexError:
                pass
    
    except KeyboardInterrupt:
        if resolve:
            try:
                update_cache_file(lcache_file, lanhost_cache)
                update_cache_file(rcache_file, remotehost_cache)
            except:
                pass
    
        sys.exit(0)

args = parse_args(sys.argv)
f = args['filter']
d = args['resolv']
p = args['color']
main(f, d, p)
