"""
Processador de anotações do My Clippings.txt do Kindle
Lê, processa e exporta anotações do Kindle em arquivos de texto
"""

import os
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Clipping:
    """Representa uma anotação (clipping) do Kindle."""
    book_title: str
    author: str
    content: str
    page_location: str
    clip_type: str
    date: str


class ClippingsProcessor:
    """Processa o arquivo My Clippings.txt do Kindle."""

    SEPARATOR = "=" * 10

    def __init__(self, clippings_file: str):
        """
        Inicializa o processador de anotações.

        Args:
            clippings_file: Caminho para o arquivo My Clippings.txt
        """
        self.clippings_file = clippings_file

    def read_clippings(self) -> List[Clipping]:
        """
        Lê e processa o arquivo My Clippings.txt.

        Returns:
            Lista de anotações (Clipping)
        """
        clippings = []

        if not os.path.exists(self.clippings_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.clippings_file}")

        with open(self.clippings_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Dividir por separador (==========)
        entries = content.split(self.SEPARATOR)

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            clipping = self._parse_entry(entry)
            if clipping:
                clippings.append(clipping)

        return clippings

    def _parse_entry(self, entry: str) -> Clipping:
        """
        Extrai informações de uma entrada individual.

        Formato esperado:
            Título do Livro (Autor)
            - Localização | Tipo | Data

            Conteúdo da anotação

        Returns:
            Objeto Clipping com os dados extraídos
        """
        lines = entry.split("\n")

        if len(lines) < 3:
            return None

        header = lines[0].strip()
        metadata = lines[1].strip()
        content = "\n".join(lines[2:]).strip()

        if not content:
            return None

        book_title, author = self._parse_header(header)
        page_loc, clip_type, date = self._parse_metadata(metadata)

        return Clipping(
            book_title=book_title,
            author=author,
            content=content,
            page_location=page_loc,
            clip_type=clip_type,
            date=date,
        )

    def _parse_header(self, header: str) -> Tuple[str, str]:
        """Extrai título do livro e autor."""
        match = re.match(r"(.+?)\s*\((.+?)\)", header)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return header, "Desconhecido"

    def _parse_metadata(self, metadata: str) -> Tuple[str, str, str]:
        """Extrai localização, tipo e data da anotação."""
        pattern = r"- (.+?)\s*\|\s*(.+?)\s*\|\s*(.+)"
        match = re.match(pattern, metadata)

        if match:
            return match.group(1).strip(), match.group(2).strip(), match.group(3).strip()
        return "", "", ""

    def group_by_book(self, clippings: List[Clipping]) -> Dict[str, List[Clipping]]:
        """
        Agrupa anotações por livro.

        Args:
            clippings: Lista de anotações

        Returns:
            Dicionário com livros como chaves e lista de anotações como valores
        """
        grouped = {}
        for clipping in clippings:
            key = clipping.book_title
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(clipping)

        return grouped

    def export_to_markdown(self, clippings: List[Clipping], output_file: str) -> bool:
        """
        Exporta anotações para arquivo Markdown otimizado para Obsidian.

        Args:
            clippings: Lista de anotações do livro
            output_file: Caminho do arquivo de saída

        Returns:
            True se exportação bem-sucedida
        """
        try:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                # Frontmatter YAML
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")

                book_title = clippings[0].book_title
                author = clippings[0].author

                f.write("---\n")
                f.write(f'title: "{book_title}"\n')
                f.write(f'author: "{author}"\n')
                f.write(f"processed: {today}\n")
                f.write(f"total_clippings: {len(clippings)}\n")
                f.write("---\n\n")

                # Título do livro
                f.write(f"# 📚 {book_title}\n\n")
                f.write(f"**Autor:** {author}  \n")
                f.write(f"**Total de anotações:** {len(clippings)}  \n")
                f.write(f"**Processado:** {today}\n\n")

                f.write("---\n\n")

                # Anotações
                f.write("## Anotações\n\n")

                for idx, clipping in enumerate(clippings, 1):
                    # Header da anotação
                    f.write(f"### [{idx}] {clipping.clip_type}\n\n")

                    # Metadados
                    f.write(f"- **Localização:** {clipping.page_location}\n")
                    f.write(f"- **Data:** {clipping.date}\n")
                    f.write(f"- **Tags:** #kindle #anotação #{self._sanitize_tag(book_title)}\n\n")

                    # Conteúdo (blockquote)
                    f.write("> ")
                    f.write(clipping.content.replace("\n", "\n> "))
                    f.write("\n\n")
                    f.write("---\n\n")

            return True
        except Exception as e:
            print(f"❌ Erro ao exportar: {e}")
            return False

    def _sanitize_tag(self, text: str) -> str:
        """Converte texto para tag válida do Obsidian."""
        return text.lower().replace(" ", "-").replace("'", "").replace('"', '')

    def export_index(self, grouped: Dict[str, List[Clipping]], output_file: str = "output/INDEX.md") -> bool:
        """
        Cria um índice de todos os livros processados.

        Args:
            grouped: Dicionário com livros agrupados
            output_file: Caminho do arquivo índice

        Returns:
            True se exportação bem-sucedida
        """
        try:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write('title: "Índice de Anotações Kindle"\n')
                f.write(f"generated: {today}\n")
                f.write(f"total_books: {len(grouped)}\n")
                f.write("---\n\n")

                f.write("# 📚 Índice de Anotações Kindle\n\n")
                f.write(f"**Data de processamento:** {today}  \n")
                f.write(f"**Total de livros:** {len(grouped)}  \n")
                f.write(f"**Total de anotações:** {sum(len(clips) for clips in grouped.values())}\n\n")

                f.write("---\n\n")

                # Índice de livros
                f.write("## 📖 Livros\n\n")

                for book_title, clippings in sorted(grouped.items()):
                    author = clippings[0].author if clippings else "Desconhecido"
                    tag = self._sanitize_tag(book_title)

                    # Cria link interno do Obsidian
                    f.write(f"### [[{book_title}/anotacoes|{book_title}]]\n\n")
                    f.write(f"**Autor:** {author}  \n")
                    f.write(f"**Anotações:** {len(clippings)}  \n")
                    f.write(f"**Tags:** #{tag}\n\n")

                f.write("---\n\n")
                f.write("*Criado com Kindle Clippings Organizer para Obsidian*\n")

            return True
        except Exception as e:
            print(f"❌ Erro ao criar índice: {e}")
            return False
