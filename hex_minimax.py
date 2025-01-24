import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
from collections import deque

class HexIgra:
    def __init__(self, velicina=4):
        self.velicina = velicina
        self.ploca = np.zeros((velicina, velicina), dtype=int)  
        self.posjeceno = set()

    def je_validan_potez(self, redak, stupac):
        return 0 <= redak < self.velicina and 0 <= stupac < self.velicina and self.ploca[redak, stupac] == 0

    def odigraj_potez(self, redak, stupac, igrac):
        if self.je_validan_potez(redak, stupac):
            self.ploca[redak, stupac] = igrac
            return True
        return False

    def reset_posjeceno(self):
        self.posjeceno.clear()

    def provjeri_put(self, trenutni, igrac):
        if igrac == 1 and trenutni[1] == self.velicina - 1: 
            return True
        if igrac == 2 and trenutni[0] == self.velicina - 1: 
            return True

        r, c = trenutni
        self.posjeceno.add((r, c))

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.velicina and 0 <= nc < self.velicina and (nr, nc) not in self.posjeceno and self.ploca[nr, nc] == igrac:
                if self.provjeri_put((nr, nc), igrac):
                    return True

        self.posjeceno.remove((r, c)) 
        return False

    def provjeri_pobjednika(self, igrac):
        self.reset_posjeceno()
        if igrac == 1:  
            for r in range(self.velicina):
                if self.ploca[r][0] == igrac:
                    if self.provjeri_put((r, 0), igrac):
                        return True
        elif igrac == 2: 
            for c in range(self.velicina):
                if self.ploca[0][c] == igrac:
                    if self.provjeri_put((0, c), igrac):
                        return True
        return False

    def dohvati_prazna_polja(self):
        return [(r, s) for r in range(self.velicina) for s in range(self.velicina) if self.ploca[r, s] == 0]

    def evaluiraj_plocu(self, igrac):
        bodovi = 0
        smjerovi = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for r in range(self.velicina):
            for s in range(self.velicina):
                if self.ploca[r, s] == igrac:
                    for dr, ds in smjerovi:
                        nr, ns = r + dr, s + ds
                        if 0 <= nr < self.velicina and 0 <= ns < self.velicina and self.ploca[nr, ns] == igrac:
                            bodovi += 1  
        return bodovi

    def minimax(self, dubina, max_igrac):
        if self.provjeri_pobjednika(2):
            return 100  
        if self.provjeri_pobjednika(1):
            return -100  
        if dubina == 0 or not self.dohvati_prazna_polja():
            return self.evaluiraj_plocu(2) - self.evaluiraj_plocu(1)  

        if max_igrac:
            max_eval = float('-inf')
            for (r, s) in self.dohvati_prazna_polja():
                self.ploca[r, s] = 2  
                eval = self.minimax(dubina - 1, False)
                self.ploca[r, s] = 0
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for (r, s) in self.dohvati_prazna_polja():
                self.ploca[r, s] = 1  
                eval = self.minimax(dubina - 1, True)
                self.ploca[r, s] = 0
                min_eval = min(min_eval, eval)
            return min_eval

    def najbolji_potez(self):
        for (r, s) in self.dohvati_prazna_polja():
            self.ploca[r, s] = 2
            if self.provjeri_pobjednika(2):
                self.ploca[r, s] = 0
                return (r, s)
            self.ploca[r, s] = 0

        najbolji_rezultat = float('-inf')
        potez = None
        for (r, s) in self.dohvati_prazna_polja():
            self.ploca[r, s] = 2
            rezultat = self.minimax(3, False) 
            self.ploca[r, s] = 0
            if rezultat > najbolji_rezultat:
                najbolji_rezultat = rezultat
                potez = (r, s)
        return potez

class HexIgraGUI:
    def __init__(self, velicina=4):
        self.velicina = velicina
        self.igra = HexIgra(velicina)
        self.prozor = tk.Tk()
        self.prozor.title("Hex Igra")

        self.igrac_prvi = True  

        self.gumbi = [[None for _ in range(velicina)] for _ in range(velicina)]
        for r in range(velicina):
            for s in range(velicina):
                gumb = tk.Button(self.prozor, text="", width=4, height=2, command=lambda r=r, s=s: self.igracev_potez(r, s))
                gumb.grid(row=r, column=s)
                self.gumbi[r][s] = gumb

        self.prozor.after(100, self.odabir_poretka)

    def odabir_poretka(self):
        odgovor = simpledialog.askstring("Odabir poretka", "Želite li igrati prvi? (da/ne)")
        if odgovor and odgovor.lower() in ["ne", "no"]:
            self.igrac_prvi = False
            self.ai_potez()  
        elif not odgovor or odgovor.lower() not in ["da", "ne", "yes", "no"]:
            messagebox.showwarning("Upozorenje", "Neispravan unos. Postavljeno je da igrač igra prvi.")

    def azuriraj_plocu(self):
        for r in range(self.velicina):
            for s in range(self.velicina):
                if self.igra.ploca[r, s] == 1:
                    self.gumbi[r][s]["text"] = "X"
                    self.gumbi[r][s]["state"] = "disabled"
                elif self.igra.ploca[r, s] == 2:
                    self.gumbi[r][s]["text"] = "O"
                    self.gumbi[r][s]["state"] = "disabled"

    def igracev_potez(self, redak, stupac):
        if self.igra.odigraj_potez(redak, stupac, 1):
            self.azuriraj_plocu()
            if self.igra.provjeri_pobjednika(1):
                messagebox.showinfo("Kraj igre", "Čestitamo, pobijedili ste!")
                self.prozor.destroy()
                return

            self.ai_potez()

    def ai_potez(self):
        potez = self.igra.najbolji_potez()
        if potez:
            r, s = potez
            self.igra.odigraj_potez(r, s, 2)
            self.azuriraj_plocu()
            if self.igra.provjeri_pobjednika(2):
                messagebox.showinfo("Kraj igre", "AI pobjeđuje! Više sreće sljedeći put.")
                self.prozor.destroy()

    def pokreni(self):
        self.prozor.mainloop()

if __name__ == "__main__":
    sucelje = HexIgraGUI(velicina=4)
    sucelje.pokreni()
