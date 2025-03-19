import sys
import re

def convert_md_to_html(input_file):
    output_content = ""
    ordered_list_open = False  # Controla se estamos numa lista ordenada
    
    with open(input_file) as md_file:
        for md_line in md_file:
            cleaned_line = md_line.rstrip('\n')  # Remove apenas a quebra de linha

            # Processa listas ordenadas primeiro
            ol_match = re.match(r'^(\d+)\.\s+(.+)', cleaned_line)
            if ol_match:
                if not ordered_list_open:
                    output_content += "<ol>\n"
                    ordered_list_open = True
                output_content += f"<li>{ol_match.group(2)}</li>\n"
                continue
            elif ordered_list_open:
                output_content += "</ol>\n"
                ordered_list_open = False

            # Converte cabeçalhos
            cleaned_line = re.sub(r'^###\s+(.+)', r'<h3>\1</h3>', cleaned_line)
            cleaned_line = re.sub(r'^##\s+(.+)', r'<h2>\1</h2>', cleaned_line)
            cleaned_line = re.sub(r'^#\s+(.+)', r'<h1>\1</h1>', cleaned_line)
            
            # Formatação de texto
            cleaned_line = re.sub(r'(\*\*)(.+?)(\*\*)', r'<b>\2</b>', cleaned_line)
            cleaned_line = re.sub(r'(?<!\*)\*([^\*]+?)\*(?!\*)', r'<i>\1</i>', cleaned_line)
            
            # Elementos multimédia
            cleaned_line = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img alt="\1" src="\2"/>', cleaned_line)
            cleaned_line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', cleaned_line)

            output_content += cleaned_line + "\n"

    # Fecha lista se necessário
    if ordered_list_open:
        output_content += "</ol>\n"

    return output_content.strip()


def run_program(arg_count, arg_values):
    if arg_count != 2:
        print("Utilização: tpc3.py <ficheiro>")
        return
    
    source_file = arg_values[1]
    html_output = convert_md_to_html(source_file)
    print(html_output)


if __name__ == '__main__':
    run_program(len(sys.argv), sys.argv)
