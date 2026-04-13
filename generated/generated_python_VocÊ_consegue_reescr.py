def reescrever_codigo(codigo):
    try:
        exec(codigo)
        return "Código reescrito com sucesso"
    except SyntaxError as e:
        return f"Erro de sintaxe: {e}"
    except Exception as e:
        return f"Erro: {e}"

def verificar_erro(codigo):
    try:
        exec(codigo)
        return "Código sem erros"
    except SyntaxError as e:
        return f"Erro de sintaxe: {e}"
    except Exception as e:
        return f"Erro: {e}"

def corrigir_bug(codigo, erro):
    if erro == "SyntaxError":
        return "Erro de sintaxe, verificar indentação e sintaxe"
    elif erro == "Exception":
        return "Erro genérico, verificar código"
    else:
        return "Erro desconhecido"

codigo = "print('Olá, mundo')"
print(reescrever_codigo(codigo))
print(verificar_erro(codigo))
print(corrigir_bug(codigo, "SyntaxError"))