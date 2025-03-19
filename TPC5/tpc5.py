import json
import re
from pathlib import Path

class MaquinaVending:
    def __init__(self):
        self.stock_file = Path("stock.json")
        self.stock = self.carregar_stock()
        self.saldo = 0  # em cêntimos
        self.moedas = {200: '2e', 100: '1e', 50: '50c', 20: '20c', 10: '10c', 5: '5c', 2: '2c', 1: '1c'}

    def carregar_stock(self):
        try:
            with open(self.stock_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Erro: Ficheiro stock.json não encontrado!")
            exit(1)

    def guardar_stock(self):
        with open(self.stock_file, 'w') as f:
            json.dump(self.stock, f, indent=2)

    def processar_comando(self, comando):
        # Expressões regulares para comandos
        if re.match(r'^LISTAR$', comando):
            self.listar_produtos()
        
        elif mo := re.match(r'^MOEDA\s+((?:\d+[ec],?\s*)+)\.$', comando):
            self.processar_moedas(mo.group(1))
        
        elif sel := re.match(r'^SELECIONAR\s+([A-Z0-9]+)$', comando):
            self.selecionar_produto(sel.group(1))
        
        elif re.match(r'^SAIR$', comando):
            self.processar_saida()
            return False
        
        else:
            print("maq: Comando inválido. Tente novamente.")
        return True

    def listar_produtos(self):
        print("\ncod | nome | quantidade | preço")
        print("-"*30)
        for produto in self.stock:
            print(f"{produto['cod']} {produto['nome']} {produto['quant']} {produto['preco']:.2f}€")

    def processar_moedas(self, moedas_str):
        moedas_validas = re.findall(r'(\d+)([ec])', moedas_str)
        total = 0
        
        for valor, tipo in moedas_validas:
            valor = int(valor)
            if tipo == 'e':
                total += valor * 100
            else:
                total += valor
        
        self.saldo += total
        print(f"maq: Saldo = {self.formatar_saldo()}")

    def selecionar_produto(self, codigo):
        produto = next((p for p in self.stock if p['cod'] == codigo), None)
        
        if not produto:
            print(f"maq: Produto {codigo} inexistente")
            return
        
        if produto['quant'] <= 0:
            print(f"maq: Produto {produto['nome']} esgotado")
            return
        
        preco = int(produto['preco'] * 100)
        if self.saldo < preco:
            print(f"maq: Saldo insuficiente (Saldo: {self.formatar_saldo()}, Pedido: {preco//100}e{preco%100:02d}c)")
            return
        
        self.saldo -= preco
        produto['quant'] -= 1
        print(f'maq: Pode retirar o produto dispensado "{produto["nome"]}"')
        print(f"maq: Saldo = {self.formatar_saldo()}")

    def processar_saida(self):
        if self.saldo > 0:
            troco = self.calcular_troco()
            print(f"maq: Pode retirar o troco: {troco}")
        print("maq: Até à próxima")

    def calcular_troco(self):
        troco = []
        restante = self.saldo
        
        for valor in sorted(self.moedas.keys(), reverse=True):
            if restante >= valor:
                qtd = restante // valor
                restante %= valor
                troco.append(f"{qtd}x {self.moedas[valor]}")
        
        return ", ".join(troco[:-1]) + f" e {troco[-1]}" if len(troco) > 1 else troco[0]

    def formatar_saldo(self):
        euros = self.saldo // 100
        centimos = self.saldo % 100
        return f"{euros}e{centimos:02d}c" if euros > 0 else f"{centimos}c"

def main():
    maq = MaquinaVending()
    print("maq: Bom dia. Estou disponível para atender o seu pedido.")
    
    while True:
        try:
            comando = input(">> ").strip().upper()
            if not maq.processar_comando(comando):
                break
        except KeyboardInterrupt:
            print("\nmaq: A desligar...")
            break
    
    maq.guardar_stock()

if __name__ == "__main__":
    main()
