# 📚 Processador de Anotações Kindle para Obsidian

Ferramenta para processar e organizar anotações do Kindle em arquivos Markdown para integração com Obsidian.

## 🎯 O que faz?

- Lê o arquivo `My Clippings.txt` do seu Kindle
- Extrai todas as anotações
- Organiza cada livro em uma pasta separada
- Salva em formato **Markdown** otimizado para Obsidian
- Gera **índice geral** com todos os livros
- Inclui metadados em **YAML frontmatter** para Obsidian

## 🚀 Como usar?

### 1. Setup inicial (primeira vez)

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências (se houver)
pip install -r requirements.txt
```

### 2. Colocar seu arquivo

Copie seu `My Clippings.txt` para a pasta `input/`:

```bash
cp "My Clippings.txt" input/
```

### 3. Executar

```bash
python main.py
```

Escolha opção **1** no menu.

## 📁 Resultado

As anotações serão organizadas em `output/` como arquivos Markdown:

```
output/
├── INDEX.md                 ← Índice de todos os livros
├── Livro 1/
│   └── anotacoes.md         ← Anotações do livro
├── Livro 2/
│   └── anotacoes.md
└── ... (mais livros)
```

### 📄 Formato dos arquivos

Cada arquivo `.md` contém:
- **YAML frontmatter** com metadados (título, autor, data)
- **Tags Obsidian** para categorização (`#kindle`, `#anotação`, `#livro`)
- **Links internos** do Obsidian (`[[link]]`)
- **Blockquotes** para destaque das anotações
- **Metadados de localização e data** para cada clipping

## 📋 Estrutura

```
.
├── input/                    ← Coloque My Clippings.txt aqui
├── output/                   ← Anotações organizadas
├── main.py                   ← Menu principal
├── clippings_processor.py    ← Processa anotações
├── venv/                     ← Ambiente virtual
└── README.md
```

## ⚙️ Dependências

- Python 3.8+

## 📝 Exemplo de saída

### Arquivo gerado: `output/Nome do Livro/anotacoes.md`

```markdown
---
title: "Clean Code"
author: "Robert C. Martin"
processed: 2026-05-24
total_clippings: 15
---

# 📚 Clean Code

**Autor:** Robert C. Martin  
**Total de anotações:** 15  
**Processado:** 2026-05-24

---

## Anotações

### [1] Highlight

- **Localização:** p. 42
- **Data:** 15 May 2026
- **Tags:** #kindle #anotação #clean-code

> O código deve ser tão claro que outro programador possa entendê-lo facilmente...

---

### [2] Bookmark

- **Localização:** p. 87
- **Data:** 18 May 2026
- **Tags:** #kindle #anotação #clean-code

> Funções bem nomeadas são o primeiro passo para código legível...

---
```

### Arquivo gerado: `output/INDEX.md`

```markdown
---
title: "Índice de Anotações Kindle"
generated: 2026-05-24
total_books: 3
---

# 📚 Índice de Anotações Kindle

**Data de processamento:** 2026-05-24  
**Total de livros:** 3  
**Total de anotações:** 47

---

## 📖 Livros

### [[Clean Code/anotacoes|Clean Code]]

**Autor:** Robert C. Martin  
**Anotações:** 15  
**Tags:** #clean-code

### [[Design Patterns/anotacoes|Design Patterns]]

**Autor:** Gang of Four  
**Anotações:** 18  
**Tags:** #design-patterns

...
```

## 💡 Como usar no Obsidian

1. Copie a pasta `output/` para dentro do seu vault do Obsidian
2. Abra `INDEX.md` para navegar entre os livros
3. Clique nos links para abrir as anotações de cada livro
4. **Adicione tags personalizadas** nas seções conforme precisar
5. **Crie anotações locais** referenciando os clips com `[[]]`

## 💾 Seu `My Clippings.txt` fica em:

- **Kindle USB**: `/Kindle/documents/My Clippings.txt`
- **Kindle Cloud**: Na pasta de documentos sincronizados

---

**Processador otimizado para Obsidian!**
