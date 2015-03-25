#!/usr/bin/env python
# ------------------------------------------------------------------------------
#    Copyright (C) 2015  youvegottabecrazy1@gmail.com
#    https://github.com/youvegottabecrazy/DELay
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------
#-- imports
import time, sys, os, shutil, sqlite3, subprocess
from optparse import OptionParser

# different module name for python >= 3
try:
    import ConfigParser
except ImportError as e:
    import configparser as ConfigParser
    
__version__ = "1.0"
script_path, script_filename = os.path.split(os.path.realpath(sys.argv[0]))
if os.getenv("DELAYRMRC"): config_file = os.getenv("DELAYRMRC")
else: config_file = os.path.join(os.getenv("HOME", '~'), ".delayrm", '.delayrmrc')
db = None
options = None
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) 

def vprint(msg):
    if get_setting('verbose'):
        print("%s" % (msg))

def init():
    read_config()
    if not os.path.isdir(get_setting('trash_dir')):
        print("Created directory %s" % get_setting('trash_dir'))
        os.mkdir(get_setting('trash_dir'))
    global db
    db = sqlite3.connect(os.path.join(get_setting('trash_dir'), '.delayrm.sqlite3'))
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, trash_dir TEXT, original_location TEXT, trash_location TEXT, removed_ts REAL, purge_ts REAL, type TEXT, bytes INTEGER)")
    except Exception as e:
        print("error in db_init() %s " % e)

def move_file(fn, filetype, **opts):
    (path, filename) = fn.rsplit("/", 1)
    dest_dir =  get_setting('trash_dir', fn) + path
    if opts['interactive'] and not opts['force']:
        a = raw_input("Move '%s' to trash? (y/N)> " % fn)
        if a not in ['y', 'Y', 'yes']:
            print("%s Not removed" % fn)
            return;
    if not os.path.isdir(dest_dir): os.makedirs(dest_dir)
    if os.path.exists(os.path.join(dest_dir, filename)):
        filename = filename + '.' + str(time.time())
    new_file = os.path.join(dest_dir, filename)
    mybytes = os.path.getsize(fn)

    if opts['stash'] and filetype == 'dir':
        print("cp %s -> %s" % (fn, new_file))
        shutil.copytree(fn, new_file)
    elif opts['stash']:
        print("cp %s -> %s" % (fn, new_file))
        shutil.copy(fn, new_file)
    else: 
        print("mv %s -> %s" % (fn, new_file))
        shutil.move(fn, new_file)

    cur = db.cursor()
    if filetype != 'dir':
        purge_ts = time.time() + get_setting('ttl_hours', fn) * 3600 
        trash_dir = get_setting('trash_dir', fn)
        cur.execute("INSERT INTO files(trash_dir, original_location, trash_location, removed_ts, purge_ts, type, bytes) VALUES (?,?,?,?,?,?,?)", (trash_dir, fn, new_file, time.time(), purge_ts , filetype, mybytes))
    else:
        for root, dirs, files in os.walk(new_file):
            for name in files:
                mybytes = os.path.getsize(os.path.join(root,name))
                mytype = 'file'
                purge_ts = time.time() + get_setting('ttl_hours', fn) * 3600 
                trash_dir = get_setting('trash_dir', fn)
                if os.path.islink(fn): mytype = 'link'
                cur.execute("INSERT INTO files(trash_dir, original_location, trash_location, removed_ts, purge_ts, type, bytes) VALUES (?,?,?,?,?,?,?)", (trash_dir, os.path.join(fn, name), os.path.join(root, name), time.time(), purge_ts, mytype, mybytes))


