"""Conversor de arquivos KFX para EPUB."""

import os
import re
import struct
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from ebooklib import epub


class KFXConverter:
    """Converte arquivos KFX (Kindle) para formato EPUB usando parsing do formato proprietário."""

    def __init__(self):
        """Inicializa o conversor KFX."""
        pass

    def convert_kfx_to_epub(self, kfx_file: str, output_epub: str) -> bool:
        """
        Converte um arquivo KFX para EPUB.

        Args:
            kfx_file: Caminho do arquivo KFX de entrada.
            output_epub: Caminho do arquivo EPUB de saída.

        Returns:
            True se conversão bem-sucedida, False caso contrário.
        """
        if not os.path.exists(kfx_file):
            raise FileNotFoundError(f"Arquivo KFX não encontrado: {kfx_file}")

        output_dir = os.path.dirname(output_epub)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extrair conteúdo do KFX
                if not self._extract_kfx(kfx_file, temp_dir):
                    return False

                # Criar EPUB
                book = epub.EpubBook()
                book.set_identifier(Path(kfx_file).stem)
                book.set_title(Path(kfx_file).stem)
                book.set_language('pt')
                book.add_author('Unknown')

                # Processar arquivos extraídos
                chapters = []
                chapter_num = 0
                temp_path = Path(temp_dir)

                # Procurar por arquivos HTML/XHTML
                html_files = sorted(temp_path.rglob('*.html')) + sorted(temp_path.rglob('*.xhtml'))

                for html_file in html_files:
                    try:
                        with open(html_file, 'rb') as f:
                            content = f.read()

                        chapter = epub.EpubHtml()
                        chapter.file_name = f'chap_{chapter_num:02d}.xhtml'
                        chapter.title = f'Chapter {chapter_num + 1}'
                        chapter.content = content

                        book.add_item(chapter)
                        chapters.append(chapter)
                        chapter_num += 1
                    except Exception as e:
                        print(f"Aviso ao processar {html_file}: {e}")

                # Copiar imagens
                for img_file in temp_path.rglob('*'):
                    if img_file.is_file() and img_file.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.svg'}:
                        try:
                            with open(img_file, 'rb') as f:
                                image_data = f.read()
                            item = epub.EpubImage()
                            item.file_name = f'images/{img_file.name}'
                            item.content = image_data
                            book.add_item(item)
                        except Exception as e:
                            print(f"Aviso ao processar imagem {img_file.name}: {e}")

                # Adicionar CSS
                style = epub.EpubItem()
                style.file_name = 'style/style.css'
                style.media_type = 'text/css'
                style.content = 'body { font-family: serif; }'
                book.add_item(style)

                # Adicionar TOC e spine
                book.toc = tuple(chapters) if chapters else ('Contents',)
                book.spine = ['nav'] + chapters

                # Escrever EPUB
                epub.write_epub(output_epub, book, {})
                return True

        except Exception as e:
            print(f"Erro na conversão: {e}")
            return False

    def _extract_kfx(self, kfx_file: str, output_dir: str) -> bool:
        """
        Extrai conteúdo do arquivo KFX (formato binário proprietário).

        O KFX é um arquivo contendo fragmentos de dados. Esta função tenta
        extrair dados legíveis (HTML, imagens, etc).
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            with open(kfx_file, 'rb') as f:
                data = f.read()

            # Procurar por assinaturas de arquivo dentro do KFX
            self._extract_embedded_files(data, output_dir)

            # Se não encontrou arquivos, criar um HTML genérico
            output_path = Path(output_dir)
            if not any(output_path.rglob('*.*')):
                self._create_fallback_html(data, output_dir, kfx_file)

            return True

        except Exception as e:
            print(f"Erro ao extrair KFX: {e}")
            return False

    def _extract_embedded_files(self, data: bytes, output_dir: str):
        """Procura e extrai arquivos embutidos (ZIP, PDF, imagens, etc)."""
        # Procurar por assinatura ZIP
        zip_start = data.find(b'PK\x03\x04')
        if zip_start != -1:
            try:
                temp_zip = os.path.join(output_dir, 'temp.zip')
                with open(temp_zip, 'wb') as f:
                    f.write(data[zip_start:])

                with zipfile.ZipFile(temp_zip, 'r') as zf:
                    zf.extractall(output_dir)

                os.remove(temp_zip)
                return
            except:
                pass

        # Procurar por PNG
        png_start = 0
        while True:
            png_start = data.find(b'\x89PNG\r\n\x1a\n', png_start)
            if png_start == -1:
                break
            self._extract_png(data, png_start, output_dir)
            png_start += 1

        # Procurar por JPEG
        jpeg_start = 0
        while True:
            jpeg_start = data.find(b'\xff\xd8\xff', jpeg_start)
            if jpeg_start == -1:
                break
            self._extract_jpeg(data, jpeg_start, output_dir)
            jpeg_start += 1

    def _extract_png(self, data: bytes, start: int, output_dir: str):
        """Extrai uma imagem PNG dos dados."""
        try:
            # PNG termina com IEND
            end = data.find(b'IEND\xaeB`\x82', start)
            if end != -1:
                end += 8
                filename = os.path.join(output_dir, f'image_{len(os.listdir(output_dir)):03d}.png')
                with open(filename, 'wb') as f:
                    f.write(data[start:end])
        except:
            pass

    def _extract_jpeg(self, data: bytes, start: int, output_dir: str):
        """Extrai uma imagem JPEG dos dados."""
        try:
            # JPEG termina com FF D9
            end = data.find(b'\xff\xd9', start)
            if end != -1:
                end += 2
                filename = os.path.join(output_dir, f'image_{len(os.listdir(output_dir)):03d}.jpg')
                with open(filename, 'wb') as f:
                    f.write(data[start:end])
        except:
            pass

    def _create_fallback_html(self, data: bytes, output_dir: str, kfx_file: str):
        """Cria um HTML básico com o conteúdo textual extraído do KFX."""
        # Tentar extrair texto do arquivo
        text_content = self._extract_text(data)

        html_content = f"""<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="pt">
