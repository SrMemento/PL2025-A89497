import sys
from analisador_sintatico import parse  # Isso deve vir do seu analisador sintático
from ast_nodes import *   # Define Program, VarDecl, Const, etc.

class SemanticError(Exception):
    pass

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def declare(self, name, var_type):
        if name in self.symbols:
            raise SemanticError(f"Variável '{name}' já declarada.")
        self.symbols[name] = var_type

    def assign(self, name, value_type):
        if name in self.symbols:
            if self.symbols[name] != value_type:
                raise SemanticError(f"Tipo incompatível para '{name}': esperado {self.symbols[name]}, recebeu {value_type}.")
            return
        elif self.parent:
            self.parent.assign(name, value_type)
        else:
            raise SemanticError(f"Variável '{name}' não declarada.")

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            raise SemanticError(f"Variável '{name}' não declarada.")

class SemanticAnalyzer:
    def __init__(self):
        self.current_scope = SymbolTable()

    def visit(self, node):
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
            return

        #print("DEBUG visitando:", type(node), repr(node))

        if node is None:
            raise SemanticError("Erro semântico: nó é None (AST mal formada?)")
        if isinstance(node, str):
            raise SemanticError(f"Erro semântico: 'str' encontrado onde se esperava um nó AST. Valor: {repr(node)}")
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)




    def generic_visit(self, node):
        raise SemanticError(f"Semântica não implementada para: {type(node).__name__}")

    # Método para analisar o nó Program
    def visit_Program(self, node):
        self.visit(node.block)  # Visitando o bloco dentro do Program
    # Outros métodos, como visit_VarDecl, visit_Assignment, etc.

    def visit_If(self, node):
        # Verificar se a expressão condicional é booleana
        condition_type = self.visit(node.condition)
        if condition_type != 'boolean':
            raise SemanticError(f"A condição do 'if' deve ser do tipo 'boolean', mas recebeu '{condition_type}'.")

        # Visitar as instruções no bloco 'then'
        self.visit(node.then_branch)  # Ajustado para acessar 'then_branch'

        # Se houver um bloco 'else', visitar também
        if node.else_branch:
            self.visit(node.else_branch)  # Ajustado para acessar 'else_branch'


    # Método para analisar o nó Block
    def visit_Block(self, node):
        for decl in node.declarations:  # Visitando declarações (VarDecl, Const, etc.)
            self.visit(decl)
        for stmt in node.statements:  # Visitando instruções (Assignments, If, While, etc.)
            self.visit(stmt)

    def visit_VarDecl(self, node):
        if isinstance(node.vartype, str):
            self.current_scope.declare(node.name, node.vartype)
        elif isinstance(node.vartype, ArrayType):
            self.current_scope.declare(node.name, node.vartype)
        else:
            raise SemanticError(f"Tipo inválido para variável '{node.name}': {type(node.vartype).__name__}")


    def visit_While(self, node):
        cond_type = self.visit(node.condition)
        if cond_type != 'boolean':
            raise SemanticError("A condição do 'while' deve ser booleana.")
        self.visit(node.body)

    def visit_Compound(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_For(self, node):
        # Verifica se a variável de controle já foi declarada
        try:
            self.current_scope.lookup(node.var)
        except SemanticError:
            # Se não foi declarada, você pode declarar aqui se sua linguagem permitir
            self.current_scope.declare(node.var, 'integer')
    
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
    
        if start_type != 'integer' or end_type != 'integer':
            raise SemanticError("Limites do 'for' devem ser inteiros.")
    
        self.visit(node.body)


    def visit_Assignment(self, node):
        if isinstance(node.var, ArrayAccess):
            array_type = self.current_scope.lookup(node.var.array_var.name)
            if not isinstance(array_type, ArrayType):
                raise SemanticError(f"'{node.var.array_var.name}' não é um array.")

            index_type = self.visit(node.var.index_expr)
            if index_type != 'integer':
                raise SemanticError("Índice do array deve ser inteiro.")

            expr_type = self.visit(node.expr)
            if expr_type != array_type.base_type:
                raise SemanticError(f"Atribuição inválida: tipo '{expr_type}' diferente do tipo do array '{array_type.base_type}'.")
        else:
            expr_type = self.visit(node.expr)
            if isinstance(node.var, Var):
                var_type = self.current_scope.lookup(node.var.name)
            else:
                raise SemanticError("Atribuição a tipo de variável desconhecido.")

            if isinstance(expr_type, str) and isinstance(var_type, str):
                if expr_type != var_type:
                    raise SemanticError(f"Atribuição inválida: variável '{node.var.name}' é '{var_type}', recebeu '{expr_type}'")
            else:
                raise SemanticError(f"Atribuição inválida: tipo inesperado em '{node.var.name}'")


    def visit_Const(self, node):
        if isinstance(node.value, bool):
            return 'boolean'
        elif isinstance(node.value, int):
            return 'integer'
        elif isinstance(node.value, str):
            return 'string'
        else:
            raise SemanticError(f"Constante de tipo desconhecido: {node.value}")

    def visit_FunctionCall(self, node):
        if node.name == 'length':
            if len(node.args) != 1:
                raise SemanticError(f"Função 'length' espera 1 argumento, recebeu {len(node.args)}.")
            
            arg_type = self.visit(node.args[0])
            
            if isinstance(arg_type, ArrayType) or arg_type == 'string':
                return 'integer'
            else:
                raise SemanticError(f"Argumento de 'length' deve ser um array ou string, mas é '{arg_type}'.")
        else:
            # Função definida pelo utilizador
            try:
                return_type = self.current_scope.lookup(node.name)
                
                for arg in node.args:
                    self.visit(arg)  # Valida os argumentos, mesmo que sem verificação de tipo formal
                
                return return_type  # ← NÃO visitar, pois é uma string, como 'integer'
            
            except SemanticError:
                raise SemanticError(f"Função desconhecida: {node.name}")




    def visit_BinaryOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.op.lower()
    
        if op in ['+', '-', '*', 'div', 'mod']:
            if left_type == 'integer' and right_type == 'integer':
                return 'integer'
            else:
                raise SemanticError(f"Operador '{op}' só suporta inteiros")
        elif op in ['=', '<>', '<', '<=', '>', '>=']:
            # Aqui, implementa comparação para tipos iguais, por exemplo:
            if left_type == right_type:
                return 'boolean'
            else:
                raise SemanticError("Tipos incompatíveis na comparação")
        elif op in ['and', 'or']:
            if left_type == 'boolean' and right_type == 'boolean':
                return 'boolean'
            else:
                raise SemanticError(f"Operador '{op}' só suporta booleanos")
        else:
            raise SemanticError(f"Operador desconhecido: {op}")

    def visit_UnaryOp(self, node):
        expr_type = self.visit(node.expr)
        if node.op == '-':
            if expr_type != 'integer':
                raise SemanticError("Negação aritmética só pode ser usada com inteiros.")
            return 'integer'
        elif node.op == 'not':
            if expr_type != 'boolean':
                raise SemanticError("Negação lógica só pode ser usada com booleanos.")
            return 'boolean'

    def visit_Var(self, node):
        return self.current_scope.lookup(node.name)

    def visit_WriteLn(self, node):
        for expr in node.exprs:
            tipo = self.visit(expr)
            if tipo.lower() not in ['string', 'integer']:
                raise SemanticError(f"Tipo inválido para writeln: {tipo}")
        return None


    def visit_Write(self, node):
        for expr in node.exprs:
            expr_type = self.visit(expr)
            if expr_type not in ['integer', 'string', 'boolean']:
                raise SemanticError(f"Tipo inválido para write: {expr_type}")
        return 'void'

    def visit_ReadLn(self, node):
        for expr in node.exprs:
            expr_type = self.visit(expr)
            # expr_type pode ser uma string ou um objeto ArrayType
            if isinstance(expr_type, ArrayType):
                raise SemanticError("readln não suporta arrays diretamente.")
            if not isinstance(expr_type, str):
                raise SemanticError(f"Tipo inválido retornado para readln: {expr_type}")
            expr_type = expr_type.lower()
            if expr_type not in ['integer', 'string', 'boolean']:
                raise SemanticError(f"Tipo inválido para readln: {expr_type}")
        return 'void'


    def visit_ArrayAccess(self, node):
        base = node.array_var
        while isinstance(base, ArrayAccess):
            base = base.array_var
    
        var_type = self.current_scope.lookup(base.name)
    
        index_type = self.visit(node.index_expr)
        if index_type != 'integer':
            raise SemanticError(f"Índice do array deve ser inteiro, mas é '{index_type}'.")
    
        # Aceita tanto arrays quanto strings como indexáveis
        if isinstance(var_type, ArrayType):
            return var_type.base_type
        elif var_type == 'string':
            return 'string'  # ou 'char', se você quiser ser mais específico
        else:
            raise SemanticError(f"'{base.name}' não é indexável.")

    def visit_list(self, nodes):
        for node in nodes:
            self.visit(node)
    
    def visit_FunctionDecl(self, node):
        # Salva assinatura na tabela de símbolos global
        self.current_scope.declare(node.name, node.return_type)

        # Cria escopo local para parâmetros e corpo
        local_scope = SymbolTable(self.current_scope)
        for nome, tipo in node.params:
            local_scope.declare(nome, tipo)

        local_scope.declare(node.name, node.return_type)

        anterior = self.current_scope
        self.current_scope = local_scope
        self.visit(node.body)
        self.current_scope = anterior



def main():
    if len(sys.argv) != 2:
        print("Uso: python analizador_semantico.py <ficheiro>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r') as file:
            source = file.read()

        # O parse() precisa vir do seu analisador léxico/sintático
        ast = parse(source)

        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)

        print("✓ Análise semântica concluída com sucesso.")

    except FileNotFoundError:
        print(f"Erro: Ficheiro '{filepath}' não encontrado.")
    except SemanticError as e:
        print(f"Erro semântico: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()
