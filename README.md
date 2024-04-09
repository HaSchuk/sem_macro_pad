# Infos
Projektordner
one-neokey -> eigentliche Entwicklungsbasis
two-neokey -> Basis von Anbieter ähnliches Modell
adafruit-files -> Examples

code.py -> Programmablauf -> Codequalität anheben

Makros -> Alle Eingaben die durch Eingabegeräte erfolgen kann -> Hier wird der Tastaturcode, Farbe und Displayausgabe definiert

4 Tasten ganz außen (1x4) -> Feste Belegung, keine Änderung durch Presets
12 Tasten in der Mitte (3x4) -> Werden durch preset umgestellt

Joystick 

Encoder - Drehrad
7 Encoder gesamt
1 encoder -> rechts oben über Tastatur -> Tastatur Presets (Quanta | LIMS)

6 encoder -> aktionen auf REM
- manueller Fokus
- Vergrößerung
- Stage Bewegung

Presets Infos
- LIMS sind 6 Encoder und der Joystick
- Quanta

ToDo:
- [X] A01 >> code.py: Dokumentation der Hardware-Abfragen bis Zeile 209
- [ ] A02 >> code.py: Entfernen der print-Kontroll-Ausgaben
- [X] A03 >> code.py: Einarbeitung Hardware-Abfrage 5+ Action-Encoder mit # - Kommentierung (Anmerkung, 4 von 8 gelieferten Encodern defekt) 
- [ ] A04 >> Macro quanta.py: Einarbeitung Action-Encoder plus Joystick
- [X] A05 >> code.py: Neokey1x4 mit statischen Tastenbelegungen bei while definieren
- [X] A06 >> code.py: Neokey1x4, oberste Taste, soll zusätzlich zum Preset-Encoder die Presets 1/2 umschalten. Hinterlegung von verschiedenen Farben (Neopixel)  für Preset 1 / 2
- [ ] A07 >> code.py: Bereinigung (classes, functions) für Hardware-Abfragen, evtl. Nachladen von py-files
- [ ] A08 >> cody.py: Generelles Anpassen ab Zeile 210
- [ ] A09 >> cody.py: Test ab 18.03. an Software, wie sich die Tasten-Emulationen verhalten, evtl. Auswirkung auf A5
- [X] A10 >> Hardware: Anschaffung Testbauteile > Joystick, Encoder, Neokey1x4
- [ ] A11 >> Gehäuse: Konstruktion und 3D-Druck (2x) Bracket
- [X] A12 >> Test Prototyp an Software
- [ ] B01 >> code.py: display_io > dynamisches Anzeigeverhalten OLED bei Nutzung Encoder bzw. Joystick << V2 des Codes

# sem_macro_pad
This project is based on the Adafruid MarcroPad: https://learn.adafruit.com/adafruit-macropad-rp2040 and is a fork of https://github.com/pixelpushinfreak/key_tickler_macro_pad

It's a modification for microscope control by using key shortcuts for controlling the software.

MacroPad will be extended with one of Stemma Qt 1x4 NeoKeys (https://www.adafruit.com/product/4980), six of the Stemma Qt Rotary Encoders (https://www.adafruit.com/product/4991) and one SparkFun Qwiic Joystick (https://www.sparkfun.com/products/15168). For SparkFun Qwiic Joystick the appropraite circuitpython lib is (https://github.com/fourstix/Sparkfun_CircuitPython_QwiicJoystick) is used.

A link for a 3D printable enclosure will be added after finishing the project.
