"""
Processador de Anotações Kindle
Lê My Clippings.txt e organiza anotações por livro
"""

import os
from clippings_processor import ClippingsProcessor


def main():
    """Menu principal da aplicação."""
    print("="*60)
    print("Processador de Anotações Kindle")
    print("="*60)
    print()

    while True:
        print("1. Processar My Clippings.txt")
        print("0. Sair")
        print()

        choice = input("Opção: ").strip()

        if choice == "1":
            process_clippings()
        elif choice == "0":
            print("Saindo...")
            break
        else:
            print("❌ Opção inválida!\n")


def process_clippings():
    """Processa arquivo My Clippings.txt e organiza anotações por livro."""
    clippings_file = "input/My Clippings.txt"
    output_dir = "output"

    if not os.path.exists(clippings_file):
        print(f"\n❌ Erro: {clippings_file} não encontrado\n")
        return

    print(f"\n📖 Processando anotações...\n")

    try:
        # Carregar e processar anotações
        processor = ClippingsProcessor(clippings_file)
        clippings = processor.read_clippings()
        grouped = processor.group_by_book(clippings)

        print(f"✓ {len(clippings)} anotações carregadas")
        print(f"✓ {len(grouped)} livros identificados\n")

        # Salvar anotações por livro em Markdown
        print("Salvando anotações em Markdown:\n")
        for book_title, book_clippings in sorted(grouped.items()):
            book_dir = os.path.join(output_dir, book_title)
            os.makedirs(book_dir, exist_ok=True)

            anotacoes_file = os.path.join(book_dir, "anotacoes.md")
            if processor.export_to_markdown(book_clippings, anotacoes_file):
                size_kb = os.path.getsize(anotacoes_file) / 1024
                print(f"  ✓ {book_title}")
                print(f"    └─ {len(book_clippings)} anotações ({size_kb:.1f} KB)")

        # Gerar índice
        print(f"\n📑 Gerando índice...\n")
        index_file = os.path.join(output_dir, "INDEX.md")
        if processor.export_index(grouped, index_file):
            size_kb = os.path.getsize(index_file) / 1024
            print(f"  ✓ Índice criado ({size_kb:.1f} KB)")

        print(f"\n✓ Processamento concluído!")
        print(f"📁 Anotações salvas em: output/")
        print(f"📑 Índice: output/INDEX.md\n")

    except Exception as e:
        print(f"❌ Erro: {e}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelado pelo usuário.")
