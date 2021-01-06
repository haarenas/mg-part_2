from django.db import models
import re


class Converter(models.Model):

    managed = False

    def __init__(self):
        self.dicc_rom = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
        self.dicc_alien = {}
        self.iron = -1
        self.silver = -1
        self.gold = -1
        self.output = []

    def parse_line(self, string):
        palabras = string.split()
        palabras_low = [x.lower() for x in palabras]
        if len(palabras) == 3 and palabras_low[1] == "is" and palabras[2] in self.dicc_rom: #asignacion de palabras
            self.add_key(palabras_low[0], palabras[2])
        elif len(palabras) > 3 and set(palabras_low) & {"iron", "silver", "gold"} and palabras[-1] != "?": #valorizacion metales
            self.validate_metals(palabras_low)
        elif len(palabras) > 3 and palabras[-1] == "?" and "credits" not in palabras_low: #pregunta numerica
            self.validate_num_question(palabras_low)
        elif len(palabras) > 3 and palabras[-1] == "?" and "credits" in palabras_low and set(palabras_low) & {"iron", "silver", "gold"}: #pregunta de creditos
            self.validate_cred_question(palabras_low)
        else:
            self.add_output(f"I dont understand that question")

    #Agregar key,value al diccionario alien
    def add_key(self, key, value):
        if key not in self.dicc_alien and value in self.dicc_rom:
            self.dicc_alien[key] = value.upper()
        elif key in self.dicc_alien:
            self.add_output(f"Another value to {key}?! previous value was {self.dicc_alien[key]}.")

    
    #Transformar numeral romano a decimal: https://www.tutorialspoint.com/program-to-convert-roman-numeral-to-integer-in-python
    def roman_to_decimal(self, numeral):
        ans = 0
        n = len(numeral)
        for (idx, c) in enumerate(numeral):
            if idx < n - 1 and self.dicc_rom[c] < self.dicc_rom[numeral[idx + 1]]:
                ans -= self.dicc_rom[c]
            else:
                ans += self.dicc_rom[c]
        return ans


    #Regex para validar el numeral romano: https://stackoverflow.com/questions/267399/how-do-you-match-only-valid-roman-numerals-with-a-regular-expression
    def is_roman_invalid(self, numeral):
        if re.match(r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", numeral):
            return False
        else:
            return True


    def alien_to_roman(self, lista):
        str_roman = ""
        for word in lista:
            str_roman += self.dicc_alien[word]
        return str_roman


    def add_output(self, string):
        self.output.append(string+"\n")


    def validate_metals(self, palabras_low):
        index = palabras_low.index("is")
        subject = palabras_low[:index-1]
        metal = self.get_metal_str(palabras_low)
        cifra = palabras_low[index+1]
        if self.check_metal(metal):
            self.add_output(f"Another value for {metal}?!. {metal} is already defined")
            return
        ret_valiadation = self.validate_subject(subject)
        if ret_valiadation != "":
            self.add_output(f"Not enough information to answer that question. '{ret_valiadation}' is not defined or invalid question")
            return
        numeral = self.alien_to_roman(subject)
        if self.is_roman_invalid(numeral):
            str_alien = " ".join(subject)
            self.add_output(f"Are you sure that {str_alien} is a correct value?. ({numeral} is not valid)")
            return
        valor = self.roman_to_decimal(numeral)
        self.add_metal(metal, valor, cifra)
        

    def get_metal_str(self, palabras_low):
        if "iron" in palabras_low:
            return "iron"
        elif "silver" in palabras_low:
            return "silver"
        else:
            return "gold"


    def get_metal_value(self, metal):
        if metal == "iron":
            return self.iron
        elif metal == "silver":
            return self.silver
        else:
            return self.gold


    def check_metal(self, metal):
        if metal == "iron" and self.iron != -1:
            return True
        elif metal == "silver" and self.silver != -1:
            return True
        elif metal == "gold" and self.gold != -1:
            return True
        else:
            return False


    def add_metal(self, metal, value, cifra):
        if metal == "iron" and self.iron == -1:
            self.iron = int(cifra)/int(value)
        elif metal == "silver" and self.silver == -1:
            self.silver = int(cifra)/int(value)
        elif metal == "gold" and self.gold == -1:
            self.gold = int(cifra)/int(value)


    def validate_num_question(self, palabras_low):
        if self.is_valid_question(palabras_low) == False:
            self.add_output(f"I dont understand that question")
            return
        index = palabras_low.index("is")
        subject = palabras_low[index +1:-1]
        ret_valiadation = self.validate_subject(subject)
        if ret_valiadation != "":
            self.add_output(f"Not enough information to answer that question. '{ret_valiadation}' is not defined or invalid question")
            return
        numeral = self.alien_to_roman(subject)
        if self.is_roman_invalid(numeral):
            str_alien = " ".join(subject)
            self.add_output(f"Are you sure that {str_alien} is a correct value?. ('{numeral}' is not valid)")
            return
        valor = self.roman_to_decimal(numeral)
        str_alien = " ".join(subject)
        self.add_output(f"{str_alien} is {valor}")


    def is_valid_question(self, palabras_low):
        for word in palabras_low:
            if word in self.dicc_alien:
                return True
        return False


    def validate_subject(self, subject):
        for word in subject:
            if word not in self.dicc_alien:
                return word
        return ""


    def validate_cred_question(self, palabras_low):
        if self.is_valid_question(palabras_low) == False:
            self.add_output(f"I dont understand that question")
            return
        index = palabras_low.index("is")
        subject = palabras_low[index +1:-2]
        ret_valiadation = self.validate_subject(subject)
        if ret_valiadation != "":
            self.add_output(f"Not enough information to answer that question. '{ret_valiadation}' is not defined or invalid question")
            return
        numeral = self.alien_to_roman(subject)
        if self.is_roman_invalid(numeral):
            str_alien = " ".join(subject)
            self.add_output(f"Are you sure that {str_alien} is a correct value?. ('{numeral}' is not valid)")
            return
        valor = self.roman_to_decimal(numeral)
        metal = self.get_metal_str(palabras_low)
        if self.check_metal(metal) is False:
            self.add_output(f"Not enough information to answer that question. ('{metal.capitalize()}' is not defined)")
            return
        str_alien = " ".join(subject)
        self.add_output(f"{str_alien} {metal.capitalize()} is {int(valor*self.get_metal_value(metal))} Credits")

