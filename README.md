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
    - Összes entitás összes formáját össze kell gyűjteni
    - Nagy tudásbázis vagy annotált korpusz szükséges
  - Szabály alapú
    - Mintákat kell írni az entitások illesztéséhez
    - Téma specifikus tudás szükséges
  - Statisztikai modell alapú
    - Valószínűségek hozzárendelése a szövegrészekhez
    - Sok tanuló példány szükséges
    - Előny: téma független tudás
- Ezen detekciók használatának előnyeit fogjuk felmérni és ezalapján a legmegfelelőbbet kiválasztani.

## Létező eszközök, módszerek
- [spaCy](https://spacy.io): python library, statisztikai modell alapú NER, sokféle kategória támogatott, továbbtanítható saját kategóriákkal
- [Stanford NER is a Named Entity Recognizer](https://nlp.stanford.edu/software/CRF-NER.shtml): Java library, kevés alapból támogatott kategória
- [Named-Entity-Recognition-BLSTM-CNN-CoNLL](https://github.com/mxhofer/Named-Entity-Recognition-BidirectionalLSTM-CNN-CoNLL): implementation based on [this paper](https://arxiv.org/abs/1511.08308), Keras

## Használni tervezett technólogiák:
-	Elsősorban Python 3-at szeretnénk használni
-	Kisebb részfeladatok/algoritmusok kipróbálásához opcionálisan RapidMinder-t is igénybe vennénk
-	A párhuzamos munkavégzést a GitHub segítségével oldanánk meg
