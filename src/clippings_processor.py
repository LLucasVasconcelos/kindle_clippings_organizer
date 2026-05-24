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

    def export_to_text(self, clippings: List[Clipping], output_file: str) -> bool:
        """
        Exporta anotações para arquivo de texto formatado.

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
                # Cabeçalho
                f.write(f"{'='*60}\n")
                f.write(f"ANOTAÇÕES - {clippings[0].book_title}\n")
                f.write(f"Autor: {clippings[0].author}\n")
                f.write(f"Total de anotações: {len(clippings)}\n")
                f.write(f"{'='*60}\n\n")

                # Anotações
                for idx, clipping in enumerate(clippings, 1):
                    f.write(f"[{idx}] {clipping.clip_type}\n")
                    f.write(f"Localização: {clipping.page_location}\n")
                    f.write(f"Data: {clipping.date}\n")
                    f.write(f"\n{clipping.content}\n")
                    f.write("\n" + "-" * 60 + "\n\n")

            return True
        except Exception as e:
            print(f"❌ Erro ao exportar: {e}")
            return False
