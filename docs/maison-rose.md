# Maison Rosé

Site de encomendas de uma confeitaria artesanal — cardápio com carrinho de compras, checkout e confirmação de pedido.

## Stack

- PHP (sem framework, sem banco de dados)
- HTML/CSS/JavaScript puro
- Fontes: Playfair Display + Nunito (Google Fonts)

## Como rodar

Requer um servidor com PHP (ex.: [XAMPP](https://www.apachefriends.org/)).

1. Copie a pasta `confeitaria/` para `C:\xampp\htdocs\`
2. Inicie o Apache pelo painel do XAMPP
3. Acesse `http://localhost/confeitaria/`

## Estrutura

```
confeitaria/
  index.php          Página inicial
  cardapio.php        Cardápio completo, com abas por categoria
  sobre.php            História da marca
  contato.php          Informações de contato
  checkout.php         Resumo do pedido + formulário de entrega
  processa.php         Confirmação do pedido (recalcula o total no servidor)
  partials/            Cabeçalho e rodapé reaproveitados em todas as páginas
  data/produtos.php    Catálogo de produtos (fonte única de nomes/preços)
  css/theme.css        Estilo visual da marca
  js/cart.js           Lógica do carrinho (localStorage)
  IMAGENS/             Favicon
```

## Como funciona o pedido

1. No cardápio, o cliente escolhe a quantidade de cada item e adiciona ao carrinho (guardado no navegador, via `localStorage`).
2. No checkout, revisa o pedido e preenche nome, e-mail, telefone e endereço.
3. Ao confirmar, o `processa.php` recalcula o total a partir do catálogo (nunca confia no valor enviado pelo navegador) e mostra a confirmação do pedido.

Não há banco de dados: o pedido não fica salvo depois de confirmado, é só exibido na tela de confirmação.
