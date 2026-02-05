# Pipeline Snakemake do analizy poziomu zanieczyszczeń (PM2.5) i przeglądu literatury PubMed

Projekt ma na celu wizualizację danych dotyczących poziomu zanieczyszczenia powietrza PM2.5 w wybranych
polskich miastach oraz zestawienie tych wyników z trendami w literaturze naukowej z bazy PubMed, co pozwala na lepszą 
interpretację zmian poziomu zanieczyszczenia powietrza w czasie.

----------

#### Repozytorium zawiera:
* Pipeline Snakemake:
  * `Snakefile` - główny plik definiujący cały workflow
  * `config/task4.yaml` - plik konfiguracyjny
* Skrypty, które znajdują się w folderze `scripts/`:
  * `combined_years.py` - łączenie danych z lat podanych w pliku konfiguracyjnym
  * `compute_averages.py` - obliczanie średnich dla miast zawartych w danych wejściowych
  * `generate_year.py` - generowanie danych dla pojedynczego roku
  * `load_data.py` - wczytywanie i czyszczenie danych
  * `pm25_year.py` - generowanie pliku zawierającego liczbę dni z przekroczonym dopuszczalnym stężeniem PM2.5 w danym 
  roku oraz tworzenie wykresów ilustrujących zmiany stężeń PM2.5 w ciągu roku
  * `pubmed_fetch.py` - pobieranie publikacji z PubMed dla danego roku
  * `pubmed_functions.py` - funkcje, które są wykorzystywane przy pobieraniu publikacji z PubMed
  * `pubmed_summary.py` - stworzenie podsumowania publikacji z lat podanych w pliku konfiguracyjnym
  * `report_maker.py` - generowanie końcowego raportu w formacie Jupyter Notebook
  * `visualizations.py` - generowanie wizualizacji<br><br>

#### Dane wejściowe:
Pipeline generuje dane wejściowe w folderze `data/`:
* Folder `years/`, który zawiera pliki z dziennymi stężenia PM2.5 zarejestrowanymi na poszczególnych stacjach pomiarowych w danym roku
* Zbiorczy plik obejmujący dzienne stężenia PM2.5 ze wszystkich lat zdefiniowanych w pliku konfiguracyjnym
* Dane przedstawiające średnie dzienne stężenia PM2.5 w miastach
* Plik zawierający średnie miesięczne stężenia PM2.5 w miastach<br><br>

#### Dane wyjściowe:  
Pipeline generuje dane wyjściowe w folderze `results/`:
* Foldery dla lat podanych w pliku konfiguracyjnym, które zawierają:
  * Plik zawierający liczbę dni z przekroczonym dopuszczalnym stężeniem PM2.5 w pojedynczym roku
  * Średnie dzienne stężenie PM2.5 w danych miastach w jednym roku
  * Wizualizacje
  * Zestawienie publikacji PubMed
* Podsumowanie publikacji z lat podanych w pliku konfiguracyjnym
* Folder `reports/`, w którym znajdują się wygenerowane raporty

Pipeline Snakemake został tak skonfigurowany, że nie wykonuje reguł dla lat, które już były policzone, 
jeśli ich wejścia się nie zmieniły. Weryfikacja odbywa się przez porównanie czasu generowania plików do analizy i raportu
końcowego. Raport końcowy zawiera informację o czasie trwania pipeline, co umożliwia łatwe sprawdzenie, że program
szybciej przebiega przy mniejszej liczby plików do wygenerowania.<br><br>

---------

### Instalacja

1. Sklonuj repozytorium
```bash
git clone https://github.com/dominikaa312/projekt4_ztp
```

2. Utwórz i aktywuj wirtualne środowisko (zalecane)
```bash
python -m venv venv
source ./venv/bin/activate
```
3. Zainstaluj potrzebne biblioteki
```bash
pip install -r requirements.txt
```

---------

### Konfiguracja

Przed uruchomieniem pipeline'u należy uzupełnić plik:

    config/task4.yaml

Nalezy podać m. in.:
- lata analiz
- lista miast
- parametry zapytań do PubMed

---------

### Uruchomienie pipeline'u

1. Dry-run (sprawdzenie workflow)
```bash
snakemake -n
```

2. Pełne uruchomienie pipeline'u
```bash
snakemake --cores 1
```

---------

### Źródła danych

[Główny Inspektorat Ochrony Środowiska – powietrze.gios.gov.pl](https://powietrze.gios.gov.pl/pjp/archives)

[PubMed (NCBI)](https://pubmed.ncbi.nlm.nih.gov/)

---------

### Autor: Dominika Aniszewska
