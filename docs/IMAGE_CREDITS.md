# Image credits

Coffee photos are free stock photos from [Pexels](https://www.pexels.com/license/)
(free to use, no attribution required — listed here so they are easy to trace or replace).
They live in `apps/web/static/web/img/coffee/`.

Each coffee **type** has one standard photo in its own cup; all its variants use it:

| File | Cup | Used for | Pexels photo |
|------|-----|----------|--------------|
| `espresso.jpg` | Small espresso cup | Espresso, Doppio, Ristretto, Macchiato | https://www.pexels.com/photo/997656/ |
| `americano.jpg` | Americano cup | Classic Americano, Long Black, Americano with Milk | https://www.pexels.com/photo/2113129/ |
| `cappuccino.jpg` | Mug | Cappuccinos | https://www.pexels.com/photo/186857/ |
| `flat-white.jpg` | Mug | Flat Whites | https://www.pexels.com/photo/374147/ |
| `mocha.jpg` | Mug | Mochas | https://www.pexels.com/photo/5419235/ |
| `latte.jpg` | Glass with handle | Lattes | https://www.pexels.com/photo/36673266/ |
| `iced-coffee.jpg` | Glass with handle | Iced Latte, Cold Brew, Iced Macchiato | https://www.pexels.com/photo/11136849/ |
| `preparing.jpg` | — | "Preparing your coffee" screen | https://www.pexels.com/photo/302902/ |

Page background: `apps/web/static/web/img/dark-wood.jpg` — https://www.pexels.com/photo/3705687/

Syrup bottles, milk cartons and the size cups are not photos: they are drawn in the page
(`web/partials/syrup_bottle.html`, `milk_carton.html`, `size_cup.html`) in each item's colour with
its name on the label, so new syrups and milks get their picture automatically.

The home page photo (`apps/web/static/web/img/hero-rainy-cafe.jpg`) was supplied by the project owner.

To change a photo: replace the file (keep the name), or set a different path in the admin
(Menu → Coffees → *Image*; a single variant can also get its own image).
