from ast_nodes import *
from analisador_sintatico import parse
from analisador_semantico import SemanticAnalyzer, SemanticError

class GeradorVM:
    def __init__(self, tabela_tipos):
        self.codigo = []
        self.labels = 0
        self.tabela_vars = {}  # Mapeia nomes para índices
        self.tabela_tipos = tabela_tipos  # novo dicionário para armazenar tipos
        self.funcoes = {}  # nome -> FunctionDecl
        self.proximo_indice = 0

    def nova_label(self):
        lbl = f"L{self.labels}"
        self.labels += 1
        return lbl

    def gerar(self, programa):
        self.codigo.append("START")
        self.visitar(programa)
        self.codigo.append("STOP")
        return self.codigo

    def expr_retorna_inteiro(self, expr):
        if isinstance(expr, Const):
            return isinstance(expr.value, int)
        elif isinstance(expr, (Var, BinaryOp, UnaryOp)):
            return True  # Assume-se que variáveis e operações são inteiras por padrão
        return False


    def visitar(self, no):
        if isinstance(no, list):
            for elemento in no:
                self.visitar(elemento)
            return

        elif isinstance(no, Program):
            self.visitar(no.block)

        elif isinstance(no, Block):
            for decl in no.declarations:
                self.visitar(decl)
            for stmt in no.statements:
                self.visitar(stmt)

        elif isinstance(no, VarDecl):
            if no.name not in self.tabela_vars:
                self.tabela_vars[no.name] = self.proximo_indice
                self.tabela_tipos[no.name] = no.vartype
                if isinstance(no.vartype, ArrayType):
                    tamanho = no.vartype.end_idx - no.vartype.start_idx + 1
                    self.codigo.append(f"PUSHI {tamanho}")
                    self.codigo.append("ALLOCN")
                    self.codigo.append(f"STOREG {self.proximo_indice}")
                    self.proximo_indice += 1  # apenas 1 posição global para armazenar o endereço do array
                else:
                    self.proximo_indice += 1


        elif isinstance(no, Assignment):
            if isinstance(no.var, ArrayAccess):
                # Gerar o endereço do elemento do array
                indice_base = self.tabela_vars.get(no.var.array_var.name)
                self.codigo.append(f"PUSHG {indice_base}")
                self.visitar(no.var.index_expr)
                self.codigo.append(f"PUSHI 1")
                self.codigo.append(f"SUB")
                self.visitar(no.expr)
                self.codigo.append("STOREN")

            else:
                self.visitar(no.expr)
                indice = self.tabela_vars.get(no.var.name)
                self.codigo.append(f"STOREG {indice}")

        elif isinstance(no, If):
            label_else = self.nova_label()
            label_end = self.nova_label()

            self.visitar(no.condition)
            self.codigo.append(f"JZ {label_else}")
            self.visitar(no.then_branch)
            self.codigo.append(f"JUMP {label_end}")
            self.codigo.append(f"{label_else}:")
            if no.else_branch:
                self.visitar(no.else_branch)
            self.codigo.append(f"{label_end}:")

        elif isinstance(no, Compound):
            for stmt in no.statements:
                self.visitar(stmt)

        elif isinstance(no, BinaryOp):
            # Sempre visitar left antes do right para preservar a ordem dos operandos
            self.visitar(no.left)
            self.visitar(no.right)
    
            instr = self.map_op(no.op)
            if '\n' in instr:
                for i in instr.split('\n'):
                    self.codigo.append(i)
            else:
                self.codigo.append(instr)

        elif isinstance(no, UnaryOp):
            self.visitar(no.expr)
            if no.op == '-':
                self.codigo.append("PUSHI -1")
                self.codigo.append("MUL")
            elif no.op == 'not':
                self.codigo.append("NOT")

        elif isinstance(no, Var):
            indice = self.tabela_vars.get(no.name)
            self.codigo.append(f"PUSHG {indice}")

        elif isinstance(no, Write):
            for expr in no.exprs:
                self.visitar(expr)
                self.codigo.append("WRITES")
            # Não adiciona WRITELN, pois Write não adiciona nova linha

        elif isinstance(no, WriteLn):
            for expr in no.exprs:
                if isinstance(expr, Const) and isinstance(expr.value, str):
                    # Constante string: só empilha e escreve direto
                    self.visitar(expr)  # PUSHS "string"
                    self.codigo.append("WRITES")
                else:
                    # Expressão que gera inteiro (var, binop, unop, const int)
                    self.visitar(expr)  # gera código que empilha o valor
                    self.codigo.append("STRI")  # converte inteiro para string
                    self.codigo.append("WRITES")
            self.codigo.append("WRITELN")


        elif isinstance(no, ReadLn):
            for var in no.exprs:
                if isinstance(var, ArrayAccess):
                    indice_base = self.tabela_vars.get(var.array_var.name)
                    self.codigo.append(f"PUSHG {indice_base}")   # endereço base do array
                    self.visitar(var.index_expr)                  # empilha índice
                    self.codigo.append("PUSHI 1")
                    self.codigo.append("SUB")                       # endereço final
                    self.codigo.append("READ")
                    self.codigo.append("ATOI")
                    self.codigo.append("STOREN")


                elif isinstance(var, Var):
                    indice = self.tabela_vars.get(var.name)
                    tipo = self.tabela_tipos.get(var.name)

                    self.codigo.append("READ")
                    if tipo.lower() == 'string':
                        self.codigo.append(f"STOREG {indice}")
                    elif tipo.lower() == 'integer':
                        self.codigo.append("ATOI")
                        self.codigo.append(f"STOREG {indice}")
                    else:
                        raise Exception(f"Tipo não suportado em READLN: {tipo}")
                else:
                    raise Exception(f"Operação READLN não suportada para {type(var)}")


        elif isinstance(no, Const):
            if isinstance(no.value, str):
                if len(no.value) == 1:
                    self.codigo.append(f'PUSHI {ord(no.value)}')  # usa código ASCII
                else:
                    self.codigo.append(f'PUSHS "{no.value}"')  # string comum

            elif isinstance(no.value, bool):
                self.codigo.append(f'PUSHI {1 if no.value else 0}')
            else:
                self.codigo.append(f'PUSHI {no.value}')

        elif isinstance(no, For):
            var_nome = no.var
            inicio = no.start
            fim = no.end
            corpo = no.body
        
            if var_nome not in self.tabela_vars:
                self.tabela_vars[var_nome] = self.proximo_indice
                self.proximo_indice += 1
        
            indice = self.tabela_vars[var_nome]
        
            # Atribui valor inicial à variável de controle
            self.visitar(inicio)
            self.codigo.append(f"STOREG {indice}")
        
            label_inicio = self.nova_label()
            label_fim = self.nova_label()
        
            self.codigo.append(f"{label_inicio}:")
        
            # Carrega variável de controle e valor final
            self.codigo.append(f"PUSHG {indice}")
            self.visitar(fim)
        
            if no.downto:
                self.codigo.append("SUPEQ")  # i < fim → sai do loop
                self.codigo.append(f"JZ {label_fim}")
                
            else:
                self.codigo.append("INFEQ")  # i > fim → sai do loop
                self.codigo.append(f"JZ {label_fim}")
        
            #self.codigo.append("NOT")
        
            # Corpo do loop
            self.visitar(corpo)
            #print(no.downto)
        
            # Incrementa ou decrementa
            self.codigo.append(f"PUSHG {indice}")
            self.codigo.append("PUSHI 1")
            if no.downto:
                self.codigo.append("SUB")
            else:
                self.codigo.append("ADD")
            
            self.codigo.append(f"STOREG {indice}")
        
            self.codigo.append(f"JUMP {label_inicio}")
            self.codigo.append(f"{label_fim}:")

        elif isinstance(no, While):
            label_inicio = self.nova_label()
            label_fim = self.nova_label()
        
            self.codigo.append(f"{label_inicio}:")
            self.visitar(no.condition)
            self.codigo.append(f"JZ {label_fim}")
            self.visitar(no.body)
            self.codigo.append(f"JUMP {label_inicio}")
            self.codigo.append(f"{label_fim}:")

        elif isinstance(no, FunctionCall):
            if no.name == "length":
                arg = no.args[0]
                self.visitar(arg)
                self.codigo.append("STRLEN")
        
            elif no.name in self.funcoes:
                func = self.funcoes[no.name]
        
                # Atribui os argumentos diretamente aos parâmetros (assume já declarados)
                for (param_nome, _), arg_expr in zip(func.params, no.args):
                    self.visitar(arg_expr)
                    indice_param = self.tabela_vars[param_nome]
                    self.codigo.append(f"STOREG {indice_param}")
        
                # Gera o corpo da função inline (assume não-recursiva)
                self.visitar(func.body)
        
                # Carrega o valor de retorno
                indice_retorno = self.tabela_vars[func.name]
                self.codigo.append(f"PUSHG {indice_retorno}")
        
            else:
                raise Exception(f"Função não suportada: {no.name}")


        elif isinstance(no, ArrayAccess):
            var_nome = no.array_var.name
            indice_base = self.tabela_vars.get(var_nome)
            tipo_var = self.tabela_tipos.get(var_nome)
        
            if tipo_var == 'string':
                # Acesso a caractere da string
                self.codigo.append(f"PUSHG {indice_base}")   # string
                self.visitar(no.index_expr)                  # índice
                self.codigo.append("PUSHI 1")
                self.codigo.append("SUB")
                self.codigo.append("CHARAT")                 # Acessa caractere da string
            else:
                # Acesso a array comum (inteiros)
                self.codigo.append(f"PUSHG {indice_base}")   # endereço base
                self.visitar(no.index_expr)
                self.codigo.append("PUSHI 1")
                self.codigo.append("SUB")
                self.codigo.append("LOADN")                  # Acessa valor numérico

        elif isinstance(no, FunctionDecl):
            self.funcoes[no.name] = no  # Armazena para chamada posterior
            # Reservar espaço para o valor de retorno
            if no.name not in self.tabela_vars:
                self.tabela_vars[no.name] = self.proximo_indice
                self.tabela_tipos[no.name] = no.return_type
                self.proximo_indice += 1

            # Reservar espaço para os parâmetros da função
            for nome, tipo in no.params:
                if nome not in self.tabela_vars:
                    self.tabela_vars[nome] = self.proximo_indice
                    self.tabela_tipos[nome] = tipo
                    self.proximo_indice += 1

            

        else:
            raise Exception(f"Nó não suportado: {type(no)}")

    def map_op(self, op):
        mapa = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',
            'div': 'DIV',
            'mod': 'MOD',
            '=': 'EQUAL',
            '<>': 'EQUAL\nNOT',  # INVERTE igualdade
            '<': 'INF',
            '<=': 'INFEQ',
            '>': 'SUP',
            '>=': 'SUPEQ',
            'and': 'AND',
            'or': 'OR'
        }
        return mapa.get(op.lower(), f'??? {op}')


