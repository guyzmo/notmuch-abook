" Address book management

" Init link to Addressbook database
fun! InitAddressBook()
    py import vim
    py import sys
    py import os.path
    py sys.path = ["/home/guyzmo/Workspace/Vilya/build/notmuch_addresses"] + sys.path
    py import notmuch_addresses
    py cfg = notmuch_addresses.NotMuchConfig(os.path.expanduser("~/.notmuch-config"))
    py db = notmuch_addresses.SQLiteStorage(cfg) if cfg.get("addressbook", "backend") == "sqlite3" else None
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
    vim.command('echo "No backend found."')
EOP
            return []
        endif
    endif
endfun

au FileType mail call InitAddressBook()
au FileType mail set completefunc=CompleteAddressBook

augroup nm_ab
    au!
    au FileType mail exe 'nmap '.s:highligh.' :call HighLightenment()<CR>'
    au FileType mail exe 'nmap '.s:cuthere.'  O'.s:CutHereBeg.'<CR>'.s:CutHereEnd.'<ESC>^O'
    au FileType mail exe 'vmap '.s:cuthere.'  :s/\(\_.*\)/'.s:CutHereBeg.'\1'.s:CutHereEnd.'<CR>'
    au FileType mail inoremap <C-Space> <C-x><C-u>
    au FileType mail inoremap <C-@> <C-Space>
augroup END
