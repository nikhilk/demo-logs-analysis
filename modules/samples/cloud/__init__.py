from IPython import get_ipython
from IPython.core.magic import register_cell_magic

from _bigQuery import _BigQueryService as BigQuery

def _rewrite_sql(sql, variables):
    import re
    tokens = re.findall("(\$\$)|(\$[a-zA-Z0-9_]+)|([^\$]*)", sql)

    parts = []
    for token in tokens:
        if (len(token[0])):
            parts.append('$')
        elif (len(token[1])):
            value = variables[token[1][1:]]
            if 'sql' in dir(value):
                value = '(' + value.sql() + ')'
            else:
                value = str(value)
            parts.append(value)
        elif (len(token[2])):
            parts.append(token[2])

    return ''.join(parts)


@register_cell_magic
def bigQuery(var, sql):
    ipy = get_ipython()

    sql = _rewrite_sql(sql, ipy.user_ns)
    data = BigQuery.data(sql)

    if len(var) != 0:
        ipy.push({ var: data })
        return None
    else:
        return data.dataFrame()