# -----------------------------
# Código para salvar no arquivo:
# -----------------------------

import sys

def main():
    if len(sys.argv) != 2:
        print("Uso: python gerador_codigo_vm.py <arquivo.pas>")
        return

    arquivo = sys.argv[1]

    try:
        with open(arquivo, 'r', encoding="utf-8") as f:
            codigo_fonte = f.read()

        ast = parse(codigo_fonte)

        analisador = SemanticAnalyzer()
        if ast is None:
            raise Exception("Parsing falhou — AST não foi gerada.")
        analisador.visit(ast)

        tabela_tipos = analisador.current_scope.symbols

        gerador = GeradorVM(tabela_tipos)
        instrucoes = gerador.gerar(ast)

        print("Código gerado:\n")
        for instrucao in instrucoes:
            print(instrucao)

        # Salvar no arquivo de saída com codificação correta
        with open(arquivo.replace('.pas', '.vm'), 'w', encoding='utf-8') as out:
            for instrucao in instrucoes:
                instrucao = instrucao.strip()  # Remover espaços extras ou quebras de linha
                out.write(instrucao + '\n')  # Escrever instruções com newline correto

    except FileNotFoundError:
        print(f"Arquivo '{arquivo}' não encontrado.")
    except SemanticError as e:
        print(f"Erro semântico: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()