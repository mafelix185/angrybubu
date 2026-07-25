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

    # --- CONFIGURAÇÃO DE ÁUDIOS E HARDWARE ---
    musica_fundo = fta.Audio(
        src="https://soundjay.com",
        volume=0.3,
        release_mode=fta.ReleaseMode.LOOP
    )
    
    som_latido = fta.Audio(
        src="https://soundjay.com",
        volume=1.0,
        release_mode=fta.ReleaseMode.STOP
    )
    
    vibração_sistema = ft.HapticFeedback()
    page.overlay.extend([musica_fundo, som_latido, vibração_sistema])

    # --- VARIÁVEIS DE ESTADO ---
    nivel_estresse = 0.4
    pontuacao_atual = 0
    jogo_ativo = True

    # Configuração de persistência local estável (shared_preferences)
    if not page.shared_preferences.contains_key("recorde_pet"):
        page.shared_preferences.set("recorde_pet", 0)
    
    recorde = page.shared_preferences.get("recorde_pet")

    # =========================================================================
    # 🖼️ CORREÇÃO DA IMAGEM (fit="cover")
    # =========================================================================
    # Passamos apenas a string "cover" diretamente no atributo 'fit'
    imagem_cachorro = ft.Image(
        src=IMG_FELIZ, 
        width=250, 
        height=250, 
        fit="cover", 
        border_radius=20
    )
    
    barra_estresse = ft.ProgressBar(value=nivel_estresse, width=300, color="red", bgcolor="green")
    lbl_status = ft.Text(value="O Bubu está feliz! Ouça a música e cuide dele. 🎵", size=15, weight=ft.FontWeight.BOLD, color="green")
    btn_reiniciar = ft.ElevatedButton(text="Jogar Novamente", visible=False)

    lbl_pontos = ft.Text(value=f"Pontos: {pontuacao_atual}", size=18, weight=ft.FontWeight.BOLD, color="indigo")
    lbl_recorde = ft.Text(value=f"🏆 Recorde: {recorde}", size=16, weight=ft.FontWeight.W_500, color="amber-700")
    placar_container = ft.Row([lbl_pontos, lbl_recorde], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300)

    # Inicia a trilha sonora
    musica_fundo.play()

    def atualizar_humor_visual():
        if nivel_estresse > 0.70:
            imagem_cachorro.src = IMG_BRAVO
            lbl_status.value = "🚨 COMPORTAMENTO AGRESSIVO! CHACOALHE! 🤬"
            lbl_status.color = "red"
        elif 0.0 < nivel_estresse <= 0.70:
            imagem_cachorro.src = IMG_FELIZ
            lbl_status.value = "O Bubu está se acalmando com o balanço... 😮‍💨"
            lbl_status.color = "orange"
        elif nivel_estresse == 0.0:
            imagem_cachorro.src = IMG_FELIZ
            lbl_status.value = "Parabéns! O Bubu dormiu relaxado! 💤"
            lbl_status.color = "green"

    def ao_chacoalhar():
        nonlocal nivel_estresse
        if not jogo_ativo:
            return
        nivel_estresse = max(0.0, nivel_estresse - 0.20)
        barra_estresse.value = nivel_estresse
        vibração_sistema.vibrate()
        atualizar_humor_visual()
        page.update()

    sensor_movimento = ft.ShakeDetector(on_shake=ao_chacoalhar)
    page.overlay.append(sensor_movimento)

    async def loop_tempo():
        nonlocal nivel_estresse, jogo_ativo, pontuacao_atual, recorde
        while jogo_active := jogo_ativo:
            await asyncio.sleep(0.8)
            
            if 0.0 < nivel_estresse < 1.0:
                nivel_estresse = min(1.0, nivel_estresse + 0.08)
                barra_estresse.value = nivel_estresse
                pontuacao_atual += 10
                lbl_pontos.value = f"Pontos: {pontuacao_atual}"
                
                if nivel_estresse > 0.70:
                    som_latido.play()
                
                atualizar_humor_visual()
                page.update()
            
            elif nivel_estresse >= 1.0:
                jogo_ativo = False
                imagem_cachorro.src = IMG_BRAVO
                musica_fundo.pause()
                
                if pontuacao_atual > recorde:
                    recorde = pontuacao_atual
                    page.shared_preferences.set("recorde_pet", recorde)
                    lbl_status.value = f"🔥 NOVO RECORDE! Você fez {pontuacao_atual} pontos! 🎉"
                    lbl_status.color = "green"
                else:
                    lbl_status.value = f"Game Over! O Bubu mordeu! Fez {pontuacao_atual} pontos. 🦮💥"
                    lbl_status.color = "red"
                
                btn_reiniciar.visible = True
                page.update()

    def reiniciar_jogo(e):
        nonlocal nivel_estresse, jogo_ativo, pontuacao_atual
        nivel_estresse = 0.4
        pontuacao_atual = 0
        jogo_ativo = True
        
        barra_estresse.value = nivel_estresse
        imagem_cachorro.src = IMG_FELIZ
        lbl_pontos.value = f"Pontos: {pontuacao_atual}"
        lbl_recorde.value = f"🏆 Recorde: {recorde}"
        lbl_status.value = "O Bubu está feliz! Ouça a música e cuide dele. 🎵"
        lbl_status.color = "green"
        btn_reiniciar.visible = False
        
        page.update()
        musica_fundo.play()
        page.run_task(loop_tempo)

    btn_reiniciar.on_click = reiniciar_jogo

    page.add(
        ft.Column([
            ft.Text("Angry Bubu - Game", size=24, weight=ft.FontWeight.BOLD, color="indigo"),
            ft.Divider(height=10, color="transparent"),
            placar_container,
            ft.Divider(height=10, color="transparent"),
            imagem_cachorro,
            ft.Divider(height=10, color="transparent"),
            barra_estresse,
            ft.Divider(height=10, color="transparent"),
            lbl_status,
            btn_reiniciar
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    
    page.run_task(loop_tempo)

ft.app(target=main)
