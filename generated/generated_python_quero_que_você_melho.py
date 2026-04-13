def otimiza_codigo(codigo):
    # Remover comentários desnecessários
    codigo = remover_comentarios(codigo)
    
    # Remover espaços em branco desnecessários
    codigo = remover_espacos(codigo)
    
    # Simplificar condicionais
    codigo = simplificar_condicionais(codigo)
    
    # Remover código duplicado
    codigo = remover_codigo_duplicado(codigo)
    
    return codigo

def remover_comentarios(codigo):
    linhas = codigo.split('\n')
    linhas_limpa = [linha for linha in linhas if not linha.strip().startswith('#')]
    return '\n'.join(linhas_limpa)

def remover_espacos(codigo):
    linhas = codigo.split('\n')
    linhas_limpa = [linha.strip() for linha in linhas]
    return '\n'.join(linhas_limpa)

def simplificar_condicionais(codigo):
    # Essa função é um exemplo e pode ser implementada de acordo com as necessidades
    return codigo

def remover_codigo_duplicado(codigo):
    # Essa função é um exemplo e pode ser implementada de acordo com as necessidades
    return codigo

# Exemplo de uso
codigo = """
# Comentário
if True:
    # Comentário
    print('Hello World')
"""
print(otimiza_codigo(codigo))