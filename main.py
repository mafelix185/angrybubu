import asyncio
import flet as ft
import flet_audio as fta

def main(page: ft.Page):
    page.title = "Angry Bubu"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- RECURSOS VISUAIS ---
    IMG_FELIZ = "https://unsplash.com"
    IMG_BRAVO = "https://unsplash.com"

    # --- CONFIGURAÇÃO DE ÁUDIOS ---
    musica_fundo = fta.Audio(
        src="/barn-beat-01.mp3",
        volume=0.3,
        release_mode=fta.ReleaseMode.LOOP
    )
    
    som_latido = fta.Audio(
        src="/dog-bark-01.mp3",
        volume=1.0,
        release_mode=fta.ReleaseMode.STOP
    )
    
    vibração_sistema = ft.HapticFeedback()
    page.services.extend([musica_fundo, som_latido, vibração_sistema])

    # --- VARIÁVEIS DE ESTADO ---
    estado = {
        "nivel_estresse": 0.4,
        "pontuacao_atual": 0,
        "jogo_ativo": True,
        "recorde": 0
    }

    # Componentes estruturais do layout
    imagem_cachorro = ft.Image(src=IMG_FELIZ, width=250, height=250, fit="cover", border_radius=20)
    barra_estresse = ft.ProgressBar(value=estado["nivel_estresse"], width=300, color="red", bgcolor="green")
    lbl_status = ft.Text(value="O Bubu está feliz! Clique nele para acalmar! 🎵", size=15, weight=ft.FontWeight.BOLD, color="green")
    btn_reiniciar = ft.ElevatedButton(content=ft.Text("Jogar Novamente"), visible=False)

    lbl_pontos = ft.Text(value="Pontos: 0", size=18, weight=ft.FontWeight.BOLD, color="indigo")
    lbl_recorde = ft.Text(value="🏆 Recorde: 0", size=16, weight=ft.FontWeight.W_500, color="amber-700")
    placar_container = ft.Row([lbl_pontos, lbl_recorde], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300)

    # Lógica de clique na imagem
    def ao_clicar_no_pet(e):
        if not estado["jogo_ativo"]:
            return
        estado["nivel_estresse"] = max(0.0, estado["nivel_estresse"] - 0.20)
        barra_estresse.value = estado["nivel_estresse"]
        vibração_sistema.vibrate()
        
        if estado["nivel_estresse"] > 0.70:
            imagem_cachorro.src = IMG_BRAVO
            lbl_status.value = "🚨 COMPORTAMENTO AGRESSIVO! DIZ CORRENDO! 🤬"
            lbl_status.color = "red"
        else:
            imagem_cachorro.src = IMG_FELIZ
            lbl_status.value = "O Bubu está adorando o carinho! 😮‍💨"
            lbl_status.color = "orange"
        page.update()

    area_clicavel = ft.GestureDetector(
        content=imagem_cachorro,
        on_tap=ao_clicar_no_pet
    )

    # Loop assíncrono para gerenciar o tempo, pontuação e início das mídias
    async def loop_tempo():
        # Solução do Timeout: Pequena pausa assíncrona para garantir que a tela carregou por completo
        await asyncio.sleep(0.5)
        try:
            musica_fundo.play() # Toca a música de forma segura
        except Exception:
            pass # Previne falhas se o hardware de áudio demorar mais para responder

        while estado["jogo_ativo"]:
            await asyncio.sleep(0.8)
            
            if 0.0 < estado["nivel_estresse"] < 1.0:
                estado["nivel_estresse"] = min(1.0, estado["nivel_estresse"] + 0.08)
                barra_estresse.value = estado["nivel_estresse"]
                estado["pontuacao_atual"] += 10
                lbl_pontos.value = f"Pontos: {estado['pontuacao_atual']}"
                
                if estado["nivel_estresse"] > 0.70:
                    try:
                        som_latido.play()
                    except Exception:
                        pass
                    imagem_cachorro.src = IMG_BRAVO
                    lbl_status.value = "🚨 ELE ESTÁ FICANDO BRAVO! DIZ CORRENDO! 🤬"
                    lbl_status.color = "red"
                else:
                    imagem_cachorro.src = IMG_FELIZ
                    lbl_status.value = "O Bubu está feliz! 🎵"
                    lbl_status.color = "green"
                
                page.update()
            
            elif estado["nivel_estresse"] >= 1.0:
                estado["jogo_ativo"] = False
                imagem_cachorro.src = IMG_BRAVO
                try:
                    musica_fundo.pause()
                except Exception:
                    pass
                
                if estado["pontuacao_atual"] > estado["recorde"]:
                    estado["recorde"] = estado["pontuacao_atual"]
                    page.shared_preferences.set("recorde_pet", estado["recorde"])
                    lbl_status.value = f"🔥 NOVO RECORDE! Fez {estado['pontuacao_atual']} pontos! 🎉"
                    lbl_status.color = "green"
                else:
                    lbl_status.value = f"Game Over! O Bubu mordeu! Fez {estado['pontuacao_atual']} pontos. 🦮💥"
                    lbl_status.color = "red"
                
                btn_reiniciar.visible = True
                page.update()

    def inicializar_sistema():
        if not page.shared_preferences.contains_key("recorde_pet"):
            page.shared_preferences.set("recorde_pet", 0)
        
        estado["recorde"] = page.shared_preferences.get("recorde_pet")
        lbl_recorde.value = f"🏆 Recorde: {estado['recorde']}"
        
        # Desenha tudo na interface imediatamente (Evita tela branca)
        page.add(
            ft.Column([
                ft.Text("Angry Bubu - Game", size=24, weight=ft.FontWeight.BOLD, color="indigo"),
                ft.Divider(height=10, color="transparent"),
                placar_container,
                ft.Divider(height=10, color="transparent"),
                area_clicavel,
                ft.Divider(height=10, color="transparent"),
                barra_estresse,
                ft.Divider(height=10, color="transparent"),
                lbl_status,
                btn_reiniciar
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        # Dispara o controlador assíncrono em paralelo
        page.run_task(loop_tempo)

    def reiniciar_jogo(e):
        estado["nivel_estresse"] = 0.4
        estado["pontuacao_atual"] = 0
        estado["jogo_ativo"] = True
        
        barra_estresse.value = estado["nivel_estresse"]
        imagem_cachorro.src = IMG_FELIZ
        lbl_pontos.value = f"Pontos: {estado['pontuacao_atual']}"
        lbl_recorde.value = f"🏆 Recorde: {estado['recorde']}"
        lbl_status.value = "O Bubu está feliz! Clique nele para acalmar! 🎵"
        lbl_status.color = "green"
        btn_reiniciar.visible = False
        
        page.update()
        try:
            musica_fundo.play()
        except Exception:
            pass
        page.run_task(loop_tempo)

    btn_reiniciar.on_click = reiniciar_jogo
    inicializar_sistema()

ft.app(target=main)
            
