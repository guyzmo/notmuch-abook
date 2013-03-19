Notmuch Addressbook manager for vim
===================================

DEPENDENCES
-----------

* notmuch with python bindings

INSTALL
-------

Use vundle to install this script, add to your vimrc:

```
Bundle "guyzmo/notmuch-abook"
```

for convenience, you can create a symlink to your bin directory:
```
ln -s $HOME/.vim/bundle/notmuch-abook/pylibs/notmuch_addresses.py ~/bin/notmuch-abook
```

CONFIGURATION
-------------

In your favorite mail filter program, add a rule such as (for procmail), so all new mail will be parsed:

```
:0 Wh
| python $HOME/.vim/bundle/notmuch-abook/pylibs/notmuch_addresses.py update
```

USAGE
-----

For the first time, you shall launch the script as follows to create the addresses database:

```
python $HOME/.vim/bundle/notmuch-abook/pylibs/notmuch_addresses.py create
```

and then, to lookup an address, either you use the vimscript to complete (<c-x><c-u>) the name in a header field,
or you can call it from commandline:

```
python $HOME/.vim/bundle/notmuch-abook/pylibs/notmuch_addresses.py lookup Guyz
```

the script will match any word beginning with the pattern in the name and address parts of the entry.

LICENSE
-------

(c)2013, Bernard Guyzmo Pratz, guyzmo at m0g dot net

Even though it is a WTFPL license, if you do improve that code, it's great, but if you
don't tell me about that, you're just a moron. And if you like that code, you have the
right to buy me a beer, thank me, or [flattr](http://flattr.com/profile/guyzmo)/[gittip](http://gittip.com/guyzmo) me.

```
DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
Version 2, December 2004 

Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 

Everyone is permitted to copy and distribute verbatim or modified 
copies of this license document, and changing it is allowed as long 
as the name is changed. 

DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 

0. You just DO WHAT THE FUCK YOU WANT TO.
```

