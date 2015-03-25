**ygbc@zz:~$ cd bin/**
**ygbc@zz:~/bin$ git clone https://github.com/youvegottabecrazy/DELay.git**
Cloning into 'DELay'...
remote: Counting objects: 22, done.
remote: Compressing objects: 100% (19/19), done.
remote: Total 22 (delta 4), reused 16 (delta 1), pack-reused 0
Unpacking objects: 100% (22/22), done.
Checking connectivity... done.

ygbc@zz:~/bin$ ll
total 12
drwxrwxr-x 3 ygbc ygbc 4096 Mar 25 03:59 ./
drwxr-xr-x 3 ygbc ygbc 4096 Mar 25 03:59 ../
drwxrwxr-x 3 ygbc ygbc 4096 Mar 25 03:59 DELay/

ygbc@zz:~/bin$ cd DELay/
ygbc@zz:~/bin/DELay$ ll
total 80
drwxrwxr-x 3 ygbc ygbc  4096 Mar 25 03:59 ./
drwxrwxr-x 3 ygbc ygbc  4096 Mar 25 03:59 ../
-rw-rw-r-- 1 ygbc ygbc 35147 Mar 25 03:59 COPYING
-rwxrwxr-x 1 ygbc ygbc 20855 Mar 25 03:59 delayrm.py*
drwxrwxr-x 8 ygbc ygbc  4096 Mar 25 03:59 .git/
-rw-rw-r-- 1 ygbc ygbc  4776 Mar 25 03:59 README.md

**ygbc@zz:~/bin$ ./delayrm.py --about**
Config file written to /home/ygbc/.delayrm/.delayrmrc
********************************************************************************
What:   This is delay, or DEL-ay, an rm wrapper that delays file removal.
Why:    So you don't accidentally delete something, dummy.
Where:  Locally installed at /home/ygbc/bin/DELay/delayrm.py
        Config file should be at /home/ygbc/.delayrm/.delayrmrc
        + Trash dir: /home/ygbc/.delayrm
        + Trash dir: /mnt/some_other_disk/.delay
        Born free & GPLv3 @ https://github.com/youvegottabecrazy/DELay
"Qui tacet consentire videtur, ubi loqui debuit ac potuit." http://is.gd/eloqui
********************************************************************************

ygbc@zz:~/bin/DELay$ mount | grep " /mnt"
/dev/sdc1 on /mnt/tv750 type ext3 (rw)
/dev/sdd1 on /mnt/backup type ext3 (rw)

ygbc@zz:~/bin/DELay$ vi ~/.delayrm/.delayrmrc
ygbc@zz:~/bin/DELay$ cat ~/.delayrm/.delayrmrc
[#information]
; the main config file for DELay.py, an rm wrapper. http://github.com/youvegottabecrazy/DELay
; Option 1: this file must be located at ~/.delay/.delayrc
;            -- or --
; Option 2: if using an alternate location, $ENV{DELAY_RC} must point to this file.
; Note: settings cascade to child paths
; Note: -1 means no limit
; Note: To not use trash for a section set disabled=True.
; Note: global_disable in the "default settings" section does exactly what it says.
; Note: lists should be comma separated.

[#main]
; used globally if not overidden below
global_disable = False
trash_dir = /home/ygbc/.delayrm
ttl_hours = 48
verbose = False
rm_executable = /bin/rm

[/mnt/backup]
trash_dir = /mnt/backup/.delayrm_ygbc

[/mnt/tv750]
trash_dir = /mnt/tv750/.delayrm_ygbc

ygbc@zz:~/bin/DELay$ echo 'alias rm="~/bin/DELay/delayrm.py $@"'  >> ~/.bashrc
ygbc@zz:~/bin/DELay$ cat ~/.bashrc | grep DE
alias rm="~/bin/DELay/delayrm.py $@"
ygbc@zz:~/bin/DELay$ source ~/.bashrc

ygbc@zz:~/bin/DELay$ rm --about
********************************************************************************
What:   This is delay, or DEL-ay, an rm wrapper that delays file removal.
Why:    So you don't accidentally delete something, dummy.
Where:  Locally installed at /home/ygbc/bin/DELay/delayrm.py
        Config file should be at /home/ygbc/.delayrm/.delayrmrc
        + Trash dir: /home/ygbc/.delayrm
        + Trash dir: /mnt/tv750/.delayrm_ygbc
        + Trash dir: /mnt/backup/.delayrm_ygbc
        Born free & GPLv3 @ https://github.com/youvegottabecrazy/DELay
"Qui tacet consentire videtur, ubi loqui debuit ac potuit." http://is.gd/eloqui
********************************************************************************

ygbc@zz:~/bin/DELay$ rm --status
------------------------------------------------------------
        OVERALL: 0 mb   in 0 files
------------------------------------------------------------
details:
0 mb    in 0 files       in /home/ygbc/.delayrm
0 mb    in 0 files       in /mnt/tv750/.delayrm_ygbc
0 mb    in 0 files       in /mnt/backup/.delayrm_ygbc

ygbc@zz:~/wrk$ cd ~/music/Pink\ Floyd/Meddle/
ygbc@zz:~/music/Pink Floyd/Meddle$ rm *
mv /home/ygbc/music/Pink Floyd/Meddle/01 - One Of These Days.mp3 -> /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/01 - One Of These Days.mp3
mv /home/ygbc/music/Pink Floyd/Meddle/02 - A Pillow Of Winds.mp3 -> /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/02 - A Pillow Of Winds.mp3
mv /home/ygbc/music/Pink Floyd/Meddle/03 - Fearless.mp3 -> /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/03 - Fearless.mp3
mv /home/ygbc/music/Pink Floyd/Meddle/04 - San Tropez.mp3 -> /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/04 - San Tropez.mp3
mv /home/ygbc/music/Pink Floyd/Meddle/05 - Seamus.mp3 -> /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/05 - Seamus.mp3
mv /home/ygbc/music/Pink Floyd/Meddle/06 - Echoes.mp3 -> /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/06 - Echoes.mp3


ygbc@zz:~/music/Pink Floyd/Meddle$ rm --status
------------------------------------------------------------
        OVERALL: 37 mb  in 6 files
------------------------------------------------------------
details:
37 mb   in 6 files       in /home/ygbc/.delayrm
0 mb    in 0 files       in /mnt/tv750/.delayrm_ygbc
0 mb    in 0 files       in /mnt/backup/.delayrm_ygbc


ygbc@zz:~/music/Pink Floyd/Meddle$ rm --list
id      mb      ttl(hr) filename
--------------------------------------------------------------------------------
1       4       47      01 - One Of These Days.mp3
2       4       47      02 - A Pillow Of Winds.mp3
3       4       47      03 - Fearless.mp3
4       2       47      04 - San Tropez.mp3
5       1       47      05 - Seamus.mp3
6       18      47      06 - Echoes.mp3


ygbc@zz:/mnt/tv750/tv/Community$ cd /mnt/tv750/tv/Community/
ygbc@zz:/mnt/tv750/tv/Community$ ls -l | grep Bloo
-rw-rw-r-- 1 ygbc ygbc 228006046 Jan 11  2014 Community, All Bloopers (Season;1,2,3).mp4

ygbc@zz:/mnt/tv750/tv/Community$ rm Community\,\ All\ Bloopers\ \(Season\;1\,2\,3\).mp4
mv /mnt/tv750/tv/Community/Community, All Bloopers (Season;1,2,3).mp4 -> /mnt/tv750/.delayrm_ygbc/mnt/tv750/tv/Community/Community, All Bloopers (Season;1,2,3).mp4

ygbc@zz:/mnt/tv750/tv/Community$ rm --status
------------------------------------------------------------
        OVERALL: 254 mb in 7 files
------------------------------------------------------------
details:
37 mb   in 6 files       in /home/ygbc/.delayrm
217 mb  in 1 files       in /mnt/tv750/.delayrm_ygbc
0 mb    in 0 files       in /mnt/backup/.delayrm_ygbc


ygbc@zz:/mnt/tv750/tv/Community$ rm --list
id      mb      ttl(hr) filename
--------------------------------------------------------------------------------
1       4       47      01 - One Of These Days.mp3
2       4       47      02 - A Pillow Of Winds.mp3
3       4       47      03 - Fearless.mp3
4       2       47      04 - San Tropez.mp3
5       1       47      05 - Seamus.mp3
6       18      47      06 - Echoes.mp3
7       217     47      Community, All Bloopers (Season;1,2,3).mp4

ygbc@zz:/mnt/tv750/tv/Community$ rm --list --full
id      mb      ttl(hr) filename
--------------------------------------------------------------------------------
1       4       47      /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/01 - One Of These Days.mp3
2       4       47      /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/02 - A Pillow Of Winds.mp3
3       4       47      /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/03 - Fearless.mp3
4       2       47      /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/04 - San Tropez.mp3
5       1       47      /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/05 - Seamus.mp3
6       18      47      /home/ygbc/.delayrm/home/ygbc/music/Pink Floyd/Meddle/06 - Echoes.mp3
7       217     47      /mnt/tv750/.delayrm_ygbc/mnt/tv750/tv/Community/Community, All Bloopers (Season;1,2,3).mp4

ygbc@zz:/mnt/tv750/tv/Community$ rm --restore 7
/mnt/tv750/.delayrm_ygbc/mnt/tv750/tv/Community/Community, All Bloopers (Season;1,2,3).mp4 -> /mnt/tv750/tv/Community/Community, All Bloopers (Season;1,2,3).mp4

ygbc@zz:/mnt/tv750/tv/Community$ ls -l | grep Blo
-rw-rw-r-- 1 ygbc ygbc 228006046 Jan 11  2014 Community, All Bloopers (Season;1,2,3).mp4
ygbc@zz:/mnt/tv750/tv/Community$ rm --status
------------------------------------------------------------
        OVERALL: 37 mb  in 6 files
------------------------------------------------------------
details:
37 mb   in 6 files       in /home/ygbc/.delayrm
0 mb    in 0 files       in /mnt/tv750/.delayrm_ygbc
0 mb    in 0 files       in /mnt/backup/.delayrm_ygbc

ygbc@zz:/mnt/tv750/tv/Community$ rm --list
id      mb      ttl(hr) filename
--------------------------------------------------------------------------------
1       4       47      01 - One Of These Days.mp3
2       4       47      02 - A Pillow Of Winds.mp3
3       4       47      03 - Fearless.mp3
4       2       47      04 - San Tropez.mp3
5       1       47      05 - Seamus.mp3
6       18      47      06 - Echoes.mp3

ygbc@zz:~/wrk$ cd ~/wrk/
ygbc@zz:~/wrk$ echo "yo" >> foo
ygbc@zz:~/wrk$ rm foo
mv /home/ygbc/wrk/foo -> /home/ygbc/.delayrm/home/ygbc/wrk/foo
ygbc@zz:~/wrk$ echo "yoyo" >> foo
ygbc@zz:~/wrk$ rm foo
mv /home/ygbc/wrk/foo -> /home/ygbc/.delayrm/home/ygbc/wrk/foo.1427275526.73
ygbc@zz:~/wrk$ rm --list
id      mb      ttl(hr) filename
--------------------------------------------------------------------------------
1       4       47      01 - One Of These Days.mp3
2       4       47      02 - A Pillow Of Winds.mp3
3       4       47      03 - Fearless.mp3
4       2       47      04 - San Tropez.mp3
5       1       47      05 - Seamus.mp3
6       18      47      06 - Echoes.mp3
7       0       47      foo
8       0       47      foo.1427275526.73

ygbc@zz:~/wrk$ rm --restore 7
/home/ygbc/.delayrm/home/ygbc/wrk/foo -> /home/ygbc/wrk/foo
ygbc@zz:~/wrk$ cat foo
yo

ygbc@zz:~/wrk$ rm --purge
purging trash dir
ygbc@zz:~/wrk$ rm --status
------------------------------------------------------------
        OVERALL: 0 mb   in 0 files
------------------------------------------------------------
details:
0 mb    in 0 files       in /home/ygbc/.delayrm
0 mb    in 0 files       in /mnt/tv750/.delayrm_ygbc
0 mb    in 0 files       in /mnt/backup/.delayrm_ygbc

ygbc@zz:~/wrk$ rm --list
id      mb      ttl(hr) filename
--------------------------------------------------------------------------------
ygbc@zz:~/wrk$

