# Pipeline Snakemake do analizy poziomu zanieczyszczeń (PM2.5) i przeglądu literatury PubMed

Projekt ma na celu  wizualizację danych dotyczących poziomu zanieczyszczenia powietrza PM2.5 w wybranych
polskich miastach oraz zestawienie tych wyników z trendami w literaturze naukowej, co pozwala na lepszą 
interpretację zmian poziomu zanieczyszczenia powietrza w czasie.

----------

#### Repozytorium zawiera:
* Pliki z kodem źródłowym:
  * `load_data.py` - moduł odpowiedzialny za wczytywanie i czyszczenie danych
  * `compute_averages.py` - moduł, który oblicza średnie dla miast zawartych w danych wejściowych
  * `visualizations.py` - moduł generujący wykresy i wizualizacje danych
  * `main.ipynb` - notebook, który pokazuje użycie wszystkich modułów
* Pliki danych:
  * `all_data.csv` - surowe dane wejściowe używane w późniejszych obliczeniach i ogólnej analizie
  * `monthly_average.csv` - miesięczne średnie stężenia PM2.5 w miastach, które są zawarte w pliku all_data.csv

---------

#### Jak zainstalować i uruchomić projekt?

1. Sklonuj repozytorium
```bash
git clone https://github.com/dominikaa312/projekt4_ztp
```

2. Utwórz wirtualne środowisko (zalecane)
```bash
python -m venv venv
source ./venv/bin/activate
```
3. Zainstaluj potrzebne biblioteki
```bash
pip install -r requirements.txt
```

---------

#### Źródła danych

[Główny Inspektorat Ochrony Środowiska – powietrze.gios.gov.pl](https://powietrze.gios.gov.pl/pjp/archives)

---------

### Autor: Dominika Aniszewska
