#coding:utf-8

import unittest
import MySQLdb

mysql_config = {
    "host": "127.0.0.1",
    "passwd": "",
    "charset": "utf8",
}


class DB(object):

    def __init__(self, db_name, conn=None, trans=False, auto_close_conn=True, *args, **kwargs):
        self.db_name = db_name
        super(DB, self).__init__()

        self.conn = conn
        self.auto_create_conn = False
        self._trans_end = False
        self._trans = trans
        if self._trans is False:
            self._trans_end = True
        self.auto_close_conn = auto_close_conn

        if conn is None:
            self.auto_create_conn = True

    def end_trans(self):

        self._trans_end = True
        with self:
            # commit trans and close conn
            pass

    def __enter__(self):

        if self.auto_create_conn is True and self.conn is None:
            self.conn = DB.get_conn(self.db_name)

        self.cur = self.conn.cursor()

    def __exit__(self, exc, value, tb):

        self.cur.close()
        if exc:
            self.conn.rollback()
            if self.auto_close_conn:
                self.close_conn()
        else:
            if self._trans_end is True:
                self.conn.commit()
                if self.auto_close_conn:
                    self.close_conn()


    def close_conn(self):

        self.conn.close()
        self.conn = None

    def test_with_ok(self):

        with self:
            print 'i am ok '

    def test_with_error(self):
        with self:
            print 'i am wrong'
            assert 1==2

    @staticmethod
    def get_conn(db_name):

        conn = MySQLdb.connect(user='root', db=db_name, **mysql_config)
        return conn

    def insert(self, table_name, obj_dict, mode='insert', print_sql=False):
        assert mode in ("insert", 'replace', 'insert_or_update')
        placeholders = ', '.join(['%s'] * len(obj_dict))
        columns = ', '.join(obj_dict.keys())
        args = obj_dict.values()
        start = ''
        if mode == 'insert' or mode == 'insert_or_update':
            start = "INSERT INTO "
        elif mode == 'replace':
            start = "REPLACE INTO "
        sql = "%s %s ( %s ) VALUES ( %s )" % (start, table_name, columns, placeholders)

        if mode == "insert_or_update":
            update = ['%s=%s' % (key, '%s') for key in obj_dict.keys()]
            sql += " ON DUPLICATE KEY UPDATE %s" % (','.join(update),)
            args = args*2

        if print_sql:
            print "sql:", sql
            print "args:", args

        with self:
            self.cur.execute(sql, args=args)
            last_id = int(self.conn.insert_id())
            return last_id

    def update(self, table_name, query_dict, update_dict, print_sql=False, sql_row_count=0):

        query, args = DB.gen_sql_query(query_dict)
        update = ', '.join(['%s=%s' % (key, '%s') for key in update_dict])
        args = update_dict.values() + args
        sql = "update %s set %s %s " %(table_name, update, query)
        if print_sql:
            print "sql:", sql
            print "args:", args

        with self:
            row_count = self.cur.execute(sql, args=args)
            if sql_row_count:
                assert row_count == sql_row_count
        return row_count

    def delete(self, table_name, query_dict, print_sql=False, sql_row_count=0):

        query, args = DB.gen_sql_query(query_dict)
        sql = "delete from %s %s" % (table_name, query)

        if print_sql:
            print "sql:", sql
            print "args:", args

        with self:
            row_count = self.cur.execute(sql, args=args)
            if sql_row_count:
                assert sql_row_count == row_count

        return row_count

    def query(self, table_name,query_dict={},fields=['*'],page=1,page_num=50,
                       group_by='',order_by='',print_sql=False, slave=False):

        if page == 0:
            page_p = " "
        else:
            start = page*page_num-page_num
            page_p = " limit %s,%s" % (start, page_num)

        query, args = DB.gen_sql_query(query_dict)
        sql = "select %s from %s %s %s %s %s" % (','.join(fields), table_name, query, group_by, order_by, page_p)
        if print_sql:
            print "sql:", sql
            print "args:", args

        with self:
            self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
            self.cur.execute(sql, args=args)
            result = self.cur.fetchall()
            return result

    @staticmethod
    def gen_sql_query(query_dict):

        query = ""
        if not query_dict:
            return query,None

        args = []
        for key, value in query_dict.items():
            key = key.split("__")
            op = key[1] if len(key) == 2 else 'eq'
            sql_operator = DB.get_sql_operator(op)

            if not query:
                place = "where"
            else:
                place = "and"

            if sql_operator == 'in':
                query += " %s %s in (%s)" % (place, key[0], ','.join(['%s']*len(value)),)
                args.extend(list(value))
            else:
                query += " %s %s %s %s" % (place, key[0], sql_operator, '%s')
                args.append(value)

        return query,args

    @staticmethod
    def get_sql_operator(op):

        operator_dict = {
            'gt': '>',
            'gte': '>=',
            'eq': '=',
            'neq': '!=',
            'lt': '<',
            'lte': '<=',
            'in': 'in',
            'like': 'like',
            'regexp': 'regexp',
        }

        if op not in operator_dict:
            assert Exception("not supported operator")

        return operator_dict[op]


class autoTestCase(unittest.TestCase):

    def setUp(self):

        print '*****************test begin*******************'

    def tearDown(self):
        print "*******************test done*******************"

    def init_db(self):

        query_dict = {
            "uid__in": (1, 2)
        }

        mysqldb = DB("db_for_test")
        mysqldb.delete('user', query_dict=query_dict)

    def insert_success(self):

        mysqldb = DB("db_for_test", trans=True)
        mysqldb.insert('user', obj_dict={"uid": 1})
        mysqldb.insert('user', obj_dict={"uid": 2})
        mysqldb.end_trans()

    def insert_success_ok(self):

        mysqldb = DB("db_for_test")
        result = mysqldb.query('user', query_dict={"uid": 1})
        assert len(result) == 1

    def insert_fail(self):

        mysqldb = DB("db_for_test", trans=True)
        mysqldb.insert('user', obj_dict={"uid": 1})
        mysqldb.insert('user', obj_dict={"uid": 3})

    def insert_success_fail(self):

        mysqldb = DB("db_for_test")
        result = mysqldb.query('user', query_dict={"uid": 3})
        assert len(result) == 0

    def testdb(self):

        self.init_db()
        self.insert_success()
        self.insert_success_ok()
        try:
            self.insert_fail()
        except:
            pass
        self.insert_success_fail()

if __name__ == "__main__":

    unittest.main()

