import re


#  消除合式公式中的等价式
def eliminate_operate1(expr):
    while '↔' in expr:
        expr = re.sub(r'([A-Za-z¬∨∧()]+)↔([A-Za-z¬∨∧()]+)',r'(\1→\2)∧(\2→\1)', expr, count=1)
    return expr


#  消除合式公式中的蕴含式
def eliminate_operate2(expr):
    while '→' in expr:
        expr = re.sub(r'([A-Za-z¬∨∧()]+)→([A-Za-z¬∨∧()]+)',r'(¬\1∨\2)', expr, count=1)
    return expr


#  否定符号内移
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


def distribute_disjunction_over_conjunction(formula):
    while re.search(r'([^∨]+)∨\(([^()]+∧[^()]+)\)', formula):
        match=re.search(r'([^∨]+)∨\(([^()]+∧[^()]+)\)', formula)
        if not match:
            break
        a=match.group(1).strip()
        bc=match.group(2).strip()
        bc_part=[x.strip() for x in bc.split('∧')]
        distributed='∧'.join(f'{a}∨{part}' for part in bc_part)
        formula=formula.replace(f'{a}∨({bc})',distributed)
    return formula


# 将CNF公式拆分为子句集（每个子句是文字的集合）
def _split_clauses(self, cnf_formula):
    if "∧" in cnf_formula:
        clauses = cnf_formula.split("∧")
    else:
        clauses = [cnf_formula]

    clause_set = []
    for clause in clauses:
        # 处理可能的外层括号
        clause = self._parse_parentheses(clause)
        if "∨" in clause:
            literals = clause.split("∨")
        else:
            literals = [clause]

        literal_set = set()
        for lit in literals:
            # 确保处理的是字符串（修复核心问题）
            lit = self._parse_parentheses(lit)  # 移除文字中的括号
            if lit.startswith("¬"):
                literal_set.add(("¬", lit[1:]))  # 否定文字
            else:
                literal_set.add(("", lit))  # 肯定文字

        clause_set.append(frozenset(literal_set))

    return clause_set


# 判断两个子句是否可消解（存在互补文字）
def _can_resolve(self, clause1, clause2):
    for lit1 in clause1:
        for lit2 in clause2:
            if (lit1[0] == "" and lit2[0] == "¬" and lit1[1] == lit2[1]) or \
               (lit1[0] == "¬" and lit2[0] == "" and lit1[1] == lit2[1]):
                return True
    return False


# 计算两个子句的消解式（移除所有互补文字对）
def _resolve(self, clause1, clause2):
    resolvent = set(clause1) | set(clause2)
    to_remove = set()
    for lit1 in clause1:
        for lit2 in clause2:
            if (lit1[0] == "" and lit2[0] == "¬" and lit1[1] == lit2[1]) or \
               (lit1[0] == "¬" and lit2[0] == "" and lit1[1] == lit2[1]):
                to_remove.add(lit1)
                to_remove.add(lit2)
    resolvent -= to_remove
    return frozenset(resolvent)


# 执行消解算法，判断公式是否可满足
def is_satisfiable(self, formula):
    cnf = self._to_cnf(formula)
    initial_clauses = self._split_clauses(cnf)
    self.S1 = set(initial_clauses)
    self.S0 = set()
    self.S2 = set()

    while True:
        clause_pairs = [(c1, c2) for c1 in self.S1 for c2 in self.S1 if c1 != c2]

        for c1, c2 in clause_pairs:
            if self._can_resolve(c1, c2):
                resolvent = self._resolve(c1, c2)
                if not resolvent:
                    return False
                if resolvent not in self.S0 and resolvent not in self.S1 and resolvent not in self.S2:
                    self.S2.add(resolvent)

        if not self.S2:
            return True

        self.S0.update(self.S1)
        self.S1 = self.S2.copy()
        self.S2.clear()


#将合式公式转化成合取范式
def transform(expr):
    #消除等价联结词
    expr=eliminate_operate1(expr)
    #消除蕴含联结词
    expr=eliminate_operate2(expr)
    #否定符号内移
    expr=move_negation(expr)
    #析取对合取的分配律
    expr=distribute_disjunction_over_conjunction(expr)
    #消解合取范式
    cnf=expr.replace('∧','&').replace('∨','|').replace('¬','~')

    return expr
expr=input()
print(transform(expr))



