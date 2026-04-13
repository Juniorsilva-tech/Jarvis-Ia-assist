// Definição de uma classe para representar um desenvolvedor full stack
class DesenvolvedorFullStack {
  constructor(nome) {
    // Inicializa o nome do desenvolvedor
    this.nome = nome;
    // Inicializa as habilidades do desenvolvedor
    this.habilidades = [];
  }

  // Método para adicionar habilidades ao desenvolvedor
  adicionarHabilidade(habilidade) {
    // Verifica se a habilidade já existe
    if (!this.habilidades.includes(habilidade)) {
      // Adiciona a habilidade às habilidades do desenvolvedor
      this.habilidades.push(habilidade);
    }
  }

  // Método para remover habilidades do desenvolvedor
  removerHabilidade(habilidade) {
    // Verifica se a habilidade existe
    const indice = this.habilidades.indexOf(habilidade);
    if (indice !== -1) {
      // Remove a habilidade das habilidades do desenvolvedor
      this.habilidades.splice(indice, 1);
    }
  }

  // Método para listar as habilidades do desenvolvedor
  listarHabilidades() {
    // Retorna as habilidades do desenvolvedor
    return this.habilidades;
  }
}

// Criação de um desenvolvedor full stack
const desenvolvedor = new DesenvolvedorFullStack("Especialista em JavaScript");

// Adicionando habilidades ao desenvolvedor
desenvolvedor.adicionarHabilidade("JavaScript");
desenvolvedor.adicionarHabilidade("HTML");
desenvolvedor.adicionarHabilidade("CSS");
desenvolvedor.adicionarHabilidade("Node.js");
desenvolvedor.adicionarHabilidade("React");
desenvolvedor.adicionarHabilidade("MongoDB");

// Listando as habilidades do desenvolvedor
console.log("Habilidades do desenvolvedor:", desenvolvedor.listarHabilidades());

// Removendo habilidades do desenvolvedor
desenvolvedor.removerHabilidade("CSS");

// Listando as habilidades do desenvolvedor após remoção
console.log("Habilidades do desenvolvedor após remoção:", desenvolvedor.listarHabilidades());