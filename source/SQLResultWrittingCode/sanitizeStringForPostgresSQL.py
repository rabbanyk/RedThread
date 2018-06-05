# The function below is taken from the bottom of the post at:
#     https://stackoverflow.com/questions/3823735/psycopg2-equivalent-of-mysqldb-escape-string
# on day16 month1 year2018. Judging by the user name, the function appears to have been written by
# one David Wolever.

def postgres_escape_string(s):
   if not isinstance(s, basestring):
       raise TypeError("%r must be a str or unicode" %(s, ))
   escaped = repr(s)
   if isinstance(s, unicode):
       assert escaped[:1] == 'u'
       escaped = escaped[1:]
   if escaped[:1] == '"':
       escaped = escaped.replace("'", "\\'")
   elif escaped[:1] != "'":
       raise AssertionError("unexpected repr: %s", escaped)
   return "E'%s'" %(escaped[1:-1], )
