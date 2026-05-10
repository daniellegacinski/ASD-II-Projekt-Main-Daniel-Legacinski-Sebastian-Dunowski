# Projekt I — Akademicki system zajęć, frekwencji i ocen

Gotowy projekt webowy wykonany w Python Flask + SQLite. Design: czerwono-biało-czarny.

## Konta testowe
- Administrator: `admin@demo.pl` / `admin123`
- Prowadzący 1: `anna@demo.pl` / `teacher123`
- Prowadzący 2: `piotr@demo.pl` / `teacher123`
- Student: `daniel@demo.pl` / `student123`

## Uruchomienie w PowerShell / Git Bash
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\activate
# Git Bash:
source .venv/Scripts/activate
pip install -r requirements.txt
python app.py
```
Potem otwórz w przeglądarce: `http://127.0.0.1:5000`

## Co jest zrobione
- 3 role: administrator, prowadzący, student.
- Semestr OPEN/CLOSED, po zamknięciu blokada edycji.
- Kursy, grupy, przypisanie studentów i prowadzących.
- Spotkania: STANDARD, CANCELLED, RESCHEDULED, EXTRA.
- Generator spotkań cyklicznych w danych startowych.
- Frekwencja: PRESENT=1.0, LATE=0.5, ABSENT=0.0, EXCUSED nie liczy się do mianownika.
- Status AT_RISK, gdy frekwencja < 60% i liczba spotkań >= 3.
- Kategorie ocen z wagami, suma wag = 100%.
- Oceny w skali 2.0–5.0, po jednej ocenie w kategorii.
- Średnia ważona zaokrąglana do 2 miejsc.
- Eksport CSV.
- Dane demonstracyjne: 2 kursy, 2 prowadzących, min. 8 studentów, semestr OPEN i CLOSED.
- Testy automatyczne.

## Testy
```bash
pytest
```
