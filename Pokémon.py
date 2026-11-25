import csv
import random
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageSequence, ImageTk

ctk.set_appearance_mode("dark")

Catalogo_Pokemon = {}
pokemon_actual = None
animaciones = []

COLORES_TIPO = {
    "ELECTRICO": "#F7D02C", "AGUA": "#6390F0", "FUEGO": "#EE8130",
    "PLANTA": "#7AC74C", "PSIQUICO": "#F95587", "SINIESTRO": "#705746",
    "FANTASMA": "#735797", "DRAGON": "#6F35FC", "LUCHA": "#C22E28",
    "BICHO": "#A6B91A", "NORMAL": "#A8A77A", "HIELO": "#96D9D6",
    "TIERRA": "#E2BF65", "ROCA": "#B6A136", "ACERO": "#B7B7CE",
    "HADA": "#D685AD", "VENENO": "#A33EA1", "VOLADOR": "#A98FF3"
}

menu = ctk.CTk()
menu.title("Simulador Pokémon")
menu.geometry("1000x600")
menu.resizable(False, False)


def cargar_Pokemons():
    with open("pokemones_stats.csv", "r", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        next(lector)

        for fila in lector:
            if not fila:
                continue

            nombre = fila[0]
            Catalogo_Pokemon[nombre] = {
                "tipo": fila[1].strip().upper(),
                "vida": int(fila[2]),
                "ataque": int(fila[3]),
                "defensa": int(fila[4]),
                "velocidad": int(fila[5]),
                "move1": fila[6],
                "dmg1": int(fila[7]),
                "move2": fila[8],
                "dmg2": int(fila[9]),
                "icono": f"Pokemones/Icon/{fila[10].strip()}",
                "gif_frente": f"Pokemones/Front/{fila[11].strip()}",
                "gif_espalda": f"Pokemones/Back/{fila[12].strip()}" if len(fila) > 12 else ""
            }


def limpiar_ventana():
    for anim_id in animaciones:
        menu.after_cancel(anim_id)
    animaciones.clear()
    for widget in menu.winfo_children():
        widget.destroy()


def mostrar_menu():
    limpiar_ventana()

    frame_menu = ctk.CTkFrame(menu, fg_color="#242424", corner_radius=0)
    frame_menu.pack(fill="both", expand=True)

    ctk.CTkLabel(frame_menu, text="BATALLA POKÉMON", font=("Arial", 32, "bold")).pack(pady=(140, 40))

    ctk.CTkButton(
        frame_menu,
        text="Seleccionar Pokémon",
        font=("Arial", 16, "bold"),
        fg_color="#7D26CD",
        hover_color="#551A8B",
        width=240,
        height=50,
        command=mostrar_catalogo
    ).pack()


def mostrar_catalogo():
    limpiar_ventana()
    botones = {}

    panel_izq = ctk.CTkFrame(menu, width=704, height=600, fg_color="#555555", corner_radius=0)
    panel_izq.grid(row=0, column=0)
    panel_izq.pack_propagate(False)

    panel_der = ctk.CTkFrame(menu, width=296, height=600, fg_color="#3A3A3A", corner_radius=0)
    panel_der.grid(row=0, column=1)
    panel_der.pack_propagate(False)

    barra = ctk.CTkFrame(panel_izq, height=48, fg_color="#2B2B2B", corner_radius=0)
    barra.pack(fill="x")
    barra.pack_propagate(False)

    ctk.CTkButton(barra, text="Regresar", fg_color="#7D26CD", hover_color="#551A8B", width=100, command=mostrar_menu).pack(side="left", padx=10, pady=10)
    ctk.CTkLabel(barra, text="Selecciona un Pokémon", font=("Arial", 14, "bold")).pack(side="left", padx=10)

    scroll = ctk.CTkScrollableFrame(panel_izq, fg_color="#555555", corner_radius=0)
    scroll.pack(fill="both", expand=True)

    def animar_gif(lbl, frames, i=0):
        if lbl.winfo_exists():
            lbl.configure(image=frames[i])
            anim_id = menu.after(60, animar_gif, lbl, frames, (i + 1) % len(frames))
            animaciones.append(anim_id)

    def seleccionar_pokemon(nombre):
        global pokemon_actual
        pokemon_actual = nombre
        datos = Catalogo_Pokemon[nombre]

        for nom, btn in botones.items():
            if nom == nombre:
                btn.configure(border_color="#1E90FF", border_width=4)
            else:
                btn.configure(border_color="#333333", border_width=2)

        for anim_id in animaciones:
            menu.after_cancel(anim_id)
        animaciones.clear()

        for w in panel_der.winfo_children():
            w.destroy()

        color = COLORES_TIPO.get(datos["tipo"], "#F95587")

        ctk.CTkLabel(panel_der, text=nombre.upper(), font=("Arial", 22, "bold")).pack(pady=(20, 12))

        cuadro_gif = ctk.CTkFrame(panel_der, width=165, height=165, fg_color="white", corner_radius=15)
        cuadro_gif.pack()
        cuadro_gif.pack_propagate(False)

        lbl_gif = ctk.CTkLabel(cuadro_gif, text="")
        lbl_gif.pack(expand=True)

        ctk.CTkLabel(panel_der, text=datos["tipo"], font=("Arial", 12, "bold"), fg_color=color, corner_radius=10, width=150, height=30).pack(pady=14)

        stats = ctk.CTkFrame(panel_der, fg_color="transparent")
        stats.pack(pady=6)
        ctk.CTkLabel(stats, text=f"VIDA\n{datos['vida']}", font=("Arial", 12, "bold"), width=110).grid(row=0, column=0, pady=6)
        ctk.CTkLabel(stats, text=f"ATAQUE\n{datos['ataque']}", font=("Arial", 12, "bold"), width=110).grid(row=0, column=1, pady=6)
        ctk.CTkLabel(stats, text=f"DEFENSA\n{datos['defensa']}", font=("Arial", 12, "bold"), width=110).grid(row=1, column=0, pady=6)
        ctk.CTkLabel(stats, text=f"VELOCIDAD\n{datos['velocidad']}", font=("Arial", 12, "bold"), width=110).grid(row=1, column=1, pady=6)

        ctk.CTkLabel(panel_der, text=f"{datos['move1'].upper()} - {datos['dmg1']}", font=("Arial", 12, "bold"), fg_color=color, corner_radius=10, width=235, height=34).pack(pady=(12, 6))
        ctk.CTkLabel(panel_der, text=f"{datos['move2'].upper()} - {datos['dmg2']}", font=("Arial", 12, "bold"), fg_color=color, corner_radius=10, width=235, height=34).pack(pady=6)

        ctk.CTkButton(panel_der, text="SELECCIONAR", font=("Arial", 13, "bold"), fg_color="#1E90FF", hover_color="#1874CD", width=235, height=40, command=iniciar_batalla).pack(side="bottom", pady=20)

        gif = Image.open(datos["gif_frente"])
        frames = []
        for frame in ImageSequence.Iterator(gif):
            img = frame.convert("RGBA")
            ancho = min(int(img.width * 1.8), 150)
            alto = min(int(img.height * 1.8), 150)
            img = img.resize((ancho, alto), Image.Resampling.NEAREST)
            frames.append(ctk.CTkImage(light_image=img, dark_image=img, size=(ancho, alto)))

        if len(frames) > 1:
            animar_gif(lbl_gif, frames)
        else:
            lbl_gif.configure(image=frames[0])

    for i, (nombre, datos) in enumerate(Catalogo_Pokemon.items()):
        img = Image.open(datos["icono"]).resize((110, 110), Image.Resampling.LANCZOS)
        icono = ctk.CTkImage(light_image=img, dark_image=img, size=(110, 110))

        btn = ctk.CTkButton(
            scroll,
            text=nombre,
            image=icono,
            compound="top",
            font=("Arial", 12, "bold"),
            fg_color="white",
            hover_color="#E0E0E0",
            text_color="black",
            border_color="#333333",
            border_width=2,
            width=155,
            height=155,
            command=lambda n=nombre: seleccionar_pokemon(n)
        )
        btn.grid(row=i // 4, column=i % 4, padx=9, pady=10)
        botones[nombre] = btn


def cargar_frames_tk(ruta_gif, zoom=2.4):
    gif = Image.open(ruta_gif)
    frames = []
    for frame in ImageSequence.Iterator(gif):
        img = frame.convert("RGBA")
        ancho = int(img.width * zoom)
        alto = int(img.height * zoom)
        img = img.resize((ancho, alto), Image.Resampling.NEAREST)
        frames.append(ImageTk.PhotoImage(img))
    return frames


def iniciar_batalla():
    limpiar_ventana()

    pkm_jugador = Catalogo_Pokemon[pokemon_actual].copy()
    pkm_jugador["nombre"] = pokemon_actual

    nombre_rival = random.choice(list(Catalogo_Pokemon))
    pkm_rival = Catalogo_Pokemon[nombre_rival].copy()
    pkm_rival["nombre"] = nombre_rival

    escala = menu._get_window_scaling()
    ancho_real = int(1000 * escala)
    alto_real = int(600 * escala)

    escenario = tk.Canvas(menu, width=1000, height=600, highlightthickness=0)
    escenario.pack(fill="both", expand=True)

    fondo_img = Image.open("Pokemones/Fondo/Grass.png").resize((ancho_real, alto_real), Image.Resampling.NEAREST)
    fondo_tk = ImageTk.PhotoImage(fondo_img)
    escenario.create_image(0, 0, anchor="nw", image=fondo_tk)

    ruta_jugador = pkm_jugador["gif_espalda"] or pkm_jugador["gif_frente"]
    frames_jugador = cargar_frames_tk(ruta_jugador, zoom=4 * escala)
    frames_rival = cargar_frames_tk(pkm_rival["gif_frente"], zoom=2.2 * escala)

    sprite_jugador = escenario.create_image(int(230 * escala), int(340 * escala), image=frames_jugador[0])
    sprite_rival = escenario.create_image(int(720 * escala), int(210 * escala), image=frames_rival[0])

    escenario.imagenes = [fondo_tk, frames_jugador, frames_rival]

    def animar_sprite(item_id, frames, i=0):
        if escenario.winfo_exists():
            escenario.itemconfig(item_id, image=frames[i])
            anim_id = menu.after(60, animar_sprite, item_id, frames, (i + 1) % len(frames))
            animaciones.append(anim_id)

    if len(frames_jugador) > 1:
        animar_sprite(sprite_jugador, frames_jugador)
    if len(frames_rival) > 1:
        animar_sprite(sprite_rival, frames_rival)

    ctk.CTkButton(
        menu,
        text="Cambiar Pokémon",
        font=("Arial", 12, "bold"),
        fg_color="#C22E28",
        hover_color="#8B1E1A",
        width=150,
        height=35,
        command=mostrar_catalogo
    ).place(x=20, y=20)


cargar_Pokemons()
mostrar_menu()
menu.mainloop()