def cleanup(background=False, purge=False, explicit=False):
    cur = db.cursor()
    if purge: cur.execute("SELECT * FROM files ORDER BY type DESC, LENGTH(trash_location) DESC")
    else: cur.execute("SELECT * FROM files WHERE purge_ts < ? ORDER BY type DESC, LENGTH(trash_location) DESC", (time.time(),) )
    trashdirs = []
    for r in cur.fetchall():
        trashdirs.append(r['trash_dir'])
        if os.path.lexists(r['trash_location']):
            if r['type'] != 'dir':
                if explicit and not background: print("unlinking %s" % r['trash_location'])
                os.unlink(r['trash_location'])
        
        if explicit and not background: print("deleting from db: %s" % r['trash_location'])
        cur.execute("DELETE FROM files WHERE id = ?", (r['id'],))
    for trashdir in trashdirs:
        for root, dirs, files in os.walk(trashdir, topdown=False):
            for dir in dirs:
                rmdir_if_empty(os.path.join(root, dir), explicit=explicit, background=background)
    if background:
        db.commit()
        os._exit(0)

def rmdir_if_empty(dir, explicit=False, background=False):
    try: 
        os.rmdir (dir)
        if explicit and not background: print("rmdir %s" % dir)
    except OSError as e:
        if e.errno == 39: return False  # dir not empty
        else:  print("OSError exception while removing directory: %s" % e)
    except Exception as e:
        print("Exception while removing directory: %s" % e)
 
def get_setting(setting_name, path=None, include_source = False):
    s = None
    src = None
    if setting_name in options['default']:
        s = options['default'][setting_name]
        src = options['default']['source']
    if path:
        parts = path.split('/')
        path = '/'
        for part in parts:
            path = os.path.join(path, part)
            if path in options:
                if setting_name in options[path]:
                    s = options[path][setting_name]
                    src = options[path]['source']
            if path not in options['rcfiles']:
                options['rcfiles'][path] = dict()
                if os.path.exists(os.path.join(path, '.delayrmrc')):
                    vprint("found config file at %s" % path)
                    c = ConfigParser.ConfigParser()
                    c.read(os.path.join(path, '.delayrc'))
                    options['rcfiles'][path]['source'] = os.path.join(path, '.delayrc')
                    for opt in c.options('#dir'):
                        options['rcfiles'][path][opt] = get_config_item('#dir', opt, c)
            if setting_name in options['rcfiles'][path]:
                s = options['rcfiles'][path][setting_name]
                src = options['rcfiles'][path]['source']
    if include_source: return [s, src]
    return s

def restore_file(id):
    cur = db.cursor()
    r = cur.execute("SELECT * FROM files WHERE id = ?", (id,)).fetchone()
    if not r: print("File with id %s not found." % id)
    else:
        d = r['original_location'].rsplit('/', 1)[0]
        if not os.path.isdir(d): os.makedirs(d)
        if os.path.isfile(r['original_location']):
            a = raw_input("%s exists.  Overwrite? (y/N)> " % r['original_location'])
            if a not in ['y', 'Y', 'yes']:
                print("%s Not restored" % r['original_location'])
                return;
        shutil.move(r['trash_location'], r['original_location'])
        print("%s -> %s" % (r['trash_location'], r['original_location']))
        cur.execute("DELETE FROM files WHERE id = ?", (id,))


def create_local_config(path):
    fn = os.path.join(path, '.delayrc')
    if os.path.isfile(fn):
        print("Error: %s already exists."  % fn)
        sys.exit()

    config = ConfigParser.RawConfigParser(allow_no_value = True)
    config.optionxform = str
    config.add_section('#information')
    config.set('#information', '; a local config file for use with DELay, an rm wrapper. http://github.com/youvegottabecrazy/DELay')
    config.set('#information', '; the settings here will cascade to all subdirs, where they can be overridden if desired.')
    config.set('#information', '; the settings pre-populated (& commented out) are those calculated to apply to this directory.')
    config.set('#information', '; created at %s.' % time.time())
    config.add_section('#dir')
    config.set('#dir', '; trash_dir', get_setting('trash_dir', path))
    config.set('#dir', '; ttl_hours', get_setting('ttl_hours', path))
    config.set('#dir', '; disabled', get_setting('disabled', path) or False)

    with open(fn, 'wb') as cf:
        config.write(cf)
    print("Local config file written to %s" % fn)
 
   
