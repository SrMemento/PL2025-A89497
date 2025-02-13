sum_total = 0
current_number = ''
state = True  # estado inicializado como On
i = 0
text = input().strip()

while i < len(text):
    cmd_found = False

    # 2. Sempre que encontrar a string “Off” em qualquer combinação de maiúsculas e minúsculas, esse comportamento é desligado;
    if i + 3 <= len(text):
        substr = text[i:i+3].lower()
        if substr == 'off':
            # adiciona current_number ao sum se state for ON
            if state and current_number:
                sum_total += int(current_number)
                current_number = ''
            state = False
            i += 3
            cmd_found = True

    # 3. Sempre que encontrar a string “On” em qualquer combinação de maiúsculas e minúsculas, esse comportamento é novamente ligado;
    if not cmd_found and i + 2 <= len(text):
        substr = text[i:i+2].lower()
        if substr == 'on':
            # adiciona current_number ao sum se state for ON
            if state and current_number:
                sum_total += int(current_number)
                current_number = ''
            state = True
            i += 2
            cmd_found = True

    if not cmd_found:
        char = text[i]
        # 4. Sempre que encontrar o caráter “=”, o resultado da soma é colocado na saída.
        if char == '=':
            # adiciona current_number ao sum se state for ON e faz print
            if state and current_number:
                sum_total += int(current_number)
                current_number = ''
            print(sum_total)
        elif state:
            # 1. Pretende-se um programa que some todas as sequências de dígitos que encontre num texto;
            if char.isdigit():
                current_number += char
            else:
                if current_number:
                    sum_total += int(current_number)
                    current_number = ''
        else:
            # Estado OFF, faz print se encontrar =
            if char == '=':
                print(sum_total)
        i += 1

if state and current_number:
    sum_total += int(current_number)
