#! /usr/bin/env python
import argparse

import MySQLdb as mysql


def make_query(table_name, columns):
    """This function creates an insert query based on a table name and
    number of columns in that table.
    """
    return 'insert into {table} values ({values})'.format(
        table=table_name, values=', '.join('%s' for n in xrange(columns)))


def copy_table(table_name, source, target, n):
    """This function copies the actual data.
    """
    # set up two connections
    with mysql.connect(*source) as source, mysql.connect(*target) as target:
        # run the select query
        source.execute('select * from {table}'.format(table=table_name))
        # prepare the insert query
        query = make_query(table_name, len(source.description))
        # iterate over the results by fetching rows in batches of `n` rows
        rows = source.fetchmany(n)
        while rows:
            # run the insert query with each fetched batch
            target.executemany(query, rows)
            rows = source.fetchmany(n)


def make_parser():
    """This function creates and configures the command line arguments parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('table', help='Name of the database table to copy')
    parser.add_argument('-b', '--batch', default=1000,
                        help='Number of rows to fetch in one batch', type=int)
    source = parser.add_argument_group('Source', 'Connection parameters for '
                                       'the source database server.')
    target = parser.add_argument_group('Target', 'Connection parameters for '
                                       'the target database server.')
    source.add_argument('--source', nargs=4, required=True,
                        metavar=('host', 'user', 'passwd', 'db'))
    target.add_argument('--target', nargs=4, required=True,
                        metavar=('host', 'user', 'passwd', 'db'))
    return parser


def main():
    """This function gets run when the script is invoked.
    """
    parser = make_parser()
    args = parser.parse_args()
    copy_table(args.table, args.source, args.target, args.batch)


if __name__ == '__main__':
    main()
