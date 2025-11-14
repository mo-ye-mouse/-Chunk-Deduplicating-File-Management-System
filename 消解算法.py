import re
#消除合式公式中的等价式
def eliminate_operate1(expr):
    while '↔' in expr:
        expr = re.sub(r'([A-Za-z¬∨∧()]+)↔([A-Za-z¬∨∧()]+)',r'(\1→\2)∧(\2→\1)', expr, count=1)
    return expr

#消除合式公式中的蕴含式
def eliminate_operate2(expr):
    while '→' in expr:
        expr = re.sub(r'([A-Za-z¬∨∧()]+)→([A-Za-z¬∨∧()]+)',r'(¬\1∨\2)', expr, count=1)
    return expr

#将合式公式转化成合取范式
def transform(expr):
    #消除等价联结词
    expr=eliminate_operate1(expr)
    #消除蕴含联结词
    expr=eliminate_operate2(expr)
    #否定符号内移

    #析取对合取的分配律

    return expr
expr=input()
print(transform(expr))