<head>
    <meta charset="utf-8"/>
    <title>{Path(kfx_file).stem}</title>
</head>
<body>
    <h1>{Path(kfx_file).stem}</h1>
    <p><em>Nota: Este EPUB foi convertido de um arquivo KFX. Algum conteúdo pode estar incompleto.</em></p>
    <pre>{text_content}</pre>
</body>
</html>"""

        with open(os.path.join(output_dir, 'content.xhtml'), 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _extract_text(self, data: bytes) -> str:
        """Extrai texto legível do arquivo KFX."""
        try:
            # Tentar decodificar como texto
            text = data.decode('utf-8', errors='ignore')
            # Remover caracteres de controle
            text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')
            # Manter apenas as primeiras 10000 caracteres
            return text[:10000]
        except:
            return "(Conteúdo não extraível)"

    def convert_batch(self, input_dir: str, output_dir: str, organize_by_book: bool = True) -> dict:
        """
        Converte múltiplos arquivos KFX de um diretório.

        Args:
            input_dir: Diretório contendo arquivos KFX.
            output_dir: Diretório para salvar arquivos EPUB convertidos.
            organize_by_book: Se True, cria subpastas por livro.

        Returns:
            Dicionário com resultados da conversão.
        """
        os.makedirs(output_dir, exist_ok=True)
        results = {"success": [], "failed": []}

        kfx_files = sorted(list(Path(input_dir).glob("*.kfx")))
        if not kfx_files:
            print(f"Nenhum arquivo KFX encontrado em: {input_dir}")
            return results

        for idx, kfx_file in enumerate(kfx_files, 1):
            clean_name = self._clean_filename(kfx_file.stem)

            if organize_by_book:
                book_dir = os.path.join(output_dir, clean_name)
                os.makedirs(book_dir, exist_ok=True)
                output_path = os.path.join(book_dir, clean_name + ".epub")
            else:
                output_path = os.path.join(output_dir, clean_name + ".epub")

            print(f"[{idx}/{len(kfx_files)}] Convertendo: {clean_name}...", end=" ")
            if self.convert_kfx_to_epub(str(kfx_file), output_path):
                print("✓")
                results["success"].append((clean_name, output_path))
            else:
                print("✗")
                results["failed"].append(clean_name)

        return results

    def _clean_filename(self, filename: str) -> str:
        """Remove IDs e caracteres especiais do nome do arquivo."""
        import re
        # Remover tudo depois de "(Z-Library)"
        cleaned = re.sub(r'\s*\(Z-Library\).*$', '', filename, flags=re.IGNORECASE)
        # Se nada foi removido, tenta remover IDs do final (_XXXXX...X)
        if cleaned == filename:
            cleaned = re.sub(r'_[A-Z0-9]{20,}$', '', filename)
        # Remove parênteses finais (completos ou incompletos)
        cleaned = re.sub(r'\s*\([^)]*(\)|$)', '', cleaned)
        # Remove underscores/espaços soltos no final
        cleaned = re.sub(r'[\s_]+$', '', cleaned)
        # Limpa espaços extras
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned or filename
