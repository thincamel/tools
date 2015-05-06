#coding:utf-8

import unittest
import MySQLdb

mysql_config = {
    "host": "127.0.0.1",
    "passwd": "",
    "charset": "utf8",
}


class DB(object):

    def __init__(self, db_name, conn=None, *args, **kwargs):
        self.db_name = db_name
        super(DB, self).__init__()

        self.conn = conn
        self.auto_close_conn = False

        return
        if conn is None:

            self.conn = DB.get_conn(db_name)
            self.auto_close_conn = True

        self.cur = self.conn.cursor()

    def __enter__(self):
        print 123
        return 123

    def test_with_ok(self):

        with self:
            print 'i am ok '

    def test_with_error(self):
        with self:
            print 'i am wrong'
            assert 1==2

    def __exit__(self, exc, value, tb):
        if exc:
            print 'error'
        else:
            print 'ok'
        print self

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

        if self.conn is None:
            self.db.dbName = self.db_name
            row_count = self.db.execUpdate(sql, args=args)
        else:
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

        self.sql_base = DB('billing_record_db')

    def tearDown(self):
        print "*******************test done*******************"


    def testquery1(self):

        query_dict = {
            "phone": '18603036769',
            "phone__in": ('18603036769','18823331333') ,
        }

        fields = ['phone']

        result = self.sql_base.query('xh_user', query_dict=query_dict, print_sql=True, fields=fields)
        print result
        self.assertEqual(len(result), 1)

    def testquery2(self):

        query_dict = {
            "phone__like": '18603036769%',
        }
        fields = ['count(*) as count']
        result = self.sql_base.query('xh_user', query_dict=query_dict, print_sql=True, fields=fields, page=0)
        print result

    def testInsert(self):

        obj_dict = {
            "phone": "17777777777",
        }

        last_id = self.sql_base.insert('xh_user', obj_dict, print_sql=True)
        print last_id

    def testReplace(self):

        obj_dict = {
            "phone": "17777777777",
            }
        last_id = self.sql_base.insert('xh_user', obj_dict, print_sql=True, mode='replace')
        print last_id

    def testInsertOrUpdate(self):

        obj_dict = {
            "phone": "17777777777",
            "balance": "23333333333",
            }
        last_id = self.sql_base.insert('xh_user', obj_dict, print_sql=True, mode='insert_or_update')
        print last_id

    def testUpdate(self):

        query_dict = {
            "phone": '18603036769',
        }
        update_dict = {
            "balance": 12345,
            "is_vip": 4,
        }

        row_count = self.sql_base.update('xh_user', query_dict=query_dict,update_dict=update_dict,print_sql=True, sql_row_count=1)
        print "update row_count", row_count

    def testdelete(self):

        query_dict = {
            "phone": "17777777778",
            "is_vip": '0',
        }
        row_count = self.sql_base.delete('xh_user', query_dict=query_dict, print_sql=True)
        print "delete row_count", row_count


    def testTrans(self):

        print "test trans"
        _conn = DB.getConn('billing_record_db')
        with _conn:

            su = DB('billing_record_db', conn=_conn)
            su.insert("xh_user", obj_dict={"phone": 18099899995})
            print su.query('xh_user', query_dict={"phone": 18603036769})
            su.update("xh_user", query_dict={"phone": '18603036769', 'uid': 100333}, update_dict={"balance": 100}, sql_row_count=1)


class Test(object):

    def __enter__(self):
        print 123
        return 123

    def __exit__(self, exc, value, tb):
        if exc:
            print 'error'
        else:
            print 'ok'
        print self


if __name__ == "__main__":

    # unittest.main()

    test = DB('123')
    test.test_with_ok()
    test.test_with_error()


