import logging
import sys

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Sistema:
    def __init__(self):
        self.bugs = []
        self.problemas_de_som = []

    def adicionar_bug(self, descricao):
        self.bugs.append(descricao)
        logging.warning(f'Bug adicionado: {descricao}')

    def adicionar_problema_de_som(self, descricao):
        self.problemas_de_som.append(descricao)
        logging.warning(f'Problema de som adicionado: {descricao}')

    def remover_bug(self, descricao):
        if descricao in self.bugs:
            self.bugs.remove(descricao)
            logging.info(f'Bug removido: {descricao}')
        else:
            logging.error(f'Bug não encontrado: {descricao}')

    def remover_problema_de_som(self, descricao):
        if descricao in self.problemas_de_som:
            self.problemas_de_som.remove(descricao)
            logging.info(f'Problema de som removido: {descricao}')
        else:
            logging.error(f'Problema de som não encontrado: {descricao}')

    def listar_bugs(self):
        logging.info('Bugs:')
        for bug in self.bugs:
            logging.info(bug)

    def listar_problemas_de_som(self):
        logging.info('Problemas de som:')
        for problema in self.problemas_de_som:
            logging.info(problema)

def main():
    sistema = Sistema()

    while True:
        print('1. Adicionar bug')
        print('2. Adicionar problema de som')
        print('3. Remover bug')
        print('4. Remover problema de som')
        print('5. Listar bugs')
        print('6. Listar problemas de som')
        print('7. Sair')

        escolha = input('Escolha uma opção: ')

        if escolha == '1':
            descricao = input('Descrição do bug: ')
            sistema.adicionar_bug(descricao)
        elif escolha == '2':
            descricao = input('Descrição do problema de som: ')
            sistema.adicionar_problema_de_som(descricao)
        elif escolha == '3':
            descricao = input('Descrição do bug a remover: ')
            sistema.remover_bug(descricao)
        elif escolha == '4':
            descricao = input('Descrição do problema de som a remover: ')
            sistema.remover_problema_de_som(descricao)
        elif escolha == '5':
            sistema.listar_bugs()
        elif escolha == '6':
            sistema.listar_problemas_de_som()
        elif escolha == '7':
            sys.exit(0)
        else:
            logging.error('Opção inválida')

if __name__ == '__main__':
    main()