def create_config():
    config = ConfigParser.RawConfigParser(allow_no_value = True)
    config.optionxform = str
    config.add_section('#information')
    config.set('#information', '; the main config file for DELay.py, an rm wrapper. http://github.com/youvegottabecrazy/DELay')
    config.set('#information', '; Option 1: this file must be located at ~/.delay/.delayrc')
    config.set('#information', ';            -- or -- ')
    config.set('#information', '; Option 2: if using an alternate location, $ENV{DELAY_RC} must point to this file.')
    config.set('#information', '; Note: settings cascade to child paths')
    config.set('#information', '; Note: -1 means no limit')
    config.set('#information', '; Note: To not use trash for a section set disabled=True.')
    config.set('#information', '; Note: global_disable in the "default settings" section does exactly what it says.')
    config.set('#information', '; Note: lists should be comma separated.')
    
    config.add_section('#main')
    config.set('#main', '; used globally if not overidden below')
    config.set('#main', 'global_disable', 'False')
    config.set('#main', 'trash_dir', config_file.rsplit('/', 1)[0])
    config.set('#main', 'ttl_hours', '48')
    config.set('#main', 'verbose', 'False')
    config.set('#main', 'rm_executable', '/bin/rm')

    config.add_section('/mnt/some_other_disk')
    config.set('/mnt/some_other_disk', '; use a different trash dir for files on this other volume to avoid long cp')
    config.set('/mnt/some_other_disk', "; cuz ain't no one got time for that")
    config.set('/mnt/some_other_disk', 'trash_dir', '/mnt/some_other_disk/.delay')
    config.set('/mnt/some_other_disk', 'ttl_hours', '72')

    config.add_section('/home/you/definitely_not_porn')
    config.set('/home/you/definitely_not_porn', '; remove files in this dir and those beneath immediately.')
    config.set('/home/you/definitely_not_porn', 'disabled', 'True')
    
    if not os.path.isdir(config_file.rsplit('/',1)[0]):
        os.mkdir(config_file.rsplit('/',1)[0])

    with open(config_file, 'wb') as cf:
        config.write(cf)
    print("Config file written to %s" % config_file)


def read_config():
    if not os.path.isfile(config_file): create_config()
    global options
    options = dict()
    options['default'] = dict()
    options['rcfiles'] = dict()
    c = ConfigParser.ConfigParser()
    c.read(config_file)
    options['default']['source'] =  "%s [%s]" % (config_file, '#main')
    options['default']['global_disable'] =  c.getboolean("#main", "global_disable")
    options['default']['trash_dir'] =  c.get("#main", "trash_dir")
    options['default']['ttl_hours'] =  c.getint("#main", "ttl_hours")
    options['default']['verbose'] =  c.getboolean("#main", "verbose")
    options['default']['rm_executable'] =  c.get("#main", "rm_executable")
    
    for s in c.sections():
        if not s.startswith("#"):
            options[s] = dict()
            options[s]['source'] =  "%s [%s]" % (config_file, s)
            for opt in c.options(s):
                options[s][opt] = get_config_item(s, opt, c)

def get_config_item(section, name, cp):
    type_bool = ['disabled']
    type_int = ['ttl_hours', 'max_filesize']
    if name in type_bool: return cp.getboolean(section, name)
    elif name in type_int: return  cp.getint(section, name)
    else: return cp.get(section, name)

def get_trash_dirs():
    mydirs = []
    for x in options:
        if 'trash_dir' in options[x] and options[x]['trash_dir'] not in mydirs:
            mydirs.append(options[x]['trash_dir'])
    cur = db.cursor()
    cur.execute("SELECT DISTINCT (trash_dir) FROM files")
    for r in cur.fetchall():
        if r['trash_dir'] not in mydirs:
            mydirs.append(r['trash_dir'])
    return mydirs

