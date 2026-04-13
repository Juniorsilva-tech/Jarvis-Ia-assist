"""
Project Generator - Jarvis
Gera projetos completos: React, Node.js, Python, etc.
Cria estrutura de pastas, arquivos, instala dependências e abre no VS Code.
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime


def generate_react_project(name: str, description: str = "") -> str:
    """Cria um projeto React completo com Vite, Tailwind e estrutura profissional."""
    from core.models.groq_client import generate_response

    safe_name = name.lower().replace(" ", "-").replace("_", "-")
    output_dir = str(Path.home() / "Desktop" / "Jarvis_Projects" / safe_name)

    if Path(output_dir).exists():
        return f"❌ Pasta já existe: {output_dir}"

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Gera o componente principal com IA
    prompt = f"""Crie um componente React funcional e bonito para: {description or name}
Use Tailwind CSS para estilização.
Retorne APENAS o código JSX do componente App, sem explicações.
O componente deve ser completo e funcional."""

    component_code = generate_response(prompt, task_type="code")

    # Remove blocos markdown se houver
    if "```" in component_code:
        parts = component_code.split("```")
        if len(parts) >= 2:
            component_code = parts[1]
            if component_code.startswith(("jsx", "javascript", "js")):
                component_code = component_code[component_code.index("\n")+1:]

    # Estrutura do projeto
    structure = {
        "package.json": json.dumps({
            "name": safe_name,
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.0.0",
                "vite": "^4.4.0",
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.14",
                "postcss": "^8.4.27"
            }
        }, indent=2),

        "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
""",
        "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
""",
        "postcss.config.js": """export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
""",
        "index.html": f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
        "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
        "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;
""",
        "src/App.jsx": component_code,
        "README.md": f"""# {name}

Criado pelo Jarvis em {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Como rodar

```bash
npm install
npm run dev
```

{description}
""",
    }

    # Cria os arquivos
    for filepath, content in structure.items():
        full_path = Path(output_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    # Abre no VS Code
    try:
        subprocess.Popen(["code", output_dir], shell=True)
    except Exception:
        pass

    return (
        f"✅ Projeto React criado!\n"
        f"📁 Pasta: {output_dir}\n"
        f"Para rodar:\n"
        f"  cd {output_dir}\n"
        f"  npm install\n"
        f"  npm run dev"
    )


def generate_node_project(name: str, description: str = "") -> str:
    """Cria um projeto Node.js/Express completo."""
    from core.models.groq_client import generate_response

    safe_name = name.lower().replace(" ", "-")
    output_dir = str(Path.home() / "Desktop" / "Jarvis_Projects" / safe_name)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Gera o servidor com IA
    prompt = f"""Crie um servidor Node.js com Express para: {description or name}
Inclua rotas REST básicas, middleware de CORS e JSON, e comentários em português.
Retorne APENAS o código JavaScript, sem explicações."""

    server_code = generate_response(prompt, task_type="code")
    if "```" in server_code:
        parts = server_code.split("```")
        if len(parts) >= 2:
            server_code = parts[1]
            if server_code.startswith(("javascript", "js", "node")):
                server_code = server_code[server_code.index("\n")+1:]

    structure = {
        "package.json": json.dumps({
            "name": safe_name,
            "version": "1.0.0",
            "main": "src/server.js",
            "scripts": {"start": "node src/server.js", "dev": "nodemon src/server.js"},
            "dependencies": {"express": "^4.18.2", "cors": "^2.8.5", "dotenv": "^16.3.1"},
            "devDependencies": {"nodemon": "^3.0.1"}
        }, indent=2),
        "src/server.js": server_code,
        ".env": "PORT=3000\nNODE_ENV=development",
        "README.md": f"# {name}\n\nCriado pelo Jarvis.\n\n```bash\nnpm install\nnpm run dev\n```\n",
    }

    for filepath, content in structure.items():
        full_path = Path(output_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    try:
        subprocess.Popen(["code", output_dir], shell=True)
    except Exception:
        pass

    return (
        f"✅ Projeto Node.js criado!\n"
        f"📁 {output_dir}\n"
        f"Para rodar:\n"
        f"  cd {output_dir}\n"
        f"  npm install\n"
        f"  npm run dev"
    )


def generate_python_project(name: str, description: str = "") -> str:
    """Cria um projeto Python completo."""
    from core.models.groq_client import generate_response

    safe_name = name.lower().replace(" ", "_")
    output_dir = str(Path.home() / "Desktop" / "Jarvis_Projects" / safe_name)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    prompt = f"""Crie um script Python completo para: {description or name}
Inclua docstrings, comentários em português e tratamento de erros.
Retorne APENAS o código Python."""

    code = generate_response(prompt, task_type="code")
    if "```" in code:
        parts = code.split("```")
        if len(parts) >= 2:
            code = parts[1]
            if code.startswith("python"):
                code = code[6:]

    structure = {
        f"{safe_name}/main.py": f"# -*- coding: utf-8 -*-\n{code}",
        f"{safe_name}/__init__.py": "",
        "requirements.txt": "# Adicione suas dependências aqui\n",
        "README.md": f"# {name}\n\nCriado pelo Jarvis.\n\n```bash\npython {safe_name}/main.py\n```\n",
    }

    for filepath, content in structure.items():
        full_path = Path(output_dir) / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    try:
        subprocess.Popen(["code", output_dir], shell=True)
    except Exception:
        pass

    return f"✅ Projeto Python criado!\n📁 {output_dir}"
