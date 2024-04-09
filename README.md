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



# sem_macro_pad
This project is based on the Adafruid MarcroPad: https://learn.adafruit.com/adafruit-macropad-rp2040 and is a fork of https://github.com/pixelpushinfreak/key_tickler_macro_pad

It's a modification for microscope control by using key shortcuts for controlling the software.

MacroPad will be extended with one of their Stemma Qt 1x4 NeoKeys: https://www.adafruit.com/product/4980, six of the Stemma Qt Rotary Encoders: https://www.adafruit.com/product/4991 and one Stemma Mini I2C Gamepad (https://www.adafruit.com/product/5743)

A link for a 3D printable enclosure will be added after finishing the project.