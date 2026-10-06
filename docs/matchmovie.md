# MatchMovie

Buscador de filmes construído com Next.js, TypeScript e Tailwind CSS, consumindo a API pública da [TMDB](https://www.themoviedb.org).

Projeto de estudo focado em aprender o App Router do Next.js — Server e Client Components, rotas dinâmicas, Route Handlers e as convenções de arquivo do framework.

---

## Funcionalidades

- **Filmes populares** — listagem em grid responsivo, buscada no servidor
- **Destaque (hero)** — o filme mais popular do momento em evidência, com backdrop e nota
- **Busca** — com _debounce_ de 500ms, evitando uma requisição por tecla digitada
- **Página de detalhes** — sinopse, gêneros, duração, nota e imagem de fundo do filme
- **Scroll infinito** — novas páginas carregam sozinhas conforme o usuário rola, via `IntersectionObserver`
- **Estados de carregamento** — skeletons que imitam o layout final, via `loading.tsx`
- **Tratamento de erros** — _error boundaries_ com botão de nova tentativa, via `error.tsx`

## Stack

| Tecnologia | Versão | Papel |
|---|---|---|
| [Next.js](https://nextjs.org) | 16.3 | Framework (App Router) |
| [React](https://react.dev) | 19.2 | Biblioteca de UI |
| [TypeScript](https://www.typescriptlang.org) | 5 | Tipagem estática |
| [Tailwind CSS](https://tailwindcss.com) | 4 | Estilização |
| [TMDB API](https://developer.themoviedb.org/docs) | v3 | Dados dos filmes |

---

## Rodando localmente

**1. Clone o repositório e instale as dependências**

```bash
git clone https://github.com/kawoliv/match.movie.git
cd match.movie
npm install
```

**2. Configure a chave da API**

Crie um arquivo `.env.local` na raiz do projeto:

```env
TMDB_API_KEY=sua_chave_aqui
```

Para obter a chave: crie uma conta gratuita na [TMDB](https://www.themoviedb.org/signup) e gere uma API Key em **Configurações → API**.

> A variável **não** tem o prefixo `NEXT_PUBLIC_` de propósito — assim ela só é lida no servidor e nunca é exposta ao navegador.

**3. Inicie o servidor de desenvolvimento**

```bash
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000).

---

## Estrutura

```
src/
├── app/
│   ├── api/
│   │   ├── movies/route.ts     # Paginação dos populares (ponte para a TMDB)
│   │   └── search/route.ts     # Busca (ponte para a TMDB)
│   ├── filme/[id]/
│   │   ├── page.tsx            # Página de detalhes (rota dinâmica)
│   │   ├── loading.tsx         # Skeleton da página de detalhes
│   │   └── error.tsx           # Error boundary da página de detalhes
│   ├── layout.tsx              # Layout raiz: fontes, navbar e footer
│   ├── page.tsx                # Home
│   ├── loading.tsx             # Skeleton da home
│   ├── error.tsx               # Error boundary da home
│   └── globals.css             # Tailwind e tokens de tema
├── components/
│   ├── Hero.tsx                # Filme em destaque
│   ├── MovieGrid.tsx           # Grid + estado da busca e paginação
│   ├── MovieCard.tsx           # Card individual
│   ├── SearchBar.tsx           # Campo de busca com debounce
│   ├── Navbar.tsx
│   └── Footer.tsx
├── lib/
│   └── tmdb.ts                 # Funções de acesso à API da TMDB
└── types/
    └── movie.ts                # Tipos da resposta da API
```

---

## Decisões técnicas

**Por que existem Route Handlers (`/api/*`)?**
A chave da TMDB só pode viver no servidor. A home busca os filmes diretamente em um Server Component, mas a busca e o "carregar mais" acontecem no navegador — então essas requisições passam por rotas internas do próprio Next.js, que conversam com a TMDB em nome do cliente. O navegador nunca vê a chave.

**Server vs Client Components**
As páginas são Server Components (buscam dados antes de enviar o HTML pronto). Só os componentes que precisam de interatividade — `MovieGrid` e `SearchBar` — são Client Components (`"use client"`), porque dependem de estado e de eventos do usuário.

**Debounce na busca**
Cada tecla digitada dispararia uma requisição. Um `setTimeout` de 500ms, cancelado pela função de limpeza do `useEffect` a cada nova tecla, garante que só a última digitação vire uma chamada de verdade.

**Filmes repetidos no scroll infinito**
O ranking de populares da TMDB é reordenado entre requisições, então um filme da página 1 pode reaparecer na página 2 e quebrar a unicidade das `key` do React. Cada página nova é filtrada contra os IDs já carregados — por isso algumas páginas acrescentam menos de 20 filmes.

**Estado derivado no `MovieGrid`**
A lista exibida é calculada (`query ? results : popularMovies`) em vez de duplicada em um terceiro estado. Isso evita que as duas fiquem dessincronizadas — limpar o campo de busca volta automaticamente para os populares.

---

## Próximos passos

- [ ] Elenco, trailer e filmes recomendados na página de detalhes
- [ ] Favoritos persistidos em `localStorage`
- [ ] Busca refletida na URL (`/busca?q=...`), permitindo compartilhar resultados
- [ ] `generateMetadata` para título e preview dinâmicos por filme
- [ ] Deploy na Vercel

---

## Créditos

Dados e imagens fornecidos pela [TMDB](https://www.themoviedb.org). Este produto usa a API da TMDB, mas não é endossado ou certificado pela TMDB.
