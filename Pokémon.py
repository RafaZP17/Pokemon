import os
import csv
import random
import pygame
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageSequence, ImageTk, ImageDraw

ctk.set_appearance_mode("dark")

Catalogo_Pokemon = {}
pokemon_actual = None
animaciones = []
musica_actual = None
pygame.mixer.init()

COLORES_TIPO = {
    "ELECTRICO": "#F7D02C", "AGUA": "#6390F0", "FUEGO": "#EE8130",
    "PLANTA": "#7AC74C", "PSIQUICO": "#F95587", "SINIESTRO": "#705746",
    "FANTASMA": "#735797", "DRAGON": "#6F35FC", "LUCHA": "#C22E28",
    "BICHO": "#A6B91A",
}

MOVIMIENTOS_PRIORIDAD = {
    "ATAQUE RÁPIDO", "ACUA JET",
}

menu = ctk.CTk()
menu.title("Simulador Pokémon")
menu.geometry("1000x600")
menu.resizable(False, False)

# --- Cambiar icono de la ventana ---
ruta_icono = "Pokemones/icono.png"
if os.path.exists(ruta_icono):
    img_icono = Image.open(ruta_icono).convert("RGBA")

    mascara = Image.new("L", img_icono.size, 0)
    dibujo = ImageDraw.Draw(mascara)
    margen = 2
    dibujo.ellipse(
        (margen, margen, img_icono.width - margen, img_icono.height - margen),
        fill=255
    )
    img_icono.putalpha(mascara)

    icono_ventana = ImageTk.PhotoImage(img_icono)
    menu.after(200, lambda: menu.iconphoto(False, icono_ventana))


def reproducir_musica(ruta, volumen=0.4):
    global musica_actual
    if musica_actual != ruta and os.path.exists(ruta):
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1)
        musica_actual = ruta


def salir_juego():
    pygame.mixer.music.stop()
    menu.destroy()


