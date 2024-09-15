import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import random
import tkinter as tk
from os import getcwd
import sys
import webbrowser
from PIL import ImageTk,Image  


#Παλέτα χρωμάτων
NODE_COL = '#fcbf49'  # χρωματάκι νεκταρινί :)
BG_COL = '#eae2b7'
MST_COL = "#d62828"
GRAPH_COL = "#003049"


#Ορίζουμε την κλάση GUI - Γραφικό Περιβάλλον
class GUI():
    '''Σχεδιάζει το γραφικό περιβάλλον με χρήση tkinter και χειρίζεται το input του χρήστη'''

    def __init__(self, root):   # Αρχικοποίηση τησ κλάσης
        self.root = root
        self.root.title("Minimum Spaning Tree Calculator")
        self.root.iconbitmap("icon.ico")
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)
        self.root.geometry('900x700')
        
        self.akmes = {}
        self.korifes = []
               
        self.buttons()
        self.canvas_and_frame()
        self.ioframe()

        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        self.fr = tk.Frame(self.root, height=20, bd=2, relief=tk.SUNKEN, bg=BG_COL)
        self.fr.grid(row=2, column=0, columnspan=2, sticky='snew')

        self.root.update()
        self.root.minsize(root.winfo_width(), root.winfo_height())


    def weight_check(self, varos): # Ελεγχος της ορθότητας των δεδομένων που εισάγει ο χρήστης
        if not varos.replace(".", "", 1).replace("-", "").isnumeric():
            self.entry_box.delete(0, "end")

            return 1

        elif float(varos) <= 0:
            self.entry_box.delete(0, "end")
            return 2

        else:
            return 0


    def buttons(self):  # Δημιουργεί τα κουμπιά
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.buttons_frame.columnconfigure(1, weight=1)
        

        self.manualbutton = tk.Button(
            self.buttons_frame, text="Χειροκίνητη εισαγωγή", cursor="hand2", command=self.input_manually, width=20)
        self.manualbutton.grid(row=0, column=0, pady=(50,5))

        self.random_button = tk.Button(
            self.buttons_frame, text="Τυχαίο γράφημα", cursor="hand2", command=self.input_random, width=20)
        self.random_button.grid(row=1, column=0, pady=(0, 5))

        self.file_button = tk.Button(
            self.buttons_frame, text="Εισαγωγή από αρχείο", cursor="hand2", command=self.input_file, width=20)
        self.file_button.grid(row=2, column=0, pady=(0, 60))

        self.calculate = tk.Button(
            self.buttons_frame, text='Υπολογισμός', cursor="hand2", state='disabled', command=self.mst)
        self.calculate.grid(row=5, column=0,pady=(31.36, 0))

        self.algorithm = tk.IntVar()

        R1 = tk.Radiobutton(self.buttons_frame, text="Αλγόριθμος του Prim", cursor="hand2",
                            variable=self.algorithm, value=1)
        R1.grid(row=3, column=0)

        R2 = tk.Radiobutton(self.buttons_frame,
                            text="Αλγόριθμος του Kruskal", cursor="hand2", variable=self.algorithm, value=2)
        R2.grid(row=4, column=0)

        
        self.info_button = tk.Button(
            self.buttons_frame, text='Οδηγίες', cursor="hand2", command=self.info_window)
        self.info_button.grid(row=6, column=0, sticky='s', pady=(40, 0))

        self.buttons_frame.rowconfigure((6,7), weight=1)

        self.credits_button = tk.Button(self.buttons_frame, text='Δημιουργοί προγράμματος', cursor="hand2", command=self.credits_window)
        self.credits_button.grid(row=7, column=0, sticky='s', padx=10)

        
        self.ccimg = Image.open('creative_commons.png')
        
        width, height = self.ccimg.size
        new_width = 158
        new_height = int(new_width * height / width)

        self.img = self.ccimg.resize((new_width, new_height), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.img)

        self.ccbutton = tk.Label(self.buttons_frame, image =self.img, cursor="hand2")
        self.ccbutton.grid(row=8,column=0)
        self.ccbutton.bind('<Button-1>', lambda x_: webbrowser.open(
            'https://creativecommons.org/licenses/by-nc-nd/4.0/'))

        cctext = "This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives\n4.0 International License."

        def del_cctext(event):
            self.text_box.configure(state='normal')
            self.text_box.delete('end-116c', 'end')
            self.text_box.insert('end', '\n')
            self.text_box.see("end")
            self.text_box.configure(state='disabled')
        
        self.ccbutton.bind('<Enter>', lambda y_: self.add_text(cctext))
        self.ccbutton.bind('<Leave>', del_cctext)
    
    def canvas_and_frame(self):   # Δημιουργεί τον καμβά που εμφανίζεται το Minimum Spaning Tree
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.grid(row=0, column=1, sticky=("nsew"))
        
        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

        self.fig = plt.figure(figsize=(5, 4), dpi=100)
        self.fig.set_facecolor(BG_COL)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame,)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=("nsew"))

        self.Toolbar = NavigationToolbar2Tk(
            self.canvas, self.plot_frame, pack_toolbar=False)
        self.Toolbar.grid(row=1,column=0, sticky=("sew"))

    def ioframe(self):  # Δημιουργεί το δεξί frame αλληλεπίδρασης
        self.io_frame = tk.Frame(self.root)
        self.io_frame.grid(row=1, column=1, sticky=("nsew"))

        self.text_box = tk.Text(self.io_frame, height=10, state='disabled')
        self.text_box.pack(fill='both', expand=True)

        self.entry_box = tk.Entry(self.io_frame, state='disabled', font='Calibri 14')
        self.entry_box.pack(fill='x', expand=True)


    def add_text(self, txt):    # Εκτυπώνει το κείμενο txt στο Text widget 
        self.text_box.configure(state='normal')
        self.text_box.insert('end', txt+'\n')
        self.text_box.see("end")
        self.text_box.configure(state='disabled')

    def start_of_input(self):   # Αρχικοποίηση της εισαγωγής
        self.korifes = []
        self.G = nx.Graph()
        self.G.clear()
        self.akmes = {}
        self.minimum_spanning_tree = 0
        self.algorithm.set(0)
        self.calculate['state']='normal'
        self.text_box.configure(state='normal')
        self.text_box.delete('1.0', tk.END)
        self.text_box.configure(state='disabled')


    def input_file(self):   # Μέθοδος για εισαγωγή γραφήματος απο αρχείο
        self.start_of_input()
        self.add_text('Επιλογή αρχείου για το Δέντρο.')

        try:
            filepath = tk.filedialog.askopenfilename(
                initialdir=getcwd(), title="Επιλέξτε αρχείο", filetypes=(("Text files", "*.txt*"), ('Comma-Seperated Values', '*.csv*')))

            with open(filepath, 'r', encoding='utf-8') as f:
                i = 0
                for line in f:
                    cont = True
                    try:
                        x1, x2, n = line.split(",")
                    except:
                        self.add_text("Σφάλμα. Η μορφή του περιεχομένου του αρχείου δεν είναι αποδεκτή.")
                        self.calculate['state'] = 'disabled'
                        break

                    i += 1

                    try:
                        n = float(n)
                        if n <= 0:
                            self.add_text(
                                "Σφάλμα. Το βάρος είναι λάθος στη γραμμή "+str(i)+". Δεν μπορεί να είναι αρνητικό!")
                            self.calculate['state'] = 'disabled'
                            cont = False

                    except ValueError:
                        self.add_text(
                            "Σφάλμα. Το βάρος είναι λάθος στη γραμμή {}. Δεν μπορεί να είναι γράμμα!".format(i))
                        self.calculate['state'] = 'disabled'
                        cont = False

                    if not (x1 != x2 and "{}-{}".format(x1, x2) not in self.akmes.keys() and "{}-{}".format(x2, x1) not in self.akmes.keys()):
                        self.add_text(
                            "Σφάλμα. Ένα ζευγάρι κορυφών έχει εισαχθεί πάνω από μια φορά.")
                        self.calculate['state'] = 'disabled'
                        cont = False
                        break 
                    
        
                    if not cont:
                        break


                    if x1 not in self.korifes:
                        self.korifes.append(x1)
                    if x2 not in self.korifes:
                        self.korifes.append(x2)

                    self.akmes.update({"{}-{}".format(x1, x2): n})

                    self.G.add_edge(x1, x2, weight=n)

                if cont:
                    for key in self.akmes:
                        self.add_text("Ακμή: {:s} , βάρος: {:.2f}".format(
                            str(key), self.akmes[key]))

        except FileNotFoundError:
            self.add_text("Σφάλμα. Δεν επιλέξατε κάποιο αρχείο.")
            self.calculate['state'] = 'disabled'
            return

    def input_random(self):  # Μέθοδος για τυχαία εισαγωγή γραφήματος
        self.start_of_input()
        self.entry_box.configure(state='normal')

        def text_input(txt):
            if self.metritis == 0:
                txt = self.entry_box.get()
                state = self.weight_check(txt)
                
                if state == 1:
                    self.add_text("Σφάλμα. Το πλήθος των κορυφών δεν πρέπει να περιέχει γράμματα ή σύμβολα.")
                    return

                elif state == 2:
                    self.add_text(
                        "Σφάλμα. Το πλήθος των κορυφών δεν πρέπει να είναι αρνητικός αριθμός.")
                    return

                elif state==0:
                    try:
                        self.n = int(txt)
                    except:
                        self.add_text(
                            'Σφάλμα. Το πλήθος των κορυφών πρέπει να είναι ακέραιος αριθμός.')
                        self.entry_box.delete(0, "end")
                        return
                    self.metritis += 1
                    self.add_text(
                        "Το πλήθος των κορυφών είναι: {} \nΔώστε το μέγιστο δυνατό βάρος των ακμών".format(self.n))
                    self.entry_box.delete(0, "end")
                    return

            if self.metritis == 1:
                txt = self.entry_box.get()
                state = self.weight_check(txt)

                if state == 1:
                    self.add_text(
                        "Σφάλμα. Το μέγιστο δυνατό βάρος δεν πρέπει να περιέχει γράμματα ή σύμβολα.")
                    return

                elif state == 2:
                    self.add_text(
                        "Σφάλμα. Το μέγιστο δυνατό βάρος πρέπει να είναι θετικό.")
                    return

                elif state==0:
                    try:
                        g = int(txt)
                    except:
                        self.add_text(
                            'Σφάλμα. Το μέγιστο δυνατό βάρος πρέπει να είναι ακέραιος αριθμός.')
                        self.entry_box.delete(0, "end")
                        return

                    self.metritis -= 1
                    self.add_text(
                        "Το μέγιστο δυνατό βάρος των ακμών είναι {} \nΤο τυχαίο γράφημα δημιουργήθηκε!!".format(g))
                    self.entry_box.delete(0, "end")
                else:
                    return

            self.korifes = []
            self.G = nx.Graph()
            self.G.clear()
            self.akmes = {}

            a = 0   # a = μεγιστος αριθμος ακμων
            
            for i in range(1, self.n):
                a += self.n-i

            b = self.n-1    # b = ελαχιστο πληθος ακμων για συνδεδεμενο γραφο
            
            for i in range(1, self.n + 1, 1):
                self.korifes.append(i)

            c = random.randint(1, 4)    # c = τυχαια επιλογη επαναληψης προσθηκης ακμων
            
            while True:
                for i in range(b, a+c):
                    x1 = random.choice(self.korifes)
                    x2 = random.choice(self.korifes)
                    v = random.randint(1, g)
                    if x1 != x2 and "{}-{}".format(x1, x2) not in self.akmes.keys() and "{}-{}".format(x2, x1) not in self.akmes.keys():
                        self.akmes.update({"{}-{}".format(x1, x2): v})
                        self.G.add_edge(x1, x2, weight=v)
                if nx.is_connected(self.G) == True and self.G.order() == self.n:
                    break

            for key in self.akmes:
                    self.add_text("Ακμή: {:s} , βάρος: {:.2f}".format(
                        str(key), self.akmes[key]))

            self.add_text(
                "Αν θέλετε να δημιουργήσετε νέο τυχαίο δέντρο, γράψτε το επιθυμητό πλήθος των κορυφών του.\nΑν θέλετε να εμφανίσετε το MST διαλέξτε αλγόριθμο και πατήστε Υπολογισμός.")

        self.add_text("Δώστε το πλήθος των κορυφών του τυχαίου γραφήματος.")
        self.metritis = 0
        self.entry_box.bind("<Return>", text_input)

    def input_manually(self):   # Μέθοδος για χειροκίνητη εισαγωγή γραφήματος απο τον χρήστη
        self.start_of_input()
        self.entry_box.configure(state='normal')

        def input_manually2(txt):
            txt = str(self.entry_box.get())
            self.entry_box.delete(0, tk.END)
            if txt == "stop":
                self.entry_box.configure(state='disabled')
                return

            try:
                x1, x2, n = txt.split(",")

                if x1 == x2 and (x1 or x2) :
                    self.add_text(
                        "Σφάλμα. Παρακαλώ δώστε διαφορετικές κορυφές.")
                    return
                elif not x1 or not x2:
                    self.add_text(
                        'Σφάλμα. Οι κορυφές πρέπει να περιέχουν αλφαριθμητικούς χαρακτήρες.')
                    return


            except ValueError:
                self.add_text("Σφάλμα. Παρακαλώ δώστε διαφορετικές κορυφές.")
                return

            

            state = self.weight_check(n)
            if state==1:
                self.add_text(
                    "Σφάλμα. Το βάρος δεν πρέπει να περιέχει γράμματα.")
                return

            elif state==2:
                self.add_text("Σφάλμα. Το βάρος πρέπει να ειναι θετικό.")
                return

            if x1 not in self.korifes:
                self.korifes.append(x1)
            if x2 not in self.korifes:
                self.korifes.append(x2)

            n = float(n)

            if x1 != x2 and "{}-{}".format(x1, x2) not in self.akmes.keys() and "{}-{}".format(x2, x1) not in self.akmes.keys():
                self.akmes.update(
                    {"{}-{}".format(x1, x2): round(n, ndigits=2)})
                self.G.add_edge(x1, x2, weight=round(n, ndigits=2))
                self.add_text("{}, {}, {}".format(x1, x2, n))
            else:
                self.add_text("Σφάλμα. Παρακαλώ δώστε διαφορετικές κορυφές.")
                return

        self.entry_box.bind("<Return>", input_manually2)
        self.add_text(
            'Δώστε τις ακμές (μορφή: κορυφή1,κορυφή2,βάρος)\n(Πληκτολογήστε stop για να ολοκληρώσετε τις εισόδους σας)')
        self.akmes = {}
        self.korifes = []
        self.G = nx.Graph()


    def mst(self): # Υπολογισμός του Minimum Spaning Tree με χρήση του καταλληλου αλγορίθμου απο την κλάση MST
        if self.algorithm.get() == 0:
            self.add_text(
                'Σφάλμα. Παρακαλώ επιλέξτε πρώτα τον αλγόριθμο επίλυσης.')
        
        elif MST.solvable_check(self, self.G, self.korifes):
            if self.algorithm.get() == 1:
                self.minimum_spanning_tree, sum_of_w = MST.prim_graph(self, self.akmes)
                self.add_text('Το Ελάχιστο Διασυνδετικό Δέντρο του Prim, με συνολικό βάρος: {}.'.format(sum_of_w))
                
                self.draw_graph()

            elif self.algorithm.get() == 2:
                self.minimum_spanning_tree, sum_of_w = MST.kruskal_graph(
                    self, self.akmes)
                self.add_text(
                    'Το Ελάχιστο Διασυνδετικό Δέντρο του Kruskal, με συνολικό βάρος: {}.'.format(sum_of_w))
                
                self.draw_graph()

    def draw_graph(self):   # Σχεδιασμός γραφήματος στον καμβά 
        plt.clf()

        colors = nx.get_edge_attributes(
            self.minimum_spanning_tree, 'color').values()

        pos = nx.spring_layout(self.minimum_spanning_tree)

        labels = nx.get_edge_attributes(self.minimum_spanning_tree, 'weight')

        nx.draw(self.minimum_spanning_tree, pos, edge_color=colors, width=3,
                with_labels=True, node_color=NODE_COL, node_size=400)

        nx.draw_networkx_edge_labels(
            self.minimum_spanning_tree, pos, alpha=1, bbox=dict(boxstyle='Circle,pad=0.1', facecolor=BG_COL, edgecolor=BG_COL), edge_labels=labels, rotate=False)

        self.fig.set_facecolor(BG_COL)
        self.canvas.draw()


    def ask_quit(self): # Εξοδος απο το πρόγραμμα
        if tk.messagebox.askokcancel("Έξοδος", "Θέλετε να τερματίσετε το πρόγραμμα;"):
            self.root.destroy()
            sys.exit()

    def credits_window(self):   # Εμφάνιση δημιουργών προγράμματος 
        self.creditsWindow = tk.Toplevel(self.root)
        self.creditsWindow.title("Δημιουργοί προγράμματος")
        self.creditsWindow.iconbitmap("icon.ico")
        line1 = str("Αυτό το πρόγραμμα δημιουργήθηκε από τους:")
        line2 = str("Βλησίδης Γεώργιος\nvlisidisge002@gmail.com")
        line3 = str("Γεωργακόπουλος Γεώργιος\ngeorgegeo248@gmail.com")
        line4 = str("Κελεσίδης Αναστάσης\nkelesidis123@gmail.com")
        line5 = str("Λελάκης Πάνος\nplelakis@gmail.com")
        line6 = str("Σκαπινάκης Στρατής\nskapinakiss@gmail.com")
        line7 = str("Τσιατσιάνας Ευάγγελος\nvagtsiats12@gmail.com")
        self.creditsText = tk.Text(self.creditsWindow, height=19, width=50, state='normal')
        self.creditsText.pack()
        self.creditsText.insert(tk.INSERT, line1)
        self.creditsText.insert(tk.INSERT, '\n' + '\n' + line2)
        self.creditsText.insert(tk.INSERT, '\n' + '\n' + line3)
        self.creditsText.insert(tk.INSERT, '\n' + '\n' + line4)
        self.creditsText.insert(tk.INSERT, '\n' + '\n' + line5)
        self.creditsText.insert(tk.INSERT, '\n' + '\n' + line6)
        self.creditsText.insert(tk.INSERT, '\n' + '\n' + line7)
        self.creditsText.configure(state='disabled')

        self.creditsWindow.resizable(0, 0)

    def info_window(self):  # Εμφάνιση οδηγιών χρήσης του προγράμματος
        self.infowindow = tk.Toplevel(self.root)
        self.infowindow.title("Οδηγίες")
        self.infowindow.iconbitmap("icon.ico")

        self.info_text = tk.Text(self.infowindow, height=47, width=100)

        with open('info.txt', 'r', encoding='utf-8') as f:
            for line in f:
                self.info_text.insert('end', line)

        self.info_text.pack()
        self.info_text.configure(state='disabled')

        self.infowindow.resizable(0, 0)


