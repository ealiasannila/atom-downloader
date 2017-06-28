# atom-downloader
App to download and maintain gis files from mml, syke etc. INSPIRE atom feeds

MML Feed
- ei toimi kunnolla, 500 erroria tulee 

Syke Feed
- Aineistot samassa gis_data/specific kansiossa

# Muutostietopalvelun ja kovalevyaineiston eroja:
* Yhteensä 30372 .laz tiedostoa, jotka löytyivät molemmista kanavista.
* Näistä 22226 .laz tiedostoa, jotka ovat saman nimisiä ja kokoisia (oletettavasti identtisiä) kovalevyllä ja muutostietopalvelussa
* Kovalevyllä on 363 perusnimistä (esim. N4131F1.laz)  .laz tiedostoa, joita ei löydy muutostietopalvelusta, lisäksi added_pts.laz tiedostoja.
* Lisäksi on 8146 perusnimistä .laz tiedostoa, jotka ovat eri kokoisia kovalevyllä ja muutostietopalvelussa. Näistä ainakin osassa myös pistepilvi on erilainen. Esimerkiksi tiedosto N4131F1.laz sisältää kovalevyllä 11742913 pistettä, kun taas muutostietopalvelusta ladattu vastaava tiedosto sisältää 11742852 pistettä.
* Kovalevyllä on myös .las, ja .tif muotoista aineistoa, jota ei muutostietopalvelusta ole saatavilla. Lisäksi on joitakin metadataa sisältäviä .txt ja xml tiedostoja. Kaikki näiden sisältämä tieto tosin käsittääkseni on myös .laz tiedostoissa.

Aineistoja on vertailtu kovalevyllä olevia tiedostoja ja MML:n muutostietopalvelun xml:ssä ilmoitettuja tietoja vertailemalla. Koko aineistoa ei siis ole ladattu muutostietopalvelusta. Latasin kuitenkin xml:n tietojen perusteella ne tiedostot, jotka vaikuttavat erikokoisimmilta (20kpl) verrattuna kovalevlyllä toimitettuun aineistoon ja vertailin näiden osalta sisältöä lasinfon avulla.