def cargar_Pokemons():
    with open("pokemones_stats.csv", "r", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        next(lector)

        for fila in lector:
            if not fila:
                continue

            nombre = fila[0]
            tipo = fila[1].split("/")[0].split("-")[0].strip().upper()

            Catalogo_Pokemon[nombre] = {
                "tipo": tipo,
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
    reproducir_musica("Pokemones/Sonidos/menu.mp3")

    frame_menu = ctk.CTkFrame(menu, fg_color="#242424", corner_radius=0)
    frame_menu.pack(fill="both", expand=True)

    ruta_logo = "Pokemones/logo.png"
    if os.path.exists(ruta_logo):
        img_logo = Image.open(ruta_logo).convert("RGBA")

        bbox = img_logo.getbbox()
        if bbox:
            img_logo = img_logo.crop(bbox)

        # Escala del logo
        ancho_deseado = 420
        alto_proporcional = int(img_logo.height * (ancho_deseado / img_logo.width))
        img_logo = img_logo.resize((ancho_deseado, alto_proporcional), Image.Resampling.LANCZOS)

        logo_ctk = ctk.CTkImage(light_image=img_logo, dark_image=img_logo, size=(ancho_deseado, alto_proporcional))
        ctk.CTkLabel(frame_menu, image=logo_ctk, text="").pack(pady=(45, 30))
    else:
        ctk.CTkLabel(
            frame_menu,
            text="BATALLA POKÉMON",
            font=("Arial", 36, "bold")
        ).pack(pady=(110, 45))

    ctk.CTkButton(
        frame_menu,
        text="Jugar",
        font=("Arial", 18, "bold"),
        fg_color="#7D26CD",
        hover_color="#551A8B",
        width=260,
        height=55,
        command=mostrar_catalogo
    ).pack(pady=12)

    ctk.CTkButton(
        frame_menu,
        text="Historial de combates",
        font=("Arial", 18, "bold"),
        fg_color="#1E90FF",
        hover_color="#1874CD",
        width=260,
        height=55,
        command=mostrar_historial
    ).pack(pady=12)

    ctk.CTkButton(
        frame_menu,
        text="Salir",
        font=("Arial", 18, "bold"),
        fg_color="#C22E28",
        hover_color="#8B1E1A",
        width=260,
        height=55,
        command=salir_juego
    ).pack(pady=12)


def mostrar_historial():
    limpiar_ventana()

    barra = ctk.CTkFrame(menu, height=55, fg_color="#2B2B2B", corner_radius=0)
    barra.pack(fill="x")
    barra.pack_propagate(False)

    ctk.CTkButton(
        barra,
        text="Regresar",
        fg_color="#7D26CD",
        hover_color="#551A8B",
        width=110,
        command=mostrar_menu
    ).pack(side="left", padx=15, pady=12)

    ctk.CTkLabel(
        barra,
        text="HISTORIAL DE COMBATES",
        font=("Arial", 18, "bold")
    ).pack(side="left", padx=15)

    scroll = ctk.CTkScrollableFrame(menu, fg_color="#242424", corner_radius=0)
    scroll.pack(fill="both", expand=True, padx=20, pady=15)

    if not os.path.exists("historial_batallas.csv"):
        ctk.CTkLabel(
            scroll,
            text="Aún no hay combates registrados.",
            font=("Arial", 16)
        ).pack(pady=50)
        return

    with open("historial_batallas.csv", "r", encoding="utf-8", newline="") as archivo:
        lector = csv.reader(archivo)
        filas = [fila for fila in lector if len(fila) == 3]

    if filas and filas[0][0].lower() == "pokemon_jugador":
        filas = filas[1:]

    combates_validos = list(reversed(filas))

    if not combates_validos:
        ctk.CTkLabel(
            scroll,
            text="Aún no hay combates registrados.",
            font=("Arial", 16)
        ).pack(pady=50)
        return

    for nom_jugador, nom_rival, resultado in combates_validos:
        color_res = "#4CAF50" if resultado == "GANASTE" else "#E53935"

        tarjeta = ctk.CTkFrame(
            scroll,
            fg_color="#333333",
            corner_radius=12,
            border_width=2,
            border_color=color_res
        )
        tarjeta.pack(fill="x", pady=8, padx=10)

        # --- Pokémon del jugador ---
        frame_jug = ctk.CTkFrame(tarjeta, fg_color="transparent")
        frame_jug.pack(side="left", padx=30, pady=10)

        if nom_jugador in Catalogo_Pokemon:
            img_j = Image.open(Catalogo_Pokemon[nom_jugador]["icono"]).resize((80, 80), Image.Resampling.LANCZOS)
            ico_j = ctk.CTkImage(light_image=img_j, dark_image=img_j, size=(80, 80))
            ctk.CTkLabel(frame_jug, image=ico_j, text="").pack()

        ctk.CTkLabel(
            frame_jug,
            text=f"TÚ: {nom_jugador.upper()}",
            font=("Arial", 13, "bold")
        ).pack(pady=(4, 0))

        # --- Centro: VS y Resultado ---
        frame_centro = ctk.CTkFrame(tarjeta, fg_color="transparent")
        frame_centro.pack(side="left", expand=True)

        ctk.CTkLabel(
            frame_centro,
            text="VS",
            font=("Arial", 16, "bold"),
            text_color="#AAAAAA"
        ).pack()

        ctk.CTkLabel(
            frame_centro,
            text=resultado,
            font=("Arial", 18, "bold"),
            fg_color=color_res,
            text_color="white",
            corner_radius=8,
            width=150,
            height=36
        ).pack(pady=6)

        # --- Pokémon del rival ---
        frame_riv = ctk.CTkFrame(tarjeta, fg_color="transparent")
        frame_riv.pack(side="right", padx=30, pady=10)

        if nom_rival in Catalogo_Pokemon:
            img_r = Image.open(Catalogo_Pokemon[nom_rival]["icono"]).resize((80, 80), Image.Resampling.LANCZOS)
            ico_r = ctk.CTkImage(light_image=img_r, dark_image=img_r, size=(80, 80))
            ctk.CTkLabel(frame_riv, image=ico_r, text="").pack()

        ctk.CTkLabel(
            frame_riv,
            text=f"RIVAL: {nom_rival.upper()}",
            font=("Arial", 13, "bold")
        ).pack(pady=(4, 0))


def mostrar_catalogo():
    limpiar_ventana()
    reproducir_musica("Pokemones/Sonidos/menu.mp3")
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

        ctk.CTkLabel(panel_der, text=f"{datos['move1'].upper()} \n(Daño: {datos['dmg1']})", font=("Arial", 12, "bold"), fg_color=color, corner_radius=10, width=235, height=50).pack(pady=(12, 6))
        ctk.CTkLabel(panel_der, text=f"{datos['move2'].upper()} \n(Daño: {datos['dmg2']})", font=("Arial", 12, "bold"), fg_color=color, corner_radius=10, width=235, height=50).pack(pady=6)

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


def cargar_frames_tk(ruta_gif, zoom):
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
    pkm_jugador["vida_max"] = pkm_jugador["vida"]

    nombre_rival = random.choice(list(Catalogo_Pokemon))
    pkm_rival = Catalogo_Pokemon[nombre_rival].copy()
    pkm_rival["nombre"] = nombre_rival
    pkm_rival["vida_max"] = pkm_rival["vida"]

    escala = menu._get_window_scaling()
    ancho_real = int(1000 * escala)
    alto_real = int(600 * escala)

    escenario = tk.Canvas(menu, width=1000, height=600, highlightthickness=0)
    escenario.pack(fill="both", expand=True)

    reproducir_musica(f"Pokemones/Sonidos/batalla{random.randint(1, 3)}.mp3")

    fondo_img = Image.open(f"Pokemones/Fondo/Fondo{random.randint(1,5)}.png").resize((ancho_real, alto_real), Image.Resampling.NEAREST)
    fondo_tk = ImageTk.PhotoImage(fondo_img)
    escenario.create_image(0, 0, anchor="nw", image=fondo_tk)

    ruta_jugador = pkm_jugador["gif_espalda"] or pkm_jugador["gif_frente"]
    frames_jugador = cargar_frames_tk(ruta_jugador, zoom=4 * escala)
    frames_rival = cargar_frames_tk(pkm_rival["gif_frente"], zoom=2.8 * escala)

    sprite_jugador = escenario.create_image(int(250 * escala), int(340 * escala), image=frames_jugador[0])
    sprite_rival = escenario.create_image(int(760 * escala), int(150 * escala), image=frames_rival[0])

    pkm_jugador["sprite"] = sprite_jugador
    pkm_rival["sprite"] = sprite_rival

    escenario.imagenes = [fondo_tk, frames_jugador, frames_rival]

    def animar_sprite(item_id, frames, i=0):
        if escenario.winfo_exists() and item_id in escenario.find_all():
            escenario.itemconfig(item_id, image=frames[i])
            anim_id = menu.after(60, animar_sprite, item_id, frames, (i + 1) % len(frames))
            animaciones.append(anim_id)

    if len(frames_jugador) > 1:
        animar_sprite(sprite_jugador, frames_jugador)
    if len(frames_rival) > 1:
        animar_sprite(sprite_rival, frames_rival)

    # --- Botones de control (Nueva Batalla / Volver al Menú) ---
    ctk.CTkButton(
        menu,
        text="Nueva Batalla",
        font=("Arial", 12, "bold"),
        fg_color="#1E90FF",
        hover_color="#1874CD",
        width=130,
        height=32,
        command=iniciar_batalla
    ).place(x=710, y=15)

    ctk.CTkButton(
        menu,
        text="Volver al Menú",
        font=("Arial", 12, "bold"),
        fg_color="#C22E28",
        hover_color="#8B1E1A",
        width=130,
        height=32,
        command=mostrar_menu
    ).place(x=850, y=15)

    # --- Panel Rival ---
    panel_rival = ctk.CTkFrame(menu, width=350, height=112, fg_color="#2B2B2B", border_color="#7D26CD", border_width=2, corner_radius=12)
    panel_rival.place(x=125, y=20)
    panel_rival.pack_propagate(False)

    ctk.CTkLabel(panel_rival, text=pkm_rival["nombre"].upper(), font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(8, 4))

    barra_hp_rival = ctk.CTkProgressBar(panel_rival, width=265, height=16, progress_color="#4CAF50", fg_color="#555555")
    barra_hp_rival.set(1.0)
    barra_hp_rival.pack(padx=15, pady=2)

    fila_stats_rival = ctk.CTkFrame(panel_rival, fg_color="transparent")
    fila_stats_rival.pack(fill="x", padx=15, pady=(4, 6))

    lbl_stats_rival = ctk.CTkLabel(fila_stats_rival, text=f"ATQ: {pkm_rival['ataque']}  |  DEF: {pkm_rival['defensa']}", font=("Arial", 11, "bold"), text_color="#AAAAAA")
    lbl_stats_rival.pack(side="left")

    lbl_hp_rival = ctk.CTkLabel(fila_stats_rival, text=f"HP: {pkm_rival['vida']} / {pkm_rival['vida_max']}", font=("Arial", 12, "bold"), text_color="#CCCCCC")
    lbl_hp_rival.pack(side="right")

    # --- Panel Jugador ---
    panel_jugador = ctk.CTkFrame(menu, width=350, height=112, fg_color="#2B2B2B", border_color="#1E90FF", border_width=2, corner_radius=12)
    panel_jugador.place(x=520, y=310)
    panel_jugador.pack_propagate(False)

    ctk.CTkLabel(panel_jugador, text=pkm_jugador["nombre"].upper(), font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(8, 4))

    barra_hp_jugador = ctk.CTkProgressBar(panel_jugador, width=265, height=16, progress_color="#4CAF50", fg_color="#555555")
    barra_hp_jugador.set(1.0)
    barra_hp_jugador.pack(padx=15, pady=2)

    fila_stats_jugador = ctk.CTkFrame(panel_jugador, fg_color="transparent")
    fila_stats_jugador.pack(fill="x", padx=15, pady=(4, 6))

    lbl_stats_jugador = ctk.CTkLabel(fila_stats_jugador, text=f"ATQ: {pkm_jugador['ataque']}  |  DEF: {pkm_jugador['defensa']}", font=("Arial", 11, "bold"), text_color="#AAAAAA")
    lbl_stats_jugador.pack(side="left")

    lbl_hp_jugador = ctk.CTkLabel(fila_stats_jugador, text=f"HP: {pkm_jugador['vida']} / {pkm_jugador['vida_max']}", font=("Arial", 12, "bold"), text_color="#CCCCCC")
    lbl_hp_jugador.pack(side="right")

    # --- Panel Inferior ---
    panel_inferior = ctk.CTkFrame(menu, width=1000, height=172, fg_color="#1E1E1E", border_color="#7D26CD", border_width=2, corner_radius=0)
    panel_inferior.place(x=0, y=430)
    panel_inferior.pack_propagate(False)

    caja_texto = ctk.CTkFrame(panel_inferior, width=490, height=145, fg_color="#2B2B2B", border_color="#444444", border_width=2, corner_radius=10)
    caja_texto.place(x=15, y=15)
    caja_texto.pack_propagate(False)

    lbl_mensaje = ctk.CTkLabel(
        caja_texto,
        text=f"¿Qué debería hacer {pkm_jugador['nombre'].upper()}?",
        font=("Arial", 15, "bold"),
        justify="left",
        wraplength=455
    )
    lbl_mensaje.pack(anchor="nw", padx=18, pady=18)

    caja_botones = ctk.CTkFrame(panel_inferior, width=465, height=145, fg_color="transparent")
    caja_botones.place(x=520, y=15)
    caja_botones.grid_propagate(False)

    def guardar_resultado(resultado):
        archivo_existe = os.path.exists("historial_batallas.csv")
        with open("historial_batallas.csv", "a", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            if not archivo_existe:
                escritor.writerow(["pokemon_jugador", "pokemon_rival", "resultado"])
            escritor.writerow([pkm_jugador["nombre"], pkm_rival["nombre"], resultado])

    def actualizar_hud():
        barra_hp_jugador.set(pkm_jugador["vida"] / pkm_jugador["vida_max"])
        lbl_hp_jugador.configure(text=f"HP: {pkm_jugador['vida']} / {pkm_jugador['vida_max']}")
        lbl_stats_jugador.configure(text=f"ATQ: {pkm_jugador['ataque']}  |  DEF: {pkm_jugador['defensa']}")

        barra_hp_rival.set(pkm_rival["vida"] / pkm_rival["vida_max"])
        lbl_hp_rival.configure(text=f"HP: {pkm_rival['vida']} / {pkm_rival['vida_max']}")
        lbl_stats_rival.configure(text=f"ATQ: {pkm_rival['ataque']}  |  DEF: {pkm_rival['defensa']}")

    def obtener_prioridad(pkm, accion):
        if accion == "move1" and pkm["move1"].strip().upper() in MOVIMIENTOS_PRIORIDAD:
            return 1
        if accion == "move2" and pkm["move2"].strip().upper() in MOVIMIENTOS_PRIORIDAD:
            return 1
        return 0

    def ejecutar_accion(atacante, defensor, accion):
        if accion == "move1":
            dano = max(1, atacante["dmg1"] + atacante["ataque"] - defensor["defensa"])
            defensor["vida"] = max(0, defensor["vida"] - dano)
            return f"¡{atacante['nombre']} usó {atacante['move1']} e hizo {dano} de daño!"
        elif accion == "move2":
            dano = max(1, atacante["dmg2"] + atacante["ataque"] - defensor["defensa"])
            defensor["vida"] = max(0, defensor["vida"] - dano)
            return f"¡{atacante['nombre']} usó {atacante['move2']} e hizo {dano} de daño!"
        elif accion == "curar":
            atacante["vida"] = min(atacante["vida_max"], atacante["vida"] + 20)
            return f"¡{atacante['nombre']} recuperó 20 HP!"
        elif accion == "bajar_def":
            defensor["defensa"] = max(0, defensor["defensa"] - 4)
            return f"¡{atacante['nombre']} bajó 4 puntos la defensa de {defensor['nombre']}!"

    def turno_batalla(accion_jugador):
        accion_rival = random.choice(["move1", "move2", "bajar_def"])
        if pkm_rival["vida"] < 30 and random.randint(1, 5) > 2:
            accion_rival = "curar"

        prio_j = obtener_prioridad(pkm_jugador, accion_jugador)
        prio_r = obtener_prioridad(pkm_rival, accion_rival)

        if prio_j != prio_r:
            jugador_primero = prio_j > prio_r
        elif pkm_jugador["velocidad"] != pkm_rival["velocidad"]:
            jugador_primero = pkm_jugador["velocidad"] > pkm_rival["velocidad"]
        else:
            jugador_primero = random.choice([True, False])

        if jugador_primero:
            orden = [
                (pkm_jugador, pkm_rival, accion_jugador),
                (pkm_rival, pkm_jugador, accion_rival)
            ]
        else:
            orden = [
                (pkm_rival, pkm_jugador, accion_rival),
                (pkm_jugador, pkm_rival, accion_jugador)
            ]

        mensajes = []

        for atacante, defensor, accion in orden:
            texto = ejecutar_accion(atacante, defensor, accion)
            mensajes.append(texto)
            actualizar_hud()

            if defensor["vida"] == 0:
                escenario.delete(defensor["sprite"])
                mensajes.append(f"¡{defensor['nombre']} se debilitó! ¡{atacante['nombre']} gana!")
                lbl_mensaje.configure(text="\n".join(mensajes))

                resultado = "GANASTE" if atacante == pkm_jugador else "PERDISTE"
                guardar_resultado(resultado)

                for b in (btn_move1, btn_move2, btn_bajar_def, btn_curar):
                    b.configure(state="disabled")
                return

        lbl_mensaje.configure(text="\n".join(mensajes))

    color_tipo = COLORES_TIPO.get(pkm_jugador["tipo"], "#1E90FF")

    btn_move1 = ctk.CTkButton(
        caja_botones,
        text=f"{pkm_jugador['move1'].upper()}\n(Daño: {pkm_jugador['dmg1']})",
        font=("Arial", 13, "bold"),
        fg_color=color_tipo,
        width=225,
        height=65,
        corner_radius=10,
        command=lambda: turno_batalla("move1")
    )
    btn_move1.grid(row=0, column=0, padx=(0, 7), pady=(0, 7))

    btn_move2 = ctk.CTkButton(
        caja_botones,
        text=f"{pkm_jugador['move2'].upper()}\n(Daño: {pkm_jugador['dmg2']})",
        font=("Arial", 13, "bold"),
        fg_color=color_tipo,
        width=225,
        height=65,
        corner_radius=10,
        command=lambda: turno_batalla("move2")
    )
    btn_move2.grid(row=0, column=1, padx=(7, 0), pady=(0, 7))

    btn_bajar_def = ctk.CTkButton(
        caja_botones,
        text="GRITO / BAJAR DEFENSA\n(-4 DEF Rival)",
        font=("Arial", 13, "bold"),
        fg_color="#D97706",
        hover_color="#B45309",
        width=225,
        height=65,
        corner_radius=10,
        command=lambda: turno_batalla("bajar_def")
    )
    btn_bajar_def.grid(row=1, column=0, padx=(0, 7), pady=(7, 0))

    btn_curar = ctk.CTkButton(
        caja_botones,
        text="RECUPERACIÓN\n(+20 HP)",
        font=("Arial", 13, "bold"),
        fg_color="#2E8B57",
        hover_color="#226B42",
        width=225,
        height=65,
        corner_radius=10,
        command=lambda: turno_batalla("curar")
    )
    btn_curar.grid(row=1, column=1, padx=(7, 0), pady=(7, 0))


cargar_Pokemons()
mostrar_menu()
menu.mainloop()