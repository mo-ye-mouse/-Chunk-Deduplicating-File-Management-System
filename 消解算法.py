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

#否定符号内移
def move_negation(expr):
    while True:
        # ¬¬A → A（双重否定律）
        m=re.search(r'¬¬\(([^()]*(?:\([^()]*\)[^()]*)*)\)',expr)
        if m:
            a=m.group(1)
            expr=expr[:m.start()] + '(' + a + ')' + expr[m.end():]
            continue
        # ¬(A∧B) → ¬A∨¬B
        m=re.search(r'¬\(([^()]+)∧([^()]+)\)',expr)
        if m:
            a=m.group(1)
            b=m.group(2)
            repl='( ¬' + a + '∨ ¬' + b + ')'
            expr=expr[:m.start()] + repl + expr[m.end():]
            continue
        # ¬(A∨B) → ¬A∧¬B
        m=re.search(r'¬\(([^()]+)∨([^()]+)\)',expr)
        if m:
            a = m.group(1)
            b = m.group(2)
            repl='( ¬' + a + '∧ ¬' + b + ')'
            expr = expr[:m.start()] + repl + expr[m.end():]
            continue
        break
    return expr

#将合式公式转化成合取范式
def transform(expr):
    #消除等价联结词
    expr=eliminate_operate1(expr)
    #消除蕴含联结词
    expr=eliminate_operate2(expr)
    #否定符号内移
    expr=move_negation(expr)
    #析取对合取的分配律

    return expr
expr=input()
print(transform(expr))