#Ορίζουμε την κλάση MST
class MST():
    '''Περιέχει μεθόδους που υπολογίζουν το Minimum Spaning Tree και μεθόδους ελέγχου'''

    def solvable_check(self, G, korifes):   # Έλεγχος καταλληλότητας του γραφήματος
        solvable = True
        if len(korifes) > 2:
            if nx.is_connected(G) == False:
                GUI.add_text(self, "Σφάλμα. Το γράφημα δεν είναι συνδεδεμένο.")
                solvable = False
        else:
            GUI.add_text(self, "Σφάλμα. Ο οριθμός των κορυφών δεν επαρκεί για την δημιουργία γραφήματος.")
            solvable = False
        
        return solvable

    def prim_graph(self, dict1):    # Αλγόριθμος του Prim για τον υπολογισμό του Minimum Spaning Tree
        self.dict1 = dict1

        cnctd_nodes = []
        korifes = []
        sum_of_w = 0

        H = nx.Graph()
        D = nx.Graph()

        for edge in self.dict1.items():
            x1, x2 = edge[0].split("-")

            H.add_edge(x1, x2, color=GRAPH_COL,
                       weight=round(edge[1], ndigits=2))

            if x1 not in korifes:
                korifes.append(x1)
            if x2 not in korifes:
                korifes.append(x2)

        r = random.choice(korifes)
        cnctd_nodes.append(r)

        while True:
            nbrs = {}
            for i in cnctd_nodes:
                for edge in self.dict1.items():
                    if i in edge[0]:
                        nbrs.update({edge[0]: edge[1]})

            nbrs = dict(sorted(nbrs.items(), key=lambda item: item[1]))

            for babushka in nbrs.items():  # love_babushka
                add_edge = [babushka[0].split("-")[0], babushka[0].split("-")[1]]

                try:
                    if D.has_edge(add_edge[0], add_edge[1]):
                        continue

                    D.add_edge(add_edge[0], add_edge[1])
                    H.edges[add_edge[0], add_edge[1]]['color'] = MST_COL
                    sum_of_w += babushka[1]

                    nx.find_cycle(D)

                    H.edges[add_edge[0], add_edge[1]]['color'] = GRAPH_COL
                    D.remove_edge(add_edge[0], add_edge[1])
                    sum_of_w -= babushka[1]

                except:
                    for n in add_edge:
                        if n not in cnctd_nodes:
                            cnctd_nodes.append(n)
                    break

            if D.order() == len(korifes):
                break

        return H , sum_of_w

    def kruskal_graph(self, dict1): # Αλγόριθμος του Kruskal για τον υπολογισμό του Minimum Spaning Tree
        self.dict1 = dict1

        self.dict1 = dict(sorted(self.dict1.items(), key=lambda item: item[1]))

        H = nx.Graph()
        D = nx.Graph()
        sum_of_w = 0

        for edge in self.dict1.items():
            x1, x2 = edge[0].split("-")

            H.add_edge(x1, x2, color= GRAPH_COL,
                       weight=round(edge[1], ndigits=2))

            try:
                D.add_edge(x1, x2)
                H.edges[x1, x2]['color'] = MST_COL
                sum_of_w += edge[1]

                nx.find_cycle(D)

                H.edges[x1, x2]['color'] = GRAPH_COL
                D.remove_edge(x1, x2)
                sum_of_w -= edge[1]

            except:
                continue

        return H, sum_of_w


#Ορίζουμε την κλάση Βασικό Πρόγραμμα
class Main():
    '''Βασικές λειτουργίες προγράμματος'''

    root = tk.Tk()
    GUI(root)
    root.mainloop()


Main()
