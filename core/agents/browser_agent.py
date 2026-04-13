import webbrowser


class BrowserAgent:

    def run(self, step: dict):

        query = step.get("query")

        if not query:
            return "Nenhuma busca."

        url = f"https://www.google.com/search?q={query}"

        webbrowser.open(url)

        return f"Pesquisando: {query}"