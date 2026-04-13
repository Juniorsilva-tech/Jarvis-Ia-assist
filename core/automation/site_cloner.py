"""
Site Cloner - Jarvis
Clona sites completos: baixa HTML, CSS, JS, imagens.
Analisa o design e gera uma versão reproduzível.
"""

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def clone_site(url: str, output_dir: str = "") -> str:
    """
    Clona um site completo.
    Baixa HTML, CSS, JS e imagens.
    Salva numa pasta local pronta para abrir no browser.
    """
    if not url.startswith("http"):
        url = "https://" + url

    # Pasta de saída
    domain = urlparse(url).netloc.replace("www.", "")
    if not output_dir:
        output_dir = str(Path.home() / "Desktop" / "Jarvis_Sites" / domain)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        # 1. Baixa o HTML principal
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # 2. Encontra todos os assets
        css_links  = re.findall(r'href=["\']([^"\']+\.css[^"\']*)["\']', html)
        js_links   = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html)
        img_links  = re.findall(r'src=["\']([^"\']+\.(png|jpg|jpeg|gif|svg|webp)[^"\']*)["\']', html)

        downloaded = []
        failed = []

        # 3. Baixa CSS
        for link in css_links[:10]:
            result = _download_asset(url, link, output_dir, "css")
            if result:
                downloaded.append(result)
                html = html.replace(link, result)

        # 4. Baixa JS
        for link in js_links[:10]:
            result = _download_asset(url, link, output_dir, "js")
            if result:
                downloaded.append(result)
                html = html.replace(link, result)

        # 5. Baixa imagens
        for link, _ in img_links[:20]:
            result = _download_asset(url, link, output_dir, "images")
            if result:
                downloaded.append(result)
                html = html.replace(link, result)

        # 6. Salva HTML modificado
        index_path = Path(output_dir) / "index.html"
        index_path.write_text(html, encoding="utf-8")

        # 7. Gera análise do design
        analysis = _analyze_design(html, url)
        analysis_path = Path(output_dir) / "ANALISE_DESIGN.md"
        analysis_path.write_text(analysis, encoding="utf-8")

        return (
            f"✅ Site clonado com sucesso!\n"
            f"📁 Pasta: {output_dir}\n"
            f"📄 Arquivos baixados: {len(downloaded)}\n"
            f"🌐 Abra o arquivo: {index_path}\n"
            f"📊 Análise de design: {analysis_path}"
        )

    except requests.ConnectionError:
        return f"❌ Não consegui acessar {url}. Verifique a conexão ou URL."
    except Exception as e:
        return f"❌ Erro ao clonar: {e}"


def _download_asset(base_url: str, asset_url: str, output_dir: str, subfolder: str) -> str:
    """Baixa um asset e retorna o caminho local relativo."""
    try:
        full_url = urljoin(base_url, asset_url)
        parsed = urlparse(full_url)

        # Nome do arquivo
        filename = Path(parsed.path).name
        if not filename or '.' not in filename:
            return ""

        folder = Path(output_dir) / subfolder
        folder.mkdir(exist_ok=True)
        filepath = folder / filename

        if not filepath.exists():
            resp = requests.get(full_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            filepath.write_bytes(resp.content)

        return f"{subfolder}/{filename}"
    except Exception:
        return ""


def _analyze_design(html: str, url: str) -> str:
    """Analisa o design do site e gera um relatório."""
    lines = [f"# Análise de Design — {url}\n"]

    # Cores encontradas
    colors = list(set(re.findall(r'#[0-9a-fA-F]{3,6}', html)))[:20]
    if colors:
        lines.append(f"## Cores encontradas\n" + ", ".join(colors))

    # Fontes
    fonts = list(set(re.findall(r"font-family:\s*['\"]?([^;'\"]+)['\"]?", html)))[:10]
    if fonts:
        lines.append(f"\n## Fontes\n" + ", ".join(fonts))

    # Frameworks detectados
    frameworks = []
    if "bootstrap" in html.lower(): frameworks.append("Bootstrap")
    if "tailwind" in html.lower(): frameworks.append("Tailwind CSS")
    if "react" in html.lower(): frameworks.append("React")
    if "vue" in html.lower(): frameworks.append("Vue.js")
    if "angular" in html.lower(): frameworks.append("Angular")
    if "jquery" in html.lower(): frameworks.append("jQuery")
    if frameworks:
        lines.append(f"\n## Frameworks detectados\n" + ", ".join(frameworks))

    # Estrutura
    sections = re.findall(r'<(header|nav|main|section|footer|aside)[^>]*>', html, re.I)
    if sections:
        lines.append(f"\n## Estrutura HTML\n" + ", ".join(set(s.lower() for s in sections)))

    lines.append(f"\n## Como reproduzir\n"
                 f"Este site usa {', '.join(frameworks) if frameworks else 'HTML/CSS puro'}.\n"
                 f"Para criar algo similar:\n"
                 f"1. Copie o index.html desta pasta\n"
                 f"2. Adapte o conteúdo mantendo a estrutura\n"
                 f"3. Os arquivos CSS e JS já estão na pasta")

    return "\n".join(lines)
