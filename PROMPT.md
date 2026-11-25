# Instrukcja dla codziennego odcinka "Poranna porcja"

Odcinek jest słuchany w aucie, więc tekst ma brzmieć dobrze na głos.

## Zadanie

1. Ustal dzisiejszą datę (strefa Europe/Warsaw). Plik odcinka: `episodes/RRRR-MM-DD.md`. Jeśli już istnieje, zakończ bez zmian.
2. Przejrzyj tytuły i treść ostatnich ~30 plików w `episodes/`, żeby nie powtarzać tematów ponadczasowych.
3. Wybierz 5 historii, po jednej z każdego koszyka:
   - **A. Aktualna sytuacja geopolityczna** - zawsze najświeższe wydarzenie z ostatnich 24-48 h.
   - **B. Giełda / biznes** - na zmianę (dzień parzysty giełda, nieparzysty biznes). Giełda: co się działo na rynkach w ostatniej sesji i dlaczego. Biznes: ciekawa decyzja firmy, historia marki, model biznesowy.
   - **C. Rozwój technologii / wynalazki** - na zmianę. Technologia: świeży news (AI, energia, kosmos, robotyka). Wynalazek: historia powstania czegoś, z ciekawą anegdotą.
   - **D. Architektura / sztuka** - na zmianę. Może być aktualne (otwarcie budynku, wystawa, aukcja) albo ponadczasowe (historia budynku, artysty, dzieła).
   - **E. Triathlon / podróże** - na zmianę. Triathlon: historia, legendy, ciekawostki treningowe, aktualne zawody. Podróże: miejsce warte zobaczenia z konkretną historią.
4. Do każdej historii aktualnej zrób wyszukiwanie w sieci i oprzyj się tylko na tym, co znalazłeś. Do ponadczasowych sprawdź kluczowe fakty (daty, liczby). Nie wymyślaj liczb ani cytatów.
5. Napisz scenariusz rozmowy dwojga prowadzących, ZOFIA i MAREK, w formacie poniżej.
6. Zapisz plik, zrób commit "Odcinek RRRR-MM-DD" i push do `main`. GitHub Actions sam zrobi z niego MP3 i doda do kanału.
7. Sprawdź `gh run list --limit 1` po ~3 minutach. Jeśli build się nie powiódł, przeczytaj log (`gh run view --log-failed`), popraw i wypchnij ponownie.

## Format pliku

```
---
title: Krótki tytuł z 5 tematami
description: Odcinek N. Jedno lub dwa zdania o tym, co dziś.
---
ZOFIA: Dzień dobry, tu Poranna porcja...
MAREK: ...
```

Na końcu pliku, w komentarzu HTML `<!-- Źródła: ... -->`, lista linków. Komentarz nie jest czytany na głos.

## Zasady pisania (tekst idzie do syntezatora mowy)

- Po polsku, swobodnie, jak rozmowa dwojga ciekawych świata znajomych. Krótkie zdania.
- Długość: 1100-1400 słów, czyli ok. 8-10 minut. Każda historia ok. 2 minuty.
- Każda kwestia w jednej linii, zaczyna się od `ZOFIA:` albo `MAREK:`. Prowadzący się przeplatają, kwestie po 1-4 zdania.
- Każdą historię zamknij jednym "pytaniem na rozmowę", od którego słuchacz może zacząć rozmowę ze znajomymi.
- Liczby, daty i lata pisz słownie, jeśli mogą być źle przeczytane ("dwudziestego lutego", "tysiąc dziewięćset siedemdziesiątego ósmego roku", "cztery procent"). Proste kwoty i wielkości też słownie.
- Bez skrótów i symboli: zamiast "S&P 500" pisz "es-en-pi 500", zamiast "%" pisz "procent", zamiast "mln" pisz "milionów".
- Nigdy nie używaj długiej pauzy (em dash). Tylko przecinki, kropki i krótki myślnik.
- Bez markdownu w kwestiach (bez gwiazdek, nagłówków, list).
- Giełda: informacyjnie, bez rekomendacji kupna czy sprzedaży.
- Geopolityka: neutralnie, fakty i różne perspektywy, bez własnych ocen.
- Powitanie krótkie, zakończenie krótkie ("Dobrej drogi i do jutra").
