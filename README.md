# Calibre Moly.hu metaadat-bővítmény

Ez a [Calibre](https://calibre-ebook.com/) bővítmény könyvek metaadatait és
borítóképeit tölti le a [Moly.hu](https://moly.hu/) oldalról.

## Főbb funkciók

- cím, szerző, sorozat és sorozatszám lekérése;
- ISBN, fülszöveg, címkék, kiadó és megjelenési év letöltése;
- értékelés és nyelv felismerése;
- keresés elsősorban ISBN, ennek hiányában cím és szerző alapján;
- több lehetséges könyvtalálat kezelése (alapértelmezetten legfeljebb 3);
- több nagy méretű borító letöltése (alapértelmezetten legfeljebb 5).

## Telepítés

1. Töltsd le a kiadáshoz tartozó `Moly_hu-1.1.0.zip` fájlt.
2. A Calibre-ben nyisd meg a **Beállítások → Bővítmények** ablakot.
3. Válaszd a **Bővítmény betöltése fájlból** lehetőséget.
4. Tallózd be a ZIP-fájlt, majd indítsd újra a Calibre-t.

A ZIP-fájlt nem kell és nem szabad kicsomagolni a telepítés előtt.

Ez egy metaadatforrás-bővítmény, ezért nem helyezhető el eszköztáron vagy
helyi menüben. A könyvek **Metaadatok szerkesztése → Metaadatok letöltése**
funkcióján keresztül használható.

## Beállítások

A bővítmény beállításainál módosítható:

- a feldolgozandó könyvtalálatok maximális száma;
- a letöltendő borítóképek maximális száma.

## Az 1.1.0 verzió javításai

A Moly.hu időközben módosította a keresését és több adatlap HTML-szerkezetét,
ezért a korábbi 1.0.9-es bővítmény hibás vagy teljesen idegen könyvet is
találhatott, illetve az alábbihoz hasonló lxml-hibával leállhatott:

```text
lxml.etree.XMLSyntaxError: internal error
```

Az 1.1.0 verzió:

- a Moly.hu jelenlegi `query` keresési paraméterét használja;
- csak a tényleges keresési eredmények között keres, így egy átirányított
  kezdőlap véletlenszerű könyveit nem tekinti találatnak;
- hibatűrő UTF-8 HTML-feldolgozással megszünteti az lxml parserhibát;
- a jelenlegi oldalhoz igazítja a cím, szerző, sorozat, ISBN, fülszöveg,
  címkék, kiadó, megjelenési év, értékelés és borítók feldolgozását;
- eltávolítja a Moly.hu által a címekbe szúrt láthatatlan karaktereket;
- helyesen alakítja át a Moly.hu százalékos értékelését a Calibre
  ötszintes csillagskálájára;
- év pontosságú adatnál január 1-jét használ, és nem talál ki aktuális
  hónapot vagy napot;
- helyes ISO nyelvkódokat használ a görög, kínai és japán nyelvhez.

## Ellenőrzés

Az 1.1.0 verziót Calibre 9.9 alatt ellenőriztük. Az automatikus parser-tesztek
mellett élő Moly.hu kereséssel is sikeresen lekérte a **Bálint Ágnes:
Hajónapló** című könyv adatait, sorozatát, ISBN-jét, kiadóját, címkéit,
értékelését és borítóját.

A tesztek futtatása fejlesztői környezetben:

```powershell
calibre-debug -e .\tests\test_parsing.py
calibre-debug -e .\tests\live_check.py
```

## Verziótörténet

### 1.1.0 – 2026. július 19.

- A jelenlegi Moly.hu keresés és könyvadatlap támogatása.
- Hibatűrő HTML-feldolgozás az lxml parserhiba ellen.
- A téves, kezdőlapról származó találatok kizárása.
- A metaadat- és borítófeldolgozás javítása.
- Az értékelési skála, a részleges megjelenési dátumok és egyes nyelvkódok
  helyesbítése.
- Automatikus és élő integrációs tesztek hozzáadása.

### 1.0.9 – 2020. augusztus 22.

- Python 3 támogatás.
- Az oldal feldolgozásával kapcsolatos hibák javítása.
- Forráskód-formázási javítások.
- Frissítette: Dezső.

### 1.0.8 – 2018. május 30.

- Elsődleges keresés ISBN alapján.
- Sikertelen keresésnél fokozatos visszalépés cím- és szerzőalapú keresésre.
- A cím zárójeles részének elhagyása újrapróbálkozáskor.
- Frissítette: Dezső.

### 1.0.7 – 2018. május 8.

- A felcserélt családnév–utónév sorrend felismerése.
- Frissítette: otapi.

### 1.0.6 – 2018. április 11.

- Ékezetfüggetlen cím- és szerzőszűrés.
- Frissítette: otapi.

### 1.0.5 – 2018. március 29.

- Pontosabb cím- és szerzőszűrés a túl tág keresések ellen.
- Frissítette: otapi.

### 1.0.4 – 2017. január 25.

- A keresés helyreállítása és ISBN-alapú keresés hozzáadása.
- Frissítette: fatsadt.

### 1.0.3 – 2014. január 2.

- Több nagy méretű borító letöltése.
- A bővítmény beállításainak átdolgozása.

### 1.0.2 – 2013. július 28.

- Igazítás a Moly.hu akkori elrendezéséhez.
- Nyelvfelismerés hozzáadása.

### 1.0.1 – 2012. október 9.

- Az oldal változásai miatt szükséges javítások.
- ISBN, kiadó és megjelenési év feldolgozása.

### 1.0 – 2011. május 8.

- Első kiadás.

## Köszönetnyilvánítás

Az eredeti bővítményt Daermond készítette és tette közzé. A projektet később
Kloon vette át; az eredeti MobileRead-bejegyzés
[itt olvasható](https://www.mobileread.com/forums/showthread.php?t=193302).
Köszönet kiwidude-nak a kezdeti segítségért, valamint fatsadt, otapi és Dezső
közreműködéséért és korábbi frissítéseiért.
