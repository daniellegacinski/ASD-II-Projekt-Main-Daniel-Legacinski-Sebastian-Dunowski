# ASD-II-Projekt-Main-Daniel-Legacinski-Sebastian-Dunowski

Akademicki System Zajęć, Frekwencji i Ocen
Opis projektu
---
Projekt został wykonany jako system akademicki do zarządzania:
zajęciami,
frekwencją,
ocenami,
semestrami,
użytkownikami,
eksportem danych.

System obsługuje trzy role:
Administrator
Prowadzący
Student

Projekt został przygotowany zgodnie z wymaganiami dokumentacji projektu.

Główne funkcje systemu:

Administrator
Administrator może:
tworzyć semestry,
otwierać i zamykać semestr,
tworzyć kursy,
tworzyć grupy,
przypisywać studentów,
przypisywać prowadzących.

Prowadzący
Prowadzący może:
zarządzać własnymi grupami,
dodawać spotkania,
oznaczać frekwencję,
wystawiać oceny,
tworzyć kategorie ocen,
eksportować dane.

Student
Student posiada wyłącznie podgląd:
planu zajęć,
frekwencji,
ocen,
średniej ważonej.
Student nie posiada uprawnień edycyjnych.

Frekwencja
System obsługuje statusy:
Status	Wartość
PRESENT	1.0
LATE	0.5
ABSENT	0.0
EXCUSED	nie liczy się
Status AT_RISK

Student otrzymuje status:
AT_RISK
gdy:
frekwencja < 60%
i liczba spotkań >= 3
Oceny

Obsługiwana skala ocen:
2.0
2.5
3.0
3.5
4.0
4.5
5.0

Średnia ważona:
liczona wyłącznie z istniejących ocen,
zaokrąglana do 2 miejsc po przecinku.
Technologie

Projekt został wykonany przy użyciu:
Python
Flask
SQLite
HTML
CSS
Bootstrap
Design projektu

Projekt wykorzystuje nowoczesny design w kolorach:
czerwony,
biały,
czarny.

Interfejs został przygotowany w stylu konferencyjnym oraz prezentacyjnym.
Struktura projektu

akademicki_system/
│
├── app.py
├── requirements.txt
├── README.md
├── database.db
│
├── templates/
├── static/
├── tests/
└── exports/

Uruchomienie projektu
1. Pobranie projektu
Pobierz projekt ZIP lub sklonuj repozytorium:
git clone (https://github.com/daniellegacinski/ASD-II-Projekt-Main-Daniel-Legacinski-Sebastian-Dunowski)
2. Wejście do folderu projektu
cd akademicki_system
3. Instalacja bibliotek
pip install -r requirements.txt
4. Uruchomienie aplikacji
python app.py
5. Otworzenie projektu

W przeglądarce:
http://127.0.0.1:5000
Konta testowe
Administrator
login: admin@example.com
hasło: admin123
Prowadzący
login: teacher1@example.com
hasło: teacher123
Student
login: student1@example.com
hasło: student123
Testy

Projekt zawiera testy:
poprawności frekwencji,
średniej ważonej,
uprawnień użytkowników,
blokady edycji po zamknięciu semestru,
poprawności generowania spotkań.
Bezpieczeństwo

W projekcie zastosowano:
autoryzację użytkowników,
role systemowe,
kontrolę dostępu,
walidację backendową,
przechowywanie haseł jako hash + salt.
Dane demonstracyjne

Projekt zawiera:
1 semestr OPEN,
1 semestr CLOSED,
minimum 2 kursy,
minimum 2 prowadzących,
minimum 8 studentów,
przykładowe oceny,
przykładową frekwencję.

Autory:
Daniel Legacinski
Sebastian Dunovski
Uniwersytet w Białymstoku
