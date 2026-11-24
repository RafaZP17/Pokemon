import csv
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

Catalogo_Pokemon = {}
pokemon_actual = None
animacion_id = None

COLORES_TIPO = {
    "ELECTRICO": "#F7D02C", "AGUA": "#6390F0", "FUEGO": "#EE8130",
    "PLANTA": "#7AC74C", "PSIQUICO": "#F95587", "SINIESTRO": "#705746",
    "FANTASMA": "#735797", "DRAGON": "#6F35FC", "LUCHA": "#C22E28",
    "BICHO": "#A6B91A", "NORMAL": "#A8A77A", "HIELO": "#96D9D6",
    "TIERRA": "#E2BF65", "ROCA": "#B6A136", "ACERO": "#B7B7CE",
    "HADA": "#D685AD", "VENENO": "#A33EA1", "VOLADOR": "#A98FF3"
}

menu = tk.Tk()
menu.title('Simulador Pokémon')
menu.geometry('1000x600')
menu.resizable(False, False)

def cargar_Pokemons():
    with open('pokemones_stats.csv', 'r', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        next(lector)

        for fila in lector:
            if not fila:
                continue

            nombre = fila[0]
            Catalogo_Pokemon[nombre] = {
                "tipo": fila[1].strip().upper(),
                'vida': int(fila[2]),
                'ataque': int(fila[3]),
                'defensa': int(fila[4]),
                "velocidad": int(fila[5]),
                'move1': fila[6],
                'dmg1': int(fila[7]),
                'move2': fila[8],
                'dmg2': int(fila[9]),
                'icono': f"Pokemones/Icon/{fila[10].strip()}",
                'gif_frente': f"Pokemones/Front/{fila[11].strip()}",
                'gif_espalda': f"Pokemones/Back/{fila[12].strip()}" if len(fila) > 12 else ""
            }

def limpiar_ventana():
    global animacion_id
    if animacion_id:
        menu.after_cancel(animacion_id)
        animacion_id = None
    menu.unbind_all("<MouseWheel>")
    for widget in menu.winfo_children():
        widget.destroy()

def mostrar_menu():
    limpiar_ventana()

    frame_menu = tk.Frame(menu, width=1000, height=600, bg="gray20")
    frame_menu.pack(fill="both", expand=True)
    frame_menu.pack_propagate(False)

    lbl_titulo = tk.Label(frame_menu, text="BATALLA POKÉMON", font=("Arial", 28, "bold"), bg="gray20", fg="white")
    lbl_titulo.pack(pady=80)

    btn_jugar = tk.Button(frame_menu, text="Seleccionar Pokémon", font=("Arial", 14, "bold"), bg="Purple3", fg="white", padx=20, pady=10, command=mostrar_catalogo)
    btn_jugar.pack(pady=20)

def iniciar_batalla():
    if pokemon_actual:
        print(f"Iniciando batalla con: {pokemon_actual}")

def mostrar_catalogo():
    limpiar_ventana()

    def mover_scroll(event):
        if canvas.winfo_exists():
            if (event.x_root - menu.winfo_rootx()) < 704:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    Pokemons = tk.Frame(menu, width=704, height=600, bg="gray", highlightbackground="Purple3", highlightcolor="Purple3", highlightthickness=2)
    Pokemons.grid(row=0, column=0)
    Pokemons.grid_propagate(False)

    Seleccion = tk.Frame(menu, width=296, height=600, bg="gray35", highlightbackground="Purple3", highlightcolor="Purple3", highlightthickness=2)
    Seleccion.grid(row=0, column=1)
    Seleccion.pack_propagate(False)

    def animar_gif(lbl, frames, indice=0):
        global animacion_id
        if not lbl.winfo_exists():
            return
        lbl.config(image=frames[indice])
        siguiente = (indice + 1) % len(frames)
        animacion_id = menu.after(60, animar_gif, lbl, frames, siguiente)

    def seleccionar_pokemon(nombre):
        global pokemon_actual, animacion_id
        pokemon_actual = nombre
        datos = Catalogo_Pokemon[nombre]

        if animacion_id:
            menu.after_cancel(animacion_id)
            animacion_id = None

        for widget in Seleccion.winfo_children():
            widget.destroy()

        color_tema = COLORES_TIPO.get(datos["tipo"], "#F95587")

        lbl_nombre_sel = tk.Label(Seleccion, text=nombre.upper(), font=("Arial", 20, "bold"), bg="gray35", fg="white")
        lbl_nombre_sel.pack(pady=(20, 12))

        cuadro_gif = tk.Frame(Seleccion, width=165, height=165, bg="white", highlightbackground="black", highlightthickness=2)
        cuadro_gif.pack()
        cuadro_gif.pack_propagate(False)

        lbl_gif = tk.Label(cuadro_gif, bg="white")
        lbl_gif.pack(expand=True)

        lbl_tipo = tk.Label(Seleccion, text=datos["tipo"], font=("Arial", 11, "bold"), bg=color_tema, fg="white", width=16, pady=4)
        lbl_tipo.pack(pady=14)

        frame_stats = tk.Frame(Seleccion, bg="gray35")
        frame_stats.pack(pady=6)

        tk.Label(frame_stats, text=f"VIDA\n{datos['vida']}", font=("Arial", 11, "bold"), bg="gray35", fg="white", width=11).grid(row=0, column=0, pady=5)
        tk.Label(frame_stats, text=f"ATAQUE\n{datos['ataque']}", font=("Arial", 11, "bold"), bg="gray35", fg="white", width=11).grid(row=0, column=1, pady=5)
        tk.Label(frame_stats, text=f"DEFENSA\n{datos['defensa']}", font=("Arial", 11, "bold"), bg="gray35", fg="white", width=11).grid(row=1, column=0, pady=5)
        tk.Label(frame_stats, text=f"VELOCIDAD\n{datos['velocidad']}", font=("Arial", 11, "bold"), bg="gray35", fg="white", width=11).grid(row=1, column=1, pady=5)

        lbl_mov1 = tk.Label(Seleccion, text=f"{datos['move1'].upper()} - {datos['dmg1']}", font=("Arial", 11, "bold"), bg=color_tema, fg="white", width=23, pady=6)
        lbl_mov1.pack(pady=(14, 6))

        lbl_mov2 = tk.Label(Seleccion, text=f"{datos['move2'].upper()} - {datos['dmg2']}", font=("Arial", 11, "bold"), bg=color_tema, fg="white", width=23, pady=6)
        lbl_mov2.pack(pady=6)

        btn_seleccionar = tk.Button(Seleccion, text="SELECCIONAR", font=("Arial", 12, "bold"), bg="#1E90FF", fg="white", width=21, pady=5, relief="flat", cursor="hand2", command=iniciar_batalla)
        btn_seleccionar.pack(side="bottom", pady=20)

        gif_pil = Image.open(datos["gif_frente"])
        frames = []
        zoom = 1.8
        for frame in ImageSequence.Iterator(gif_pil):
            copia = frame.convert("RGBA")
            nuevo_ancho = min(int(copia.width * zoom), 155)
            nuevo_alto = min(int(copia.height * zoom), 155)
            copia = copia.resize((nuevo_ancho, nuevo_alto), Image.Resampling.NEAREST)
            frames.append(ImageTk.PhotoImage(copia))

        menu.frames_gif_actual = frames
        if len(frames) > 1:
            animar_gif(lbl_gif, frames, 0)
        else:
            lbl_gif.config(image=frames[0])

    barra_superior = tk.Frame(Pokemons, height=45, bg="gray25")
    barra_superior.pack(side="top", fill="x")
    barra_superior.pack_propagate(False)

    btn_regresar = tk.Button(barra_superior, text="Regresar al menú", bg="Purple3", fg="white", font=("Arial", 10, "bold"), relief="flat", cursor="hand2", command=mostrar_menu)
    btn_regresar.pack(side="left", padx=10, pady=8)

    lbl_instruccion = tk.Label(barra_superior, text="Selecciona un Pokémon", bg="gray25", fg="white", font=("Arial", 13, "bold"))
    lbl_instruccion.pack(side="left", padx=15)

    canvas = tk.Canvas(Pokemons, width=680, height=551, bg="gray", highlightthickness=0)
    scrollbar = tk.Scrollbar(Pokemons, orient="vertical", command=canvas.yview)
    frame_botones = tk.Frame(canvas, bg="gray")

    frame_botones.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame_botones, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    menu.bind_all("<MouseWheel>", mover_scroll)

    columnas = 4
    menu.iconos_cache = []

    for i, (nombre, datos) in enumerate(Catalogo_Pokemon.items()):
        fila = i // columnas
        columna = i % columnas

        img_raw = Image.open(datos['icono']).resize((95, 95), Image.Resampling.LANCZOS)
        icono_tk = ImageTk.PhotoImage(img_raw)
        menu.iconos_cache.append(icono_tk)

        btn = tk.Button(
            frame_botones,
            text=nombre,
            image=icono_tk,
            compound="top",
            font=("Arial", 10, "bold"),
            width=145,
            height=145,
            command=lambda n=nombre: seleccionar_pokemon(n)
        )
        btn.grid(row=fila, column=columna, padx=8, pady=10)

cargar_Pokemons()
mostrar_menu()
menu.mainloop()