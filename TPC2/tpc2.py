def split_csv_line(line):
    
    result = []
    current_field = ""
    in_quotes = False
    pos = 0

    while pos < len(line):
        char = line[pos]

        if char == '"' and (pos + 1 < len(line) and line[pos + 1] == '"'):
            # Duplas aspas: adiciona uma e avança duas posições
            current_field += '"'
            pos += 2
            continue
        elif char == '"':
            # Inverte estado das aspas
            in_quotes = not in_quotes
        elif char == ";" and not in_quotes:
            # Separador fora de aspas, finaliza campo
            result.append(current_field.strip())
            current_field = ""
        else:
            # Caractere normal, adiciona ao campo
            current_field += char
        
        pos += 1

    # Adiciona último campo processado
    result.append(current_field.strip())

    return result


def csv_parser(arquivo):
    catalog = {}
    
    with open(arquivo, "r", encoding="utf-8") as file:
        counter = 0
        buffer = ""

        for linha in file:
            if counter == 0:  # Pular cabeçalho
                counter += 1
                continue
            
            buffer += linha.rstrip('\n')

            # Verificar se número de aspas é par (linha completa)
            if buffer.count('"') % 2 == 0:
                dados = split_csv_line(buffer)

                # Garantir 7 elementos
                dados += [""] * (7 - len(dados))

                titulo = dados[0].strip()
                entry = {
                    "desc": dados[1].strip(),
                    "anoCriacao": dados[2].strip(),
                    "periodo": dados[3].strip(),
                    "compositor": dados[4].strip(),
                    "duracao": dados[5].strip(),
                    "id": dados[6].strip()
                }

                catalog[titulo] = entry
                counter += 1
                buffer = ""  # Reinicia buffer

    return catalog


def lista_compositores(data):
    autores = set()

    for obra in data.values():
        compositor = obra.get("compositor", "").strip()
        if compositor:
            # Formatar nome invertido
            if "," in compositor:
                parte1, sep, parte2 = compositor.partition(',')
                compositor = f"{parte2.strip()} {parte1.strip()}"
            
            autores.add(compositor)

    return sorted(autores)


def nr_obras_por_periodo(obras):
    contagem = {}
    for obra in obras.values():
        periodo = obra.get("periodo", "").strip()
        if periodo:
            contagem[periodo] = contagem.get(periodo, 0) + 1
    return contagem


def obras_por_periodo(base_dados):
    periodos = {}
    for titulo, metadata in base_dados.items():
        epoca = metadata.get("periodo", "").strip()
        if epoca:
            periodos.setdefault(epoca, []).append(titulo)
    return periodos


def main():
    dados_obras = csv_parser("./assets/obras.csv")
    # compositores = lista_compositores(dados_obras)
    # print(compositores)
    # contagem = nr_obras_por_periodo(dados_obras)
    # print(contagem)
    por_periodo = obras_por_periodo(dados_obras)
    print(por_periodo)

main()
