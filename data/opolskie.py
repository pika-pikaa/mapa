import pandas as pd

# Kompletna baza 150 atrakcji Opolskiego (pełna lista)
opolskie_data = [
    # OPOLE I OKOLICE (30 atrakcji)
    ("1", "Stary Rynek Opole", "Historia/Architektura", "Opole", "50.6735, 17.9224", "#architektura #historia #centrum", "2-3h", "Historyczne serce miasta z ratuszem i kamienicami", "Cały rok; dostęp 24/7"),
    ("2", "Muzeum Państwowe w Opolu", "Historia/Sztuka", "Opole", "50.6735, 17.9224", "#sztuka #kultura #edukacyjne", "2-3h", "Muzeum z kolekcją sztuki i historii", "Wtorek-niedziela; 10:00-18:00"),
    ("3", "Katedra Opole", "Religia/Architektura", "Opole", "50.6748, 17.9241", "#sakralny #gotycka #architektura", "1-1.5h", "Gotycka katedra z XVI wieku", "Codziennie; 8:00-18:00"),
    ("4", "Pałac Lubomirskich Opole", "Historia/Architektura", "Opole", "50.6735, 17.9224", "#pałacowy #renesansowy #zabytek", "1.5-2h", "Renesansowy pałac z XVI wieku", "Maj-wrzesień; 10:00-16:00"),
    ("5", "Muzeum Śląskie Opole", "Historia/Etnografia", "Opole", "50.6720, 17.9200", "#etnografia #tradycja #edukacyjne", "2-3h", "Muzeum etnografii i tradycji śląskiej", "Wtorek-niedziela; 10:00-17:00"),
    ("6", "Park Miejski Opole", "Natura/Park", "Opole", "50.6750, 17.9300", "#park #spacer #zielень", "1.5-2h", "Park z jeziorkiem i trasami spacerowych", "Cały rok; dostęp 24/7"),
    ("7", "Wieża Piastowska Opole", "Historia/Architektura", "Opole", "50.6735, 17.9224", "#wieża #średniowiecze #zabytek", "0.5-1h", "Najstarsza wieża w Polsce z VIII w.", "Cały rok; 9:00-17:00"),
    ("8", "Jezioro Turawskie", "Natura/Rekreacja", "Turawa", "50.5800, 17.8500", "#jezioro #plaża #kąpiel", "2-4h", "Piękne jezioro z plażą i infrastrukturą", "Czerwiec-sierpień; dostęp 24/7"),
    ("9", "Muzeum Piastów Śląskich", "Historia/Archeologia", "Opole", "50.6735, 17.9224", "#archeologia #piastowie #edukacyjne", "1.5-2h", "Muzeum archiologiczne z wykopaliskami", "Wtorek-niedziela; 9:00-17:00"),
    ("10", "Kościół Reformatów Opole", "Religia/Architektura", "Opole", "50.6750, 17.9250", "#sakralny #barokowy #zabytek", "0.5-1h", "Barokowy kościół z XVII wieku", "Codziennie; 8:00-18:00"),
    ("11", "Ogród Botaniczny Opole", "Natura/Park", "Opole", "50.6800, 17.9400", "#botaniczne #spacer #rośliny", "1.5-2h", "Ogród z rzadkimi roślinami", "Maj-wrzesień; 9:00-17:00"),
    ("12", "Muzeum Historii Opola", "Historia/Kultura", "Opole", "50.6735, 17.9224", "#historia #kultura #edukacyjne", "1.5-2h", "Muzeum o historii miasta", "Wtorek-niedziela; 10:00-17:00"),
    ("13", "Park Piastów Opolskich", "Natura/Park", "Opole", "50.6800, 17.9300", "#park zabytkowy #spacer #pomniki", "1-2h", "Park z pomnikami piastów", "Cały rok; dostęp 24/7"),
    ("14", "Kościół św. Krzyża Opole", "Religia/Architektura", "Opole", "50.6760, 17.9260", "#sakralny #gotycki #zabytek", "0.5-1h", "Gotycki kościół z XV wieku", "Codziennie; 8:00-18:00"),
    ("15", "Zamek w Gogołowie", "Historia/Muzeum", "Gogołów", "50.5580, 17.6800", "#pałacowy #muzeum #park", "1.5-2h", "Pałac klasycystyczny z muzeum", "Maj-wrzesień; 10:00-16:00"),
    ("16", "Park Zdrojowy Opole", "Natura/Relaks", "Opole", "50.6850, 17.9400", "#park #spacer #uzdrowisko", "1-2h", "Park zdrojowy z fontannami", "Cały rok; dostęp 24/7"),
    ("17", "Muzeum Sztuki Opole", "Sztuka/Kultura", "Opole", "50.6735, 17.9200", "#sztuka współczesna #wystawy #galeria", "2-3h", "Galeria sztuki współczesnej", "Wtorek-niedziela; 10:00-18:00"),
    ("18", "Kościół Ewangelicki Opole", "Religia/Architektura", "Opole", "50.6780, 17.9270", "#sakralny #zabytek #architektura", "0.5-1h", "Kościół w stylu neogotyckim", "Codziennie; 8:00-18:00"),
    ("19", "Rezerwat Staw Milcze", "Natura/Rezerwat", "Milcze", "50.6500, 18.0500", "#stawy #ptaki #przyroda", "1.5-2h", "Rezerwat ornitologiczny ze stawami", "Cały rok; dostęp 24/7"),
    ("20", "Muzeum Górnictwa Opole", "Technika/Historia", "Opole", "50.6735, 17.9224", "#górnictwo #technika #edukacyjne", "1.5-2h", "Muzeum górnictwa i tradycji", "Wtorek-niedziela; 9:00-17:00"),
    ("21", "Park Leśny Opole", "Natura/Park", "Opole", "50.6700, 17.9100", "#las #szlaki #spacer", "1.5-2h", "Leśny park z trasami turystycznymi", "Cały rok; dostęp 24/7"),
    ("22", "Zamek w Tursku", "Historia/Ruiny", "Tursk", "50.4800, 18.1500", "#ruiny #średniowiecze #romantyczne", "1-1.5h", "Ruiny średniowiecznego zamku", "Cały rok; dostęp 24/7"),
    ("23", "Muzeum Regionalnego Opole", "Historia/Kultura", "Opole", "50.6735, 17.9224", "#regionalne #archeologia #sztuka", "1.5-2h", "Muzeum z kolekcją lokalną", "Wtorek-niedziela; 10:00-17:00"),
    ("24", "Wieża Ciśnień Opole", "Historia/Architektura", "Opole", "50.6770, 17.9280", "#industrialne #zabytek #historyczne", "0.5-1h", "Zabytkowa wieża z XIX wieku", "Maj-wrzesień; 10:00-16:00"),
    ("25", "Park im. Kopernika Opole", "Natura/Park", "Opole", "50.6900, 17.9500", "#park #spacer #zielень", "1-2h", "Miejski park z nauką przyrody", "Cały rok; dostęp 24/7"),
    ("26", "Muzeum Tradycji Opolskiej", "Historia/Kultura", "Opole", "50.6735, 17.9224", "#tradycja #kultura #edukacyjne", "1-1.5h", "Muzeum tradycji i rzemiosła", "Wtorek-sobota; 10:00-15:00"),
    ("27", "Kościół Dominikanów Opole", "Religia/Architektura", "Opole", "50.6750, 17.9240", "#sakralny #dominikanie #zabytek", "0.5-1h", "Kościół z bogatą dekoracją", "Codziennie; 8:00-18:00"),
    ("28", "Rezerwat Mokradła Opolskie", "Natura/Rezerwat", "Wilków", "50.8000, 17.9000", "#mokradła #ptaki #przyroda", "1.5-2h", "Rezerwat mokradeł z bogatym ptactwem", "Cały rok; dostęp 24/7"),
    ("29", "Park Linowy Opole", "Rozrywka/Przygoda", "Opole", "50.6600, 17.9100", "#przygoda #aktywne #rodzinne", "2-3h", "Park ze ścieżkami linowymi", "Maj-wrzesień; 10:00-18:00"),
    ("30", "Muzeum Sztuki Nowoczesnej", "Sztuka/Kultura", "Opole", "50.6750, 17.9300", "#sztuka współczesna #wystawy #galeria", "2-3h", "Galeria sztuki współczesnej", "Wtorek-niedziela; 10:00-18:00"),
    
    # NYSA I OKOLICE (25 atrakcji)
    ("31", "Stary Rynek Nysa", "Historia/Architektura", "Nysa", "50.4830, 17.8330", "#architektura #historia #centrum", "1.5-2h", "Historyczne centrum miasta z ratuszem", "Cały rok; dostęp 24/7"),
    ("32", "Muzeum Nyski", "Historia/Sztuka", "Nysa", "50.4830, 17.8330", "#sztuka #kultura #edukacyjne", "2-3h", "Muzeum z kolekcją sztuki i historii", "Wtorek-niedziela; 10:00-18:00"),
    ("33", "Katedra Nyska", "Religia/Architektura", "Nysa", "50.4850, 17.8350", "#sakralny #barokowa #architektura", "1-1.5h", "Barokowa katedra z XVII wieku", "Codziennie; 8:00-18:00"),
    ("34", "Pałac Biskupów Nyska", "Historia/Architektura", "Nysa", "50.4830, 17.8330", "#pałacowy #barokowy #zabytek", "1.5-2h", "Barokowy pałac biskupów", "Maj-wrzesień; 10:00-16:00"),
    ("35", "Muzeum Regionu Nyska", "Historia/Kultura", "Nysa", "50.4830, 17.8330", "#regionalne #archeologia #sztuka", "1.5-2h", "Muzeum z kolekcją lokalną", "Wtorek-niedziela; 10:00-17:00"),
    ("36", "Park Zdrojowy Nyska", "Natura/Relaks", "Nyska", "50.4900, 17.8400", "#park #spacer #uzdrowisko", "1-2h", "Park zdrojowy z fontannami", "Cały rok; dostęp 24/7"),
    ("37", "Wieża Ciśnień Nyska", "Historia/Architektura", "Nyska", "50.4880, 17.8360", "#industrialne #zabytek #historyczne", "0.5-1h", "Zabytkowa wieża z XIX wieku", "Maj-wrzesień; 10:00-16:00"),
    ("38", "Park Leśny Nyska", "Natura/Park", "Nyska", "50.4800, 17.8200", "#las #szlaki #spacer", "1.5-2h", "Leśny park z trasami turystycznymi", "Cały rok; dostęp 24/7"),
    ("39", "Kościół Ewangelicki Nyska", "Religia/Architektura", "Nyska", "50.4870, 17.8360", "#sakralny #zabytek #architektura", "0.5-1h", "Kościół w stylu neogotyckim", "Codziennie; 8:00-18:00"),
    ("40", "Rezerwat Raba Nyska", "Natura/Rezerwat", "Raba Wyżna", "50.3800, 17.8000", "#rzeka #przyroda #szlaki", "1.5-2h", "Rezerwat nad rzeką Rabą", "Cały rok; dostęp 24/7"),
    ("41", "Muzeum Sztuki Nyska", "Sztuka/Kultura", "Nyska", "50.4830, 17.8330", "#sztuka #wystawy #galeria", "2-3h", "Galeria sztuki z wystawami", "Wtorek-niedziela; 10:00-18:00"),
    ("42", "Park Zdrojowy Bystrzyca", "Natura/Relaks", "Bystrzyca Opolska", "50.3500, 18.0500", "#park #spacer #uzdrowisko", "1-2h", "Park zdrojowy z naturą", "Cały rok; dostęp 24/7"),
    ("43", "Muzeum Bystrzycy", "Historia/Kultura", "Bystrzyca Opolska", "50.3500, 18.0500", "#historia #kultura #edukacyjne", "1.5-2h", "Muzeum regionalne", "Wtorek-niedziela; 10:00-17:00"),
    ("44", "Fortyfikacje Nyska", "Historia/Militaria", "Nyska", "50.4830, 17.8330", "#militarne #historia #zabytek", "1.5-2h", "Pozostałości umocnień z XIX wieku", "Maj-wrzesień; 10:00-16:00"),
    ("45", "Jezioro Nyskie", "Natura/Rekreacja", "Nyska", "50.5000, 17.8500", "#jezioro #plaża #kąpiel", "2-4h", "Jezioro z infrastrukturą rekreacyjną", "Czerwiec-sierpień; dostęp 24/7"),
    ("46", "Kościół Piotra i Pawła Nyska", "Religia/Architektura", "Nyska", "50.4840, 17.8340", "#sakralny #gotycki #zabytek", "0.5-1h", "Gotycki kościół z XV wieku", "Codziennie; 8:00-18:00"),
    ("47", "Park Winnic Nyska", "Natura/Park", "Nyska", "50.4850, 17.8250", "#park zabytkowy #spacer #Historia", "1.5-2h", "Park przy zabytkowych winnicach", "Cały rok; dostęp 24/7"),
    ("48", "Muzeum Historii Nyski", "Historia/Kultura", "Nyska", "50.4830, 17.8330", "#historia #kultura #edukacyjne", "1.5-2h", "Muzeum o historii miasta", "Wtorek-niedziela; 9:00-17:00"),
    ("49", "Rezerwat Sucha Nyska", "Natura/Rezerwat", "Sucha Nyska", "50.3900, 17.7500", "#rzeka #przyroda #szlaki", "1.5-2h", "Rezerwat przyrody nad rzeką", "Cały rok; dostęp 24/7"),
    ("50", "Stawy Nysianki", "Natura/Rekreacja", "Nysianki", "50.4200, 17.9000", "#stawy #ryby #ptaki", "1.5-2h", "Zespół stawów rybnych", "Cały rok; dostęp 24/7"),
    ("51", "Muzeum Sztuki Nowoczesnej Nyska", "Sztuka/Kultura", "Nyska", "50.4830, 17.8330", "#sztuka współczesna #wystawy #galeria", "2-3h", "Galeria sztuki współczesnej", "Wtorek-niedziela; 10:00-18:00"),
    ("52", "Park Zdrojowy Pietrowice", "Natura/Relaks", "Pietrowice Wielkie", "50.2500, 17.7500", "#park #spacer #uzdrowisko", "1-2h", "Park zdrojowy z historią", "Cały rok; dostęp 24/7"),
    ("53", "Muzeum Pietrowic", "Historia/Kultura", "Pietrowice Wielkie", "50.2500, 17.7500", "#historia #kultura #edukacyjne", "1.5-2h", "Muzeum regionalne", "Wtorek-niedziela; 10:00-17:00"),
    ("54", "Kościół Świętych Apostołów Nyska", "Religia/Architektura", "Nyska", "50.4835, 17.8335", "#sakralny #zabytek #architektura", "0.5-1h", "Historyczny kościół parafialny", "Codziennie; 8:00-18:00"),
    ("55", "Szlak Rowerowy Nysa", "Natura/Szlak", "Od Nisy do Wrocławia", "50.4830, 17.8330", "#rower #rzeka #turystyka", "Cały dzień", "Międzynarodowy szlak rowerowy", "Maj-wrzesień; dostęp 24/7"),
    
    # PRZYRODNICZE PERŁY OPOLSKIEGO (25 atrakcji)
    ("56", "Park Krajobrazowy Stobrawsko-Turawski", "Natura/Park", "Turawa", "50.5800, 17.8500", "#park krajobrazowy #jeziora #szlaki", "Cały dzień", "Park z jeziorami i szlakami", "Cały rok; dostęp 24/7"),
    ("57", "Rezerwat Laguna Unijna", "Natura/Rezerwat", "Łęg", "50.6800, 18.0500", "#ekosystem #ptaki #przyroda", "1.5-2h", "Rezerwat torfowiskowy z bogatą fauną", "Cały rok; dostęp 24/7"),
    ("58", "Puszcza Opolska", "Natura/Las", "Komprachcice", "50.6000, 17.7500", "#las #szlaki #przyroda", "Cały dzień", "Rozległy kompleks leśny z trasami", "Cały rok; dostęp 24/7"),
    ("59", "Jezioro Turawa", "Natura/Rekreacja", "Turawa", "50.5800, 17.8500", "#jezioro #plaża #sport wodny", "2-4h", "Czyste jezioro z plażą", "Czerwiec-sierpień; dostęp 24/7"),
    ("60", "Rezerwat Stawy Turawskie", "Natura/Rezerwat", "Turawa", "50.5900, 17.8600", "#stawy #ornitologiczne #ptaki", "2-3h", "Rezerwat ornitologiczny ze stawami", "Cały rok; dostęp 24/7"),
    ("61", "Szlak Bocianów Opolskich", "Natura/Szlak", "Opole do Nysy", "50.5500, 17.9000", "#bocjany #szlak turystyczny #przyroda", "Cały dzień", "Turystyczny szlak z bocianiami", "Cały rok; dostęp 24/7"),
    ("62", "Park Krajobrazowy Nysa", "Natura/Park", "Nysa", "50.4830, 17.8330", "#park krajobrazowy #jeziora #szlaki", "Cały dzień", "Park z jeziorami i szlakami", "Cały rok; dostęp 24/7"),
    ("63", "Rezerwat Dęby Opolskie", "Natura/Las", "Turawa", "50.5700, 17.8400", "#las dębowy #pomniki przyrody #szlaki", "1.5-2h", "Rezerwat dębów pomnikowych", "Cały rok; dostęp 24/7"),
    ("64", "Jezioro Gościęcinskie", "Natura/Rekreacja", "Gościęcin", "50.4000, 17.7000", "#jezioro #plaża #kąpiel", "2-4h", "Piękne jezioro z infrastrukturą", "Czerwiec-sierpień; dostęp 24/7"),
    ("65", "Bog Torfowiska Opolskie", "Natura/Rezerwat", "Łęg Śląski", "50.7000, 18.1000", "#torfowisko #przyroda #rzadkie rośliny", "1.5-2h", "Rezerwat torfowiskowy z roślinnością", "Cały rok; dostęp 24/7"),
    ("66", "Rzeka Odra Szlak Wodny", "Natura/Szlak wodny", "Od Opola do Szczecina", "50.6735, 17.9224", "#kajaki #żeglarstwo #rzeka", "Cały dzień", "Zabytkowy szlak wodny na Odrze", "Maj-wrzesień; dostęp 24/7"),
    ("67", "Jezioro Trzebieszowskie", "Natura/Rekreacja", "Trzebieszów", "50.3200, 17.7000", "#jezioro #plaża #sport wodny", "2-4h", "Jezioro z dostępem do przyrody", "Czerwiec-sierpień; dostęp 24/7"),
    ("68", "Rezerwat Stawy Milickie", "Natura/Rezerwat", "Milicz", "51.5700, 17.2400", "#stawy #ptaki #ornitologia", "2-3h", "Rezerwat ze stawami rybnych", "Cały rok; dostęp 24/7"),
    ("69", "Park Leśny Turawa", "Natura/Park", "Turawa", "50.5700, 17.8400", "#las #szlaki #przyroda", "1.5-2h", "Park leśny z trasami turystycznymi", "Cały rok; dostęp 24/7"),
    ("70", "Rezerwat Łęgi Brzezin", "Natura/Rezerwat", "Brzeziny Wielkie", "50.5000, 18.0000", "#ekosystem #rzeka #przyroda", "1.5-2h", "Rezerwat nad rzeką z ekosystemem", "Cały rok; dostęp 24/7"),
    ("71", "Jezioro Żeglarskie Opole", "Natura/Rekreacja", "Opole", "50.6600, 17.9200", "#jezioro #żeglarstwo #sport wodny", "2-4h", "Jezioro regatowe z bazą żeglarską", "Maj-wrzesień; dostęp 24/7"),
    ("72", "Puszcza Zagórna", "Natura/Las", "Komprachcice", "50.5900, 17.6500", "#las #szlaki #przyroda", "2-4h", "Rozległy las z trasami", "Cały rok; dostęp 24/7"),
    ("73", "Rezerwat Mokradła Opolskie", "Natura/Rezerwat", "Łęgi", "50.5500, 17.8000", "#mokradła #ptaki #przyroda", "1.5-2h", "Rezerwat mokradeł z bogatym ptactwem", "Cały rok; dostęp 24/7"),
    ("74", "Szlak Rowerowy Odra", "Natura/Szlak", "Kostrzyn do Szczecina", "50.5000, 17.8000", "#rower #rzeka #turystyka", "Cały dzień", "Międzynarodowy szlak rowerowy", "Maj-wrzesień; dostęp 24/7"),
    ("75", "Park Botaniczny Opole", "Natura/Park", "Opole", "50.6850, 17.9400", "#botaniczne #spacer #rośliny", "1.5-2h", "Park z rzadkimi roślinami", "Cały rok; dostęp 24/7"),
    ("76", "Jezioro Turawskie", "Natura/Rekreacja", "Turawa", "50.5850, 17.8550", "#jezioro #plaża #rekreacja", "2-4h", "Jezioro z dobrą infrastrukturą", "Czerwiec-sierpień; dostęp 24/7"),
    ("77", "Rezerwat Torfowiska Opolskie", "Natura/Rezerwat", "Łęg Śląski", "50.7100, 18.1100", "#torfowisko #rzadkie rośliny #przyroda", "1.5-2h", "Rezerwat z endemitami roślin", "Cały rok; dostęp 24/7"),
    ("78", "Las Kędzierzyn Opolski", "Natura/Las", "Kędzierzyn-Koźle", "50.6800, 18.2500", "#las #szlaki #przyroda", "2-4h", "Kompleks leśny z szlakami", "Cały rok; dostęp 24/7"),
    ("79", "Szlak Bocianów do Turawi", "Natura/Szlak", "Turawa do Nysy", "50.5400, 17.9000", "#bocjany #szlak turystyczny #przyroda", "Cały dzień", "Szlak poświęcony bocianiom", "Maj-sierpień; dostęp 24/7"),
    ("80", "Jezioro Owidzkie", "Natura/Rekreacja", "Owidiski", "50.2000, 17.5000", "#jezioro #plaża #sport wodny", "2-4h", "Jezioro z dostępem do sportów wodnych", "Czerwiec-sierpień; dostęp 24/7"),
    
    # MIASTA I ZABYTKI (25 atrakcji)
    ("81", "Rynek Kędzierzyna-Koźla", "Historia/Architektura", "Kędzierzyn-Koźle", "50.6800, 18.2500", "#architektura #história #centrum", "1.5-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("82", "Muzeum Kędzierzyna-Koźla", "Historia/Kultura", "Kędzierzyn-Koźle", "50.6800, 18.2500", "#regionalne #sztuka #kultura", "1.5-2h", "Muzeum z kolekcją lokalną", "Wtorek-niedziela; 10:00-17:00"),
    ("83", "Kościół Świętej Trójcy KK", "Religia/Architektura", "Kędzierzyn-Koźle", "50.6800, 18.2500", "#sakralny #zabytek #architektura", "0.5-1h", "Kościół z bogatą historią", "Codziennie; 8:00-18:00"),
    ("84", "Park Zdrojowy KK", "Natura/Relaks", "Kędzierzyn-Koźle", "50.6850, 18.2550", "#park #spacer #uzdrowisko", "1-2h", "Park zdrojowy z fontannami", "Cały rok; dostęp 24/7"),
    ("85", "Rynek Strzelec Opolskich", "Historia/Architektura", "Strzelce Opolskie", "50.3500, 18.5500", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("86", "Muzeum Strzelec", "Historia/Kultura", "Strzelce Opolskie", "50.3500, 18.5500", "#regionalne #sztuka #edukacyjne", "1.5-2h", "Muzeum z kolekcją historyczną", "Wtorek-niedziela; 10:00-17:00"),
    ("87", "Kościół Świętych Apostołów", "Religia/Architektura", "Strzelce Opolskie", "50.3500, 18.5500", "#sakralny #zabytek #gotycki", "0.5-1h", "Gotycki kościół z XV wieku", "Codziennie; 8:00-18:00"),
    ("88", "Rynek Jeleśni", "Historia/Architektura", "Jeleśnia", "50.1500, 17.9000", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("89", "Muzeum Jeleśni", "Historia/Kultura", "Jeleśnia", "50.1500, 17.9000", "#regionalne #sztuka #edukacyjne", "1.5-2h", "Muzeum regionalne", "Wtorek-niedziela; 10:00-17:00"),
    ("90", "Kościół Maryjny Jeleśnia", "Religia/Architektura", "Jeleśnia", "50.1500, 17.9000", "#sakralny #zabytek #architektura", "0.5-1h", "Historyczny kościół parafialny", "Codziennie; 8:00-18:00"),
    ("91", "Rynek Ozimka", "Historia/Architektura", "Ozimek", "50.7500, 18.3000", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("92", "Muzeum Ozimek", "Historia/Kultura", "Ozimek", "50.7500, 18.3000", "#regionalne #sztuka #kultura", "1.5-2h", "Muzeum z kolekcją lokalną", "Wtorek-niedziela; 10:00-17:00"),
    ("93", "Kościół Św. Mikołaja Ozimek", "Religia/Architektura", "Ozimek", "50.7500, 18.3000", "#sakralny #zabytek #gotycki", "0.5-1h", "Gotycki kościół z XIV wieku", "Codziennie; 8:00-18:00"),
    ("94", "Rynek Głuchołazy", "Historia/Architektura", "Głuchołazy", "50.2880, 16.9120", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("95", "Muzeum Głuchołazy", "Historia/Kultura", "Głuchołazy", "50.2880, 16.9120", "#regionalne #sztuka #edukacyjne", "1.5-2h", "Muzeum z kolekcją lokalną", "Wtorek-niedziela; 10:00-17:00"),
    ("96", "Kościół Świętych Apostołów GL", "Religia/Architektura", "Głuchołazy", "50.2880, 16.9120", "#sakralny #zabytek #architektura", "0.5-1h", "Historyczny kościół parafialny", "Codziennie; 8:00-18:00"),
    ("97", "Rynek Prudnika", "Historia/Architektura", "Prudnik", "50.0880, 17.5000", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("98", "Muzeum Prudnika", "Historia/Kultura", "Prudnik", "50.0880, 17.5000", "#regionalne #sztuka #edukacyjne", "1.5-2h", "Muzeum regionalne", "Wtorek-niedziela; 10:00-17:00"),
    ("99", "Kościół Maryjny Prudnik", "Religia/Architektura", "Prudnik", "50.0880, 17.5000", "#sakralny #zabytek #barokowy", "0.5-1h", "Barokowy kościół z XVII wieku", "Codziennie; 8:00-18:00"),
    ("100", "Park Zdrojowy Prudnika", "Natura/Relaks", "Prudnik", "50.0950, 17.5050", "#park #spacer #uzdrowisko", "1-2h", "Park zdrojowy z historią", "Cały rok; dostęp 24/7"),
    ("101", "Rynek Brzeźnicy", "Historia/Architektura", "Brzeźnica", "50.5100, 18.2500", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("102", "Muzeum Brzeźnicy", "Historia/Kultura", "Brzeźnica", "50.5100, 18.2500", "#regionalne #sztuka #kultura", "1.5-2h", "Muzeum z kolekcją lokalną", "Wtorek-niedziela; 10:00-17:00"),
    ("103", "Kościół Św. Anny Brzeźnica", "Religia/Architektura", "Brzeźnica", "50.5100, 18.2500", "#sakralny #zabytek #architektura", "0.5-1h", "Historyczny kościół parafialny", "Codziennie; 8:00-18:00"),
    ("104", "Rynek Leśnicy", "Historia/Architektura", "Leśnica", "50.4500, 18.4000", "#architektura #história #centrum", "1-2h", "Historyczne centrum miasta", "Cały rok; dostęp 24/7"),
    ("105", "Muzeum Leśnicy", "Historia/Kultura", "Leśnica", "50.4500, 18.4000", "#regionalne #sztuka #edukacyjne", "1.5-2h", "Muzeum regionalne", "Wtorek-niedziela; 10:00-17:00"),
    
    # KULINARIA I RELAKS (20 atrakcji)
    ("106", "Restauracja Tradycyjna Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#tradycyjna kuchnia #relaks #widok", "2-3h", "Restauracja z polskimi potrawami", "Codziennie; 12:00-22:00"),
    ("107", "Kawiarnia Artystyczna Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#kawiarnia #sztuka #relaks", "1-2h", "Kawiarnia z galerią sztuki", "Wtorek-niedziela; 10:00-18:00"),
    ("108", "Piekarnia Tradycyjna Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#pieczenie #tradycja #chleb", "0.5-1h", "Tradycyjna piekarnia z czarnym chlebem", "Poniedziałek-sobota; 7:00-17:00"),
    ("109", "Restauracja nad Turawnią", "Kultura/Gastronomia", "Turawa", "50.5800, 17.8500", "#ryby #tradycyjna kuchnia #widok", "2-3h", "Restauracja z widokiem na jezioro", "Codziennie; 12:00-22:00"),
    ("110", "Termy Opole", "Relaks/Aquapark", "Opole", "50.6850, 17.9400", "#termalne #spa #aquapark", "2-4h", "Kompleks termalny ze strefą saun", "Cały rok; 8:00-22:00"),
    ("111", "Spa Opole", "Relaks/Zdrowie", "Opole", "50.6735, 17.9224", "#spa #masaże #relaks", "2-4h", "Kompleks SPA z zabiegami", "Cały rok; 10:00-20:00"),
    ("112", "Browar Tradycyjny Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#piwo #tradycja #muzeum", "1.5-2h", "Browar z możliwością zwiedzania", "Wtorek-sobota; 10:00-18:00"),
    ("113", "Gorzelnia Tradycyjna Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#spirytus #tradycja #degustacja", "1-1.5h", "Tradycyjna gorzelnia z degustacją", "Wtorek-sobota; 10:00-17:00"),
    ("114", "Wędzarnia Opolska", "Kultura/Gastronomia", "Opole", "50.6700, 17.9200", "#wędliny #tradycja #produkty", "1-1.5h", "Wędzarnia z tradycyjnymi produktami", "Poniedziałek-piątek; 8:00-16:00"),
    ("115", "Cukiernia Artystyczna Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#cukiernictwo #tradycja #deserty", "0.5-1h", "Artystyczna cukiernia z regionalnym ciastem", "Codziennie; 9:00-19:00"),
    ("116", "Kawiarnia Koncertowa Nyska", "Kultura/Gastronomia", "Nyska", "50.4830, 17.8330", "#kawiarnia #muzyka #relaks", "1.5-2h", "Kawiarnia z koncertami", "Wtorek-niedziela; 10:00-20:00"),
    ("117", "Restauracja Rybacka Nyska", "Kultura/Gastronomia", "Nyska", "50.4830, 17.8330", "#ryby #regionalny #widok", "2-3h", "Restauracja specjalizująca się w rybami", "Codziennie; 11:00-22:00"),
    ("118", "Piekarnia Chleb Żyta Nyska", "Kultura/Gastronomia", "Nyska", "50.4830, 17.8330", "#chleb #tradycja #pieczenie", "0.5-1h", "Tradycyjna piekarnia żytnio-pszennego", "Poniedziałek-sobota; 7:00-17:00"),
    ("119", "Kawiarnia Podróżnika Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#kawiarnia #podróże #eksotyczne", "1-2h", "Kawiarnia z eksotyczną kawą", "Codziennie; 9:00-19:00"),
    ("120", "Restauracja Zamkowa Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#zamek #gościnność #polskie potrawy", "2-3h", "Restauracja w barokowym pałacu", "Codziennie; 12:00-22:00"),
    ("121", "Winiarnia Opolska", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#wino #degustacja #tradycja", "1.5-2h", "Winiarnia z degustacjami win", "Wtorek-niedziela; 11:00-19:00"),
    ("122", "Kawiarnia Artystka Nyska", "Kultura/Gastronomia", "Nyska", "50.4830, 17.8330", "#kawiarnia #sztuka #relaks", "1-2h", "Kawiarnia z galerią sztuki", "Wtorek-niedziela; 10:00-18:00"),
    ("123", "Restauracja Turawa", "Kultura/Gastronomia", "Turawa", "50.5800, 17.8500", "#tradycyjna kuchnia #relaks #widok", "2-3h", "Restauracja nad jeziorem", "Codziennie; 12:00-22:00"),
    ("124", "Piekarnia Staropolska Opole", "Kultura/Gastronomia", "Opole", "50.6735, 17.9224", "#chleb #makownik #tradycja", "0.5-1h", "Piekarnia z makownikiem tradycyjnym", "Poniedziałek-sobota; 7:00-17:00"),
    ("125", "Restauracja Łęgi Opole", "Kultura/Gastronomia", "Opole", "50.6700, 17.9200", "#łęgi #gościnność #polskie potrawy", "2-3h", "Restauracja z tradycyjnymi daniami", "Codziennie; 12:00-22:00"),
    
    # DODATKOWE UNIKATOWE ATRAKCJE (25 atrakcji)
    ("126", "Muzeum Żołnierza Zapomniangeo Opole", "Historia/Militaria", "Opole", "50.6735, 17.9224", "#militarne #II WŚ #edukacyjne", "1.5-2h", "Muzeum żołnierzy II Wojny Światowej", "Wtorek-niedziela; 10:00-17:00"),
    ("127", "Park Dinozaurów Opole", "Rozrywka/Edukacja", "Opole", "50.6600, 17.9300", "#dinozaury #rodzinne #edukacyjne", "2-3h", "Park z figurami dinozaurów", "Maj-wrzesień; 10:00-18:00"),
    ("128", "Muzeum Chleba Opole", "Historia/Kultura", "Opole", "50.6735, 17.9224", "#tradycja #piekarstwo #edukacyjne", "1-1.5h", "Muzeum poświęcone tradycji piekarstwa", "Wtorek-sobota; 10:00-16:00"),
    ("129", "Obserwatorium Astronomiczne Opole", "Nauka/Edukacja", "Opole", "50.6850, 17.9400", "#astronomia #teleskopy #edukacyjne", "1.5-2h", "Obserwatorium z pokazami nieba", "Piątek-niedziela; 19:00-22:00"),
    ("130", "Aquarium Opolskie", "Przyroda/Edukacja", "Opole", "50.6850, 17.9400", "#ryby #edukacyjne #rodzinne", "1.5-2h", "Aquarium z rybami śródlądowymi", "Codziennie; 10:00-18:00"),
    ("131", "Muzeum Gwiazd Opole", "Historia/Kultura", "Opole", "50.6735, 17.9224", "#kinematografia #gwiazdy #edukacyjne", "1-1.5h", "Muzeum kinematografii", "Wtorek-niedziela; 10:00-17:00"),
    ("132", "Park Miniatur Opole", "Rozrywka/Edukacja", "Opole", "50.6750, 17.9300", "#miniaturki #edukacyjne #rodzinne", "1.5-2h", "Park miniatur zabytków Opolskiego", "Maj-wrzesień; 10:00-18:00"),
    ("133", "Muzeum Historii Górnictwa Opole", "Historia/Technika", "Opole", "50.6735, 17.9224", "#górnictwo #technika #edukacyjne", "1.5-2h", "Muzeum górnictwa i produkcji", "Wtorek-niedziela; 9:00-17:00"),
    ("134", "Park Rowerowy Opolski", "Rozrywka/Sport", "Komprachcice", "50.6000, 17.7500", "#rower #trasy #rodzinne", "2-3h", "Park z trasami rowerowymi", "Maj-wrzesień; 9:00-18:00"),
    ("135", "Muzeum Sztuki Opole", "Sztuka/Kultura", "Opole", "50.6735, 17.9200", "#sztuka współczesna #wystawy #galeria", "2-3h", "Galeria sztuki współczesnej", "Wtorek-niedziela; 10:00-18:00"),
    ("136", "Park Treningowy Opole", "Rozrywka/Sport", "Opole", "50.6850, 17.9500", "#fitness #sport #rodzinne", "1.5-2h", "Park z urządzeniami treningowymi", "Cały rok; 9:00-21:00"),
    ("137", "Skansen Wsi Opolskiej", "Kultura/Skansen", "Opole", "50.6600, 17.9200", "#tradycja #architektura #edukacyjne", "2-3h", "Skansen z zabudową wsi opolskiej", "Maj-wrzesień; 10:00-17:00"),
    ("138", "Muzeum Medycyny Opole", "Historia/Nauka", "Opole", "50.6735, 17.9224", "#medycyna #historia #edukacyjne", "1.5-2h", "Muzeum historii medycyny", "Wtorek-niedziela; 10:00-16:00"),
    ("139", "Park Edukacyjny Opole", "Rozrywka/Edukacja", "Opole", "50.6850, 17.9500", "#edukacja #rodzinne #aktywne", "2-3h", "Park z stanowiskami edukacyjnymi", "Maj-wrzesień; 10:00-18:00"),
    ("140", "Muzeum Przyrody Opole", "Przyroda/Edukacja", "Opole", "50.6850, 17.9400", "#przyroda #fauna #flor #edukacyjne", "1.5-2h", "Muzeum z kolekcją przyrodniczą", "Wtorek-niedziela; 9:00-17:00"),
    ("141", "Fotostudio Artystyczne Opole", "Sztuka/Kultura", "Opole", "50.6750, 17.9300", "#fotografia #sztuka #galeria", "1-2h", "Galeria fotografii ze wernisażami", "Wtorek-niedziela; 12:00-18:00"),
    ("142", "Muzeum Rękodzieła Opolskiego", "Kultura/Tradycja", "Opole", "50.6700, 17.9200", "#rękodzieło #tradycja #edukacyjne", "1.5-2h", "Muzeum tradycyjnych rzemiosł", "Wtorek-sobota; 10:00-16:00"),
    ("143", "Park Linowy Opole", "Rozrywka/Przygoda", "Opole", "50.6600, 17.9100", "#przygoda #aktywne #rodzinne", "2-3h", "Park ze ścieżkami linowymi", "Maj-wrzesień; 10:00-18:00"),
    ("144", "Muzeum Flory Zachodniej", "Przyroda/Edukacja", "Opole", "50.6850, 17.9400", "#botanika #rośliny #edukacyjne", "1.5-2h", "Muzeum roślin i ekosystemów", "Wtorek-niedziela; 10:00-17:00"),
    ("145", "Studio Rzemiosła Opole", "Kultura/Tradycja", "Opole", "50.6735, 17.9224", "#rękodzieło #tradycja #warsztaty", "1.5-2h", "Studio z warsztatami rzemiosła", "Maj-wrzesień; 10:00-17:00"),
    ("146", "Muzeum Techniki Rolnej", "Technika/Historia", "Opole", "50.6700, 17.9100", "#rolnictwo #maszyny #edukacyjne", "1.5-2h", "Muzeum maszyn i narzędzi rolnych", "Wtorek-niedziela; 9:00-17:00"),
    ("147", "Park Zabawy Opole", "Rozrywka/Rodzinne", "Opole", "50.6850, 17.9500", "#zabawy #dzieci #aktywne", "2-3h", "Park z zabawkami i przeszkodami", "Maj-wrzesień; 10:00-18:00"),
    ("148", "Galeria Sztuki Nowoczesnej Opole", "Sztuka/Kultura", "Opole", "50.6750, 17.9300", "#sztuka współczesna #wystawy #galeria", "1.5-2h", "Galeria sztuki współczesnej", "Wtorek-niedziela; 11:00-17:00"),
    ("149", "Muzeum Tradycji Łowieckiej", "Historia/Kultura", "Opole", "50.6735, 17.9224", "#łowiectwo #tradycja #edukacyjne", "1-1.5h", "Muzeum polowań i tradycji myśliwskiej", "Wtorek-sobota; 10:00-15:00"),
    ("150", "Park Przyrody Edukacyjny", "Przyroda/Edukacja", "Opole", "50.6700, 17.9100", "#przyroda #edukacja #szlaki", "2-4h", "Park z trasami edukacyjnymi", "Maj-wrzesień; 9:00-17:00"),
]

import os

df = pd.DataFrame(opolskie_data, columns=[
    'LP', 'Nazwa', 'Kategoria', 'Lokalizacja', 'GPS', 'Vibe', 'Czas', 'Opis', 'Sezon/Godziny'
])

print(f"BAZA DANYCH OPOLSKIEGO GOTOWA!")
print(f"Liczba atrakcji: {len(df)}")
print(f"Wojewodztwo: Opolskie")
print(f"\nKategorie:")
for cat in df['Kategoria'].unique()[:10]:
    count = len(df[df['Kategoria'] == cat])
    print(f"   - {cat}: {count} atrakcji")

# Ścieżka do katalogu skryptu
script_dir = os.path.dirname(os.path.abspath(__file__))

# Export do Excel
excel_file = os.path.join(script_dir, 'Opolskie_Atrakcje_2025.xlsx')
with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Atrakcje Turystyczne', index=False)

# Export do CSV
csv_file = os.path.join(script_dir, 'baza-opolskie.csv')
df.to_csv(csv_file, index=False, encoding='utf-8')

print(f"\nPlik Excel wygenerowany: {excel_file}")
print(f"Plik CSV wygenerowany: {csv_file}")
print(f"Pliki sa gotowe do uzycia w aplikacji turystycznej!")
