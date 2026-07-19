# Calibre Moly.hu metaadat-bővítmény

Ez a [Calibre](https://calibre-ebook.com/) bővítmény könyvek metaadatait és
borítóképeit tölti le a [Moly.hu](https://moly.hu/) oldalról.

A 5.1-es kiadási ág egyesíti a korábbi 1.0.9-es forrásvonalat Hokutya 5.0.9-ig
karbantartott változatával, és hozzáadja a Moly.hu jelenlegi oldalához szükséges
javításokat.

## Főbb funkciók

- cím, szerző, sorozat és sorozatszám lekérése;
- ISBN, fülszöveg, címkék, kiadó és megjelenési év letöltése;
- értékelés és nyelv felismerése;
- keresés elsősorban ISBN, ennek hiányában cím és szerző alapján;
- több lehetséges könyvtalálat kezelése (alapértelmezetten legfeljebb 3);
- több nagy méretű borító letöltése (alapértelmezetten legfeljebb 5);
- kattintható Moly.hu-azonosító a könyv adatlapjának megnyitásához.

## Követelmények

- Calibre 5.0 vagy újabb.
- Internetkapcsolat a metaadatok és borítók lekéréséhez.

Az aktuális kiadást Calibre 9.9 alatt is ellenőriztük.

## Telepítés

1. Töltsd le a kiadáshoz tartozó `Moly_hu-5.1.2.zip` fájlt.
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

## Az 5.1-es kiadási ág javításai

A Moly.hu időközben módosította a keresését és több adatlap HTML-szerkezetét.
A korábbi kiadások emiatt hibás vagy teljesen idegen könyvet találhattak,
illetve az alábbihoz hasonló lxml-hibával leállhattak:

```text
lxml.etree.XMLSyntaxError: internal error
```

Az 5.1-es kiadási ág:

- a Moly.hu jelenlegi `query` keresési paraméterét használja;
- az ISBN-t részesíti előnyben akkor is, ha cím és szerző is rendelkezésre áll;
- csak a tényleges keresési eredmények között keres, így egy átirányított
  kezdőlap véletlenszerű könyveit nem tekinti találatnak;
- hibatűrő UTF-8 HTML-feldolgozással megszünteti az lxml parserhibát;
- a jelenlegi oldalhoz igazítja a cím, szerző, sorozat, ISBN, fülszöveg,
  címkék, kiadó, megjelenési év, értékelés és borítók feldolgozását;
- eltávolítja a címekbe szúrt láthatatlan karaktereket és a fülszöveg
  spoilerfigyelmeztetését, miközben megőrzi a kiemelt szövegrészek tartalmát;
- csak valódi nagy borítóképeket ad vissza, HTML-oldalakat nem;
- helyesen alakítja át a százalékos értékelést a Calibre csillagskálájára;
- év pontosságú adatnál január 1-jét használ, és nem talál ki aktuális
  hónapot vagy napot;
- helyes ISO nyelvkódokat használ a görög, kínai és japán nyelvhez;
- kattintható hivatkozást biztosít a könyv Moly.hu-adatlapjához;
- automatikus parser- és élő integrációs teszteket tartalmaz.

## Ellenőrzés

Az automatikus tesztek mellett élő Moly.hu kereséssel is ellenőriztük a
**Bálint Ágnes: Hajónapló** című könyv adatait és borítóját. A korábban hibát
okozó **Ákody Zsuzsa: Egy csúnya nő** adatlapját, valamint a sorozatnévvel
előtagolt **Egy Zizi naplója: Popsztár** címet és borítóját is sikeresen
feldolgozza. A Moly.hu-n nem szereplő **Jeremy Robinson: Omega** esetében nem
ad vissza téves `Biomega` vagy más szerzőtől származó `Omega` találatot.

A tesztek futtatása fejlesztői környezetben:

```powershell
calibre-debug -e .\tests\test_parsing.py
calibre-debug -e .\tests\live_check.py
```

## Verziótörténet

### 5.1.2 – 2026. július 19.

- Teljes szavakból álló címillesztés: az `Omega` nem egyezik a `Biomega`
  belsejében.
- A csak címre kereső újrapróbálkozás is megtartja az eredeti szerzőszűrést,
  ezért más szerző azonos vagy hasonló című könyve nem kerül a találatok közé.
- Élő negatív regressziós teszt a **Jeremy Robinson: Omega** keresésére.

### 5.1.1 – 2026. július 19.

- A Calibre-ben sorozatnévvel előtagolt címek felismerése, amikor a Moly.hu a
  sorozatot külön linkként, a könyvet pedig rövid címmel jeleníti meg.
- Regressziós teszt az **Egy Zizi naplója: Popsztár** keresésére és borítójára.

### 5.1.0 – 2026. július 19.

- A korábbi 1.0.9-es és 5.0.9-es fejlesztési ág egyesítése.
- A jelenlegi Moly.hu keresés és könyvadatlap támogatása.
- Hibatűrő HTML-feldolgozás az lxml parserhiba ellen.
- A téves, kezdőlapról származó találatok kizárása.
- Az ISBN-keresés, metaadatok, értékelések, dátumok és borítók javítása.
- Kattintható Moly.hu könyvazonosító.
- A spoilerfigyelmeztetés eltávolítása a fülszövegből.
- Automatikus és élő integrációs tesztek hozzáadása.

### 5.0.9 – 2025. augusztus 7.

- Igazítás a Moly.hu fülszövegének változásaihoz.

### 5.0.8 – 2025. május 17.

- Igazítás a sorozatinformációk megváltozott szövegéhez.

### 5.0.7 – 2024. október 19.

- Kisebb hibajavítások, seeder közreműködésével.

### 5.0.6 – 2024. július 7.

- Kisebb hibajavítások.

### 5.0.5 – 2024. július 6.

- Igazítás a Moly.hu címkéinek változásaihoz.

### 5.0.4 – 2022. december 3.

- Igazítás a Moly.hu szöveges mezőinek változásaihoz.

### 5.0.3 – 2021. december 28.

- Kisebb hibajavítások.

### 5.0.2 – 2021. november 28.

- ISBN-keresési hiba javítása.

### 5.0.1 – 2021. november 4.

- A címkefeldolgozás javítása.

### 4.1.7 – 2020. szeptember 26.

- Verziószám módosítása a Calibre 5-höz.

### 1.1.7–1.1.5 – 2020. szeptember 25–26.

- Átállás a Calibre Python 3 környezetére és kisebb hibajavítások.

### 1.1.4 – 2020. július 3.

- ISBN-alapú keresés javítása.

### 1.1.3–1.1.2 – 2020. június 17–18.

- Kisebb hibajavítások és a `moly_hu` azonosító kezelésének módosítása.

### 1.1.1–1.1.0 – 2020. június 17–18.

- Cím- és sorozatfeldolgozás javítása.
- Láthatatlan karakterek és felesleges sortörések eltávolítása.
- A dőlt szövegrészek és spoilerfigyelmeztetések kezelése.

### 1.0.9 – 2020. augusztus 22.

- Python 3 támogatás a másik karbantartási ágban.
- Az oldal feldolgozásával kapcsolatos hibák és formázás javítása.
- Frissítette: Dezső.

### 1.0.8 – 2018. május 30.

- Elsődleges keresés ISBN alapján.
- Sikertelen keresésnél fokozatos visszalépés cím- és szerzőalapú keresésre.
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

- Több nagy méretű borító letöltése és a beállítások átdolgozása.

### 1.0.2 – 2013. július 28.

- Igazítás a Moly.hu akkori elrendezéséhez és nyelvfelismerés hozzáadása.

### 1.0.1 – 2012. október 9.

- ISBN, kiadó és megjelenési év feldolgozása.

### 1.0 – 2011. május 8.

- Első kiadás.

## Köszönetnyilvánítás

Az eredeti bővítményt Daermond készítette és tette közzé. A projektet később
Kloon vette át; az eredeti MobileRead-bejegyzés
[itt olvasható](https://www.mobileread.com/forums/showthread.php?t=193302).

Köszönet kiwidude-nak a kezdeti segítségért; Hoffer Csabának, Kloonnak,
fatsadtnak, otapinak és Dezsőnek az eredeti ág fejlesztéséért; Hokutyának a
Calibre 5-höz igazított ág 2020–2025 közötti karbantartásáért; valamint
seedernek a 2024-es hibajavításokért. A közreműködők munkáját a GPL v3 licenc
feltételeinek megfelelően őrizzük meg és tüntetjük fel.