def exit(nocleanup=False):
    db.commit()
    if not nocleanup:
        if not os.fork(): cleanup(background=True)
    sys.exit()

#-- main
"""
supported options from rm: -f -i
note: using -f on a dir is equivalent to rm -Rf.  More or less.

non-supported options from rm:
-I
--one-file-system
--no-preserve-root
--preserve-root
-r, -R, --recursive
-d, --dir
-v, --verbose
--help display this help and exit
--version

"""
if '__main__' == __name__:
    init()
    parser = OptionParser()
    parser.add_option("-f", action="store_true", dest="force", default=False,
        help="Force removal. allows removal of directories. overrides -i.  This is more or less equivalent to rm -Rf. ")
    parser.add_option("-i", action="store_true", dest="interactive", default=False,
        help="Interactive. \"Are you sure? (y/N)> \" " )
    parser.add_option("--about", action="store_true", dest="about", default=False,
        help="Show information about this script.")
    parser.add_option("--status", action="store_true", dest="status", default=False,
        help="Show statistics on the trash directories" )
    parser.add_option("--paths", action="store_true", dest="paths", default=False,
        help="Information about the paths specified in the config file. Probably gonna remove this." )
    parser.add_option("--list", action="store_true", dest="list_files", default=False,
        help="List trash dir contents. Combine with --full for full paths." )
    parser.add_option("--full", action="store_true", dest="full_display", default=False,
        help="Show full paths.  Use with --list option" )
    parser.add_option("--explicit", action="store_true", dest="explicit", default=False,
        help="Verbose explanations." )
    parser.add_option("--restore", action="store_true", dest="restore", default=False,
        help="Restore (undelete) a file to its original location. Accepts space separated id # list. Will prompt if file exists.  id numbers are available via --list." )
    parser.add_option("--purge", action="store_true", dest="purge", default=False,
        help ="Purge all trash directories immediately." )
    parser.add_option("--maintenance", action="store_true", dest="maintenance", default=False,
        help = "Maintenance operations. Don't remove a file, just expunge timed-out files. You may want to schedule this command periodically if you're not an rm enthusiast." )
    parser.add_option("--real", action="store_true", dest="real_rm", default=False,
        help = "Real rm.  Will pass the exact command string (less the --real flag) along to the system's rm command." )
    parser.add_option("--explain", action="store_true", dest="explain", default=False,
        help = "Explain how <filename> will be handled if removed, also listing the source of each rule." )
    parser.add_option("--stash", action="store_true", dest="stash", default=False,
        help = "Don't delete the file, but instead copy it to the trash dir." )
    parser.add_option("--create_local_rc", action="store_true", dest="create_local_rc", default=False,
        help = "Create a local .delayrc file in the current directory")
    (cloptions, files) = parser.parse_args()

    if cloptions.about:
        print("*" * 80)
        print("What:   This is delay, or DEL-ay, an rm wrapper that delays file removal.")
        print("Why:    So you don't accidentally delete something, dummy.")
        print("Where:  Locally installed at %s" % os.path.realpath(sys.argv[0]))
        print("        Config file should be at %s" % config_file)
        for d in get_trash_dirs():
            print("        + Trash dir: %s" % d)
        print("        Born free & GPLv3 @ https://github.com/youvegottabecrazy/DELay")
        print("\"Qui tacet consentire videtur, ubi loqui debuit ac potuit.\" http://is.gd/eloqui")
        print("*" * 80)
        exit()

    if cloptions.create_local_rc:
        create_local_config(os.getcwd())
        exit()

    if cloptions.explain:
        fn = os.path.abspath(files[0])
        print("Full Path: %s" % fn)
        if get_setting("global_disable"):
            print("DELay is globally disabled.  All commands passed to %s" % get_setting("rm_executable"))
            exit(nocleanup=True)
        else:
            s, src = get_setting("disabled", path=fn, include_source=True)
            if s:
                print("Disabled. (from: %s)" % src)
            else: 
                s, src = get_setting('trash_dir', path=fn, include_source=True)
                print("Trash Dir: %s. (from: %s)" % (s, src))
                s, src = get_setting('ttl_hours', path=fn, include_source=True)
                print("TTL (hours): %s. (from: %s)" % (s, src))
            exit()       

    if cloptions.status:
        cur = db.cursor()
        num_files = cur.execute("SELECT COUNT(*) as c from files").fetchone()[0]
        size = cur.execute("SELECT COALESCE(SUM(bytes),0) from files").fetchone()[0]
        print('-' * 60)
        print("\tOVERALL: %s mb\tin %s files" % (size /1024/1024, num_files))
        print('-' * 60)
        print("details:")
        mydirs = get_trash_dirs()
        for x in mydirs:
            num_files = cur.execute("SELECT COUNT(*) as c from files where trash_dir = ?", (x,)).fetchone()[0]
            size = cur.execute("SELECT COALESCE(SUM(bytes),0) from files where trash_dir = ?", (x,)).fetchone()[0]
            print("%s mb\tin %s files\t in %s" % (int(size /1024/1024), num_files, x))
        print()
        exit()

    if cloptions.paths:
        print("-" * 60)
        print("\tDefined paths")
        print("-" * 60)
        for x in options:
            print("%s hours \t%s" % (get_setting('ttl_hours', x), x))
        exit()

    if cloptions.list_files:
        cur = db.cursor()
        cur.execute("SELECT * from files ORDER BY trash_dir")
        print("id\tmb\tttl(hr)\tfilename")
        print('-' * 80)
        for r in cur.fetchall():
            fn = r['trash_location']
            if not cloptions.full_display:
                fn = fn.rsplit('/', 1)[1]
            until_delete = int((r['purge_ts'] - time.time())/3600)
            print("%s\t%s\t%s\t%s" % (r['id'], int(r['bytes']/1024/1024), until_delete, fn))
        exit()       

    if cloptions.restore:
        if files:
            for id in files:
                restore_file(id)
        else: print("Specify the id's of the files you want to restore. Space separated list." )
        db.commit()
        exit()

    if get_setting("global_disable"):
        vprint("DELay is globally disabled, passthrough to rm")
        args = []
        args.append(get_setting("rm_executable"))
        args.extend(sys.argv[1:])
        subprocess.call(args)
        exit(nocleanup=True)

    if cloptions.maintenance:
        print("Performing maintenance operations in background.")
        exit()

    if cloptions.purge:
        print("purging trash dir")
        cleanup(purge=cloptions.purge, explicit=cloptions.explicit)
        db.commit()
        exit(nocleanup=True)

    if cloptions.real_rm:
        args = []
        args.append(get_setting("rm_executable"))
        for arg in sys.argv[1:]:
            if arg != '--real':
                args.append(arg)
        subprocess.call(args)
        exit()

    if len(files):
        for f in files:
            fn = os.path.abspath(f)
            if fn.startswith(get_setting('trash_dir')):
                vprint("real rm on file in trash dir: %s" % fn)
                os.unlink(fn)
                cur = db.cursor()
                cur.execute("DELETE FROM files WHERE trash_location = ?", (fn,))
            
            elif os.path.islink(fn):
                vprint("symlink: %s"  % fn )
                move_file(fn, 'link', **vars(cloptions))

            elif os.path.isdir(fn):
                if cloptions.force: move_file(fn, 'dir', **vars(cloptions))
                else: print("%s: is directory. Use -f to force." % fn)
        
            elif os.path.isfile(fn):
                vprint("file: %s" % fn)
                move_file(fn, 'file', **vars(cloptions))
            
            else:
                vprint("not a file: %s"  % fn)
                print("%s: cannot remove '%s': No such file or directory" % (os.path.join(script_path, script_filename), fn))
    else:
        print("%s: missing operand." % script_filename)
        print("try rm --help for more information")
    exit()
