#DELay

A replacement for rm that moves files to a trash directory instead of removing them. 


* Files are auto-purged periodically according to the ttl_hours setting.

* The original directory structure is recreated in the trash directory on demand. When a particular directory is no longer needed, it is auto-pruned upon file removal.

* Clobbers: In the case of an existing filename, a timestamp is appended to the new version.

* Configurable on a per-directory basis, with settings cascading to child dirs.  

* Supports multiple trash directories.  To speed things along, you may want to create a different trash directory on each physical device.

* Supports restoring removed files. 

* Keeps a small sqlite3 db in the trash dir.
    

## Installation

1.  Clone this repo, or download the delayrm.py file.

2.  The default trash dir is $HOME/.delayrm. $HOME/.delayrm/.delayrmrc will be created on first run.  If you'd like to use a different location, set ENV{DELAYRMRC} to the full path of the .delayrmrc file.  Run the script once to generate the default rc file. 

3.  Edit the generated .delayrc file as desired.

4. It's best to use the script via shell alias.  If using bash, add the following line to .bashrc:

        alias rm="/<location>/delayrm.py $@"

    Pro-tip: If using bash, prepending a backslash will ignore the alias. e.g. \rm filename

5. When removing a file, DELay will first load the main .delayrmrc file, and will then load all .delayrmrc files found in the rm'ed file's path.  The settings found in each local .delayrmrc file will cascade to all sub-directories.  To generate a local .delayrmrc file in the current directory, use the --create_local_rc option.

## Options

    Switches (from rm):   
        -f (force) (note: will allow directory removal.)
        -i (interactive)
 
    Switches (unique to DELay):
        --help              show this dialog.
        --status            show status of trash directories.
        --paths             show options for each path specified in config file
        --list              list all deleted files
        --full              use with list for full path display
        --restore           un-delete an item by id number
        --explicit          detail each operation as it happens.
        --purge             clear the entire trash dir & db immediately.
        --maintenance       don't remove a file, just clear expired files.
        --real              do a "real" rm. pass the command line on to the system's rm command
        --explain           show the rules that will be applied to a particular file
        --stash             don't delete the file, but make a copy of it.
        --create_local_rc   Create a local .delayrc file in the current directory
        --about             about the script
 

##Maintenance

Maintenence (clearing trash dir of expired files) is done when rm is called. A job forks into the background so you don't have to deal with a delay.  If you use rm infrequently you may want to schedule a periodic run of rm --maintenance.

  
##Rules parsing

An example of how the rules parsing works.

        1.  Start with everything specified in [#main] section of main .delayrmrc file
        2.  for each dir in the path, starting with '/':
            a.  apply any rules found in matching [/dir/] section of main .delayrmrc file
            b.  apply any rules found in ${path}/.delayrmrc file
 
        Example, as user "syd":
                  /home/syd/.delayrm/.delayrmrc contains:  
                        [default settings]
                        ttl_hours = 10
                        trash_dir = /home/syd/.delayrm
                        
                        [/home/music]
                        ttl_hours = 50
                        trash_dir = /tmp/garbage
 
                  /home/music/pinkfloyd/.delayrmrc contains:  
                        trash_dir = /home/music/.pinkfloydtrash
  
                  /home/music/pinkfloyd/wywh/.delayrmrc contains:  
                        disabled = True
 
       Calculated rules for rm /home/syd/royharper.txt:
            ttl_hours = 10
            trash_dir = /home/syd/.delayrm
 
       Calculated rules for rm /home/music/whatdoesthefoxsay.mp4:
            ttl_hours /= 50
            trash_dir = /tmp/garbage
 
       Calculated rules for rm /home/music/pinkfloyd/dogs.mp4:
            ttl_hours  = 50
            trash_dir = /home/music/.pinkfloydtrash
         
       Calculated rules for rm /home/music/pinkfloyd/meddle/echoes.mp4:
            ttl_hours = 50
            trash_dir = /home/music/.pinkfloydtrash
 
       Calculated rules for rm /home/music/pinkfloyd/wywh/have_a_cigar.mp4:
            disabled = True, so command passed directly to /bin/rm
            
