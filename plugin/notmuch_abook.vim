" Address book management


if exists("g:notmuch_addressbook")
    finish
else
    let g:notmuch_addressbook = 1
endif

if !has('python')
    echoerr "Error: Notmuch Addressbook plugin requires Vim to be compiled with +python"
    finish
endif

" Init link to Addressbook database
fun! InitAddressBook()
python<<EOS
import vim
import sys
import os.path
curpath = vim.eval("getcwd()")
libpath = os.path.join(os.path.dirname(os.path.dirname(vim.eval("expand('<sfile>:p')"))), 'pylibs')
sys.path = [os.path.dirname(libpath), libpath, curpath] + sys.path

import notmuch_addresses
cfg = notmuch_addresses.NotMuchConfig(os.path.expanduser("~/.notmuch-config"))
db = notmuch_addresses.SQLiteStorage(cfg) if cfg.get("addressbook", "backend") == "sqlite3" else None
EOS
endfun

" Addressbook completion
fun! CompleteAddressBook(findstart, base)
    let curline = getline('.')
    if curline =~ '^From: ' || curline =~ '^To: ' || curline =~ 'Cc: ' || curline =~ 'Bcc: '
        if a:findstart
        " locate the start of the word
            let start = col('.') - 1
            while start > 0 && curline[start - 2] != ":"
                let start -= 1
            endwhile
            let failed = append(line('.'), a:base[:-2])
            return start
        else
python << EOP
encoding = vim.eval("&encoding")
if db:
    for addr in db.lookup(vim.eval('a:base')): 
        if addr[0] == "":
            addr = addr[1]
        else:
            addr = addr[0]+" <"+addr[1]+">"
        vim.command(('call complete_add("%s")' % addr.replace('"', "")).encode( encoding ))
        vim.command('call complete_check()')
else:
    vim.command('echoerr "No backend found."')
EOP
            return []
        endif
    endif
endfun

au FileType mail call InitAddressBook()
au FileType mail set completefunc=CompleteAddressBook

