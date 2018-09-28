# text_enrichment
Text Enrichment

Névelem felismerés: olyan valakinek vagy valaminek az említése a szövegben, mely érdekel bennünket továbbá szerepel az adatbázisban. Például személyek, helyszínek, gyógyszerek

## Vállalt részfeladatok:
1.	Létező megoldások vizsgálata és kipróbálása
2.	Órán tanult módszerek áttanulmányozása
3.	A tapasztalatok alapján prototípus elkészítése
4.	Az elkészült megoldás javítása, továbbfejlesztése
5.	Bemutató elkészítése és előadása

## Megoldási ötletek:
- Az általánosabb feldolgozási folyamat a következő:
  - Tokenizálás, normalizálás/szótövezés, névelem detektálás, névelem normalizálás
- Névelem detektálására az alábbi megközelítéseket ismerjük
  - Szótár alapú
    - Összes entitás összes formáját össze kell gyűjteni
    - Nagy tudásbázis vagy annotált korpusz szükséges
  - Szabály alapú
    - Mintákat kell írni az entitások illesztéséhez
    - Téma specifikus tudás szükséges
  - Statisztikai modell alapú
    - Valószínűségek hozzárendelése a szövegrészekhez
    - Sok tanuló példány szükséges
    - Előny: téma független tudás
- Ezen detekciók használatának előnyeit fogjuk felmérni és ezalapján a legmegfelelőbbet kiválasztani.

## Használni tervezett szoftverek:
-	Elsősorban Python 3-at szeretnénk használni
-	Kisebb részfeladatok/algoritmusok kipróbálásához RapidMinder-t is igénybe vennénk
-	A párhuzamos munkavégzést a GitHub segítségével oldanánk meg
