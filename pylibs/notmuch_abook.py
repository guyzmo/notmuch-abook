#!/usr/bin/env python

## Filename: notmuch_addresses.py
## Copyright (C) 2010-11 Jesse Rosenthal
## Author: Jesse Rosenthal <jrosenthal@jhu.edu>

## This file is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 2, or (at your
## option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## NOTE: This script requires the notmuch python bindings.
"""
Notmuch Addressbook utility

Usage:
  notmuch_abook.py [-hv] [-c CONFIG] create
  notmuch_abook.py [-hv] [-c CONFIG] update
  notmuch_abook.py [-hv] [-c CONFIG] lookup [--output (abook | email)] <match>
  notmuch_abook.py [-hv] [-c CONFIG] changename <address> <name>

Options:
  -h --help                   Show this help message and exit
  -v --verbose                Show full stacktraces on error
  -c CONFIG, --config CONFIG  Path to notmuch configuration file
  -o OUTPUT, --output OUTPUT  Format for address output [default: email]

Commands:

  create              Create a new database.
  update              Update the database with a new email (on stdin).
  lookup <match>      Lookup an address in the database.  The match can be
                      an email address or part of a name.
  changename <address> <name>
                      Change the name associated with an email address.

Valid values for the OUTPUT are:

* abook - Give output in abook compatible format so it can be easily parsed
          by other programs.  The format is EMAIL<Tab>NAME
* email - Give output in a format that can be used when composing an email.
          So NAME <EMAIL>


The database to use is set in the notmuch config file.
"""

import os.path
import sys
import docopt
import notmuch
import sqlite3
import ConfigParser
import email.parser
import email.utils


class NotMuchConfig(object):
    def __init__(self, config_file):
        if config_file is None:
            config_file = os.environ.get('NOTMUCH_CONFIG', '~/.notmuch_config')

        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.expanduser(config_file))

    def get(self, section, key):
        return self.config.get(section, key)


class MailParser(object):
    def __init__(self):
        self.addresses = dict()

    def parse_mail(self, m):
        """
        function used to extract headers from a email.message or
        notmuch.message email object yields address tuples
        """
        addrs = []
        if isinstance(m, email.message.Message):
            get_header = m.get
        else:
            get_header = m.get_header
        for h in ('to', 'from', 'cc', 'bcc'):
            v = get_header(h)
            if v:
                addrs.append(v)
        for addr in email.utils.getaddresses(addrs):
            name = addr[0].strip('; ')
            address = addr[1].lower().strip(';\'" ')
            if (address and address not in self.addresses):
                self.addresses[address] = name
                yield (name, address)


class NotmuchAddressGetter(object):
    """Get all addresses from notmuch, based on information information from
    the user's $HOME/.notmuch-config file.
    """

    def __init__(self, config):
        """
        """
        self.db_path = config.get("database", "path")
        self._mp = MailParser()

    def _get_all_messages(self):
        notmuch_db = notmuch.Database(self.db_path)
        query = notmuch.Query(notmuch_db, "NOT tag:junk AND NOT folder:drafts AND NOT tag:deleted")
        return query.search_messages()

    def generate(self):
        msgs = self._get_all_messages()
        for m in msgs:
            for addr in self._mp.parse_mail(m):
                yield addr


class SQLiteStorage():
    """SQL Storage backend"""
    def __init__(self, config):
        self.__path = config.get("addressbook", "path")

    def connect(self):
        """
        creates a new connection to the database and returns a cursor
        throws an error if the database does not exists
        """
        if not os.path.exists(self.__path):
            raise IOError("Database '%s' does not exists" % (self.__path,))
        return sqlite3.connect(self.__path, isolation_level="DEFERRED")

    def create(self):
        """
        create a new database
        """
        if os.path.exists(self.__path):
            raise IOError("Can't create database at '%s'. File exists." %
                          (self.__path,))
        else:
            with sqlite3.connect(self.__path) as c:
                cur = c.cursor()
                cur.execute("CREATE VIRTUAL TABLE AddressBook USING fts4(Name, Address)")
                cur.execute("CREATE VIEW AddressBookView AS SELECT * FROM addressbook")
                cur.executescript(
                    "CREATE TRIGGER insert_into_ab " +
                    "INSTEAD OF INSERT ON AddressBookView " +
                    "BEGIN" +
                    " SELECT RAISE(ABORT, 'column name is not unique')" +
                    "   FROM addressbook" +
                    "  WHERE address = new.address;" +
                    " INSERT INTO addressbook VALUES(new.name, new.address);" +
                    "END;")

    def init(self, gen):
        """
        populates the database with all addresses from address book
        """
        n = 0
        with self.connect() as cur:
            cur.execute("PRAGMA synchronous = OFF")
            for elt in gen():
                try:
                    cur.execute("INSERT INTO AddressBookView VALUES(?,?)", elt)
                    n += 1
                except sqlite3.IntegrityError:
                    pass
            cur.commit()
        return n

    def update(self, addr):
        """
        updates the database with a new mail address tuple
        """
        try:
            with self.connect() as c:
                cur = c.cursor()
                cur.execute("INSERT INTO AddressBookView VALUES(?,?)", addr)
                return True
        except sqlite3.IntegrityError:
            return False

    def lookup(self, match):
        """
        lookup an address from the given match in database
        """
        with self.connect() as c:
            cur = c.cursor()
            for res in cur.execute(
                """SELECT * FROM AddressBook WHERE AddressBook MATCH '"%s*"'"""
                    % match).fetchall():
                yield res

    def change_name(self, address, name):
        """
        Change the name associated with an email address
        """
        with self.connect() as c:
            cur = c.cursor()
            cur.execute(
                "UPDATE AddressBook SET name = '%s' WHERE address = '%s'" %
                (name, address))
            return True


def format_address(address, output_format):
    if output_format == 'abook':
        return "{address}\t{name}".format(address)
    elif output_format == 'email':
        if address['name']:
            return "{name} <{address}>".format(address)
        else:
            return address['address']


def print_address_list(address_list, output_format):
    for address in address_list:
        print format_address(address, output_format)


def create_act(db, cf):
    db.create()
    nm_mailgetter = NotmuchAddressGetter(cf)
    n = db.init(nm_mailgetter.generate)
    print "added %d addresses" % n


def update_act(db, verbose):
    n = 0
    m = email.message_from_file(sys.stdin)
    for addr in MailParser().parse_mail(m):
        if db.update(addr):
            n += 1
    if verbose:
        print "added %d addresses" % n


def lookup_act(match, output_format, db):
    print_address_list(db.lookup(match), output_format)


def run():
    options = docopt.docopt(__doc__)

    try:
        cf = NotMuchConfig(options['--config'])
        if cf.get("addressbook", "backend") == "sqlite3":
            db = SQLiteStorage(cf)
        else:
            print "Database backend '%s' is not implemented." % \
                cf.get("addressbook", "backend")

        if options['create']:
            create_act(db, cf)
        elif options['update']:
            update_act(db, options['--verbose'])
        elif options['lookup']:
            lookup_act(options['<match>'], options['--output'], db)
        elif options['changename']:
            db.change_name(options['<address>'], options['<name>'])
    except Exception as exc:
        if options['--verbose']:
            import traceback
            traceback.print_exc()
        else:
            print exc

if __name__ == '__main__':
    run()
