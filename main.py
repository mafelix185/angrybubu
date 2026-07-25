import asyncio
import flet as ft
import flet_audio as fta

# Recorde global armazenado na memória RAM do aplicativo
RECORDE_GLOBAL = 0

def main(page: ft.Page):
    global RECORDE_GLOBAL
    page.title = "Angry Bubu"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

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
        "jogo_ativo": True
    }

    # =========================================================================
    # 🐕 SUBSTITUIÇÃO DA IMAGEM POR ICONE EM TEXTO (Sem falhas de download)
    # =========================================================================
    # Usamos um texto gigante com emojis. Abre em qualquer smartphone sem usar internet
    lbl_emoji_pet = ft.Text(value="🐶", size=120)
    
    barra_estresse = ft.ProgressBar(value=estado["nivel_estresse"], width=300, color="red", bgcolor="green")
    lbl_status = ft.Text(value="O Bubu está feliz! Clique nele para acalmar! 🎵", size=15, weight=ft.FontWeight.BOLD, color="green")
    btn_reiniciar = ft.ElevatedButton(content=ft.Text("Jogar Novamente"), visible=False)

    lbl_pontos = ft.Text(value="Pontos: 0", size=18, weight=ft.FontWeight.BOLD, color="indigo")
    lbl_recorde = ft.Text(value=f"🏆 Recorde: {RECORDE_GLOBAL}", size=16, weight=ft.FontWeight.W_500, color="amber-700")
    placar_container = ft.Row([lbl_pontos, lbl_recorde], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300)

    # Lógica de clique no emoji para acalmar o pet
    def ao_clicar_no_pet(e):
        if not estado["jogo_ativo"]:
            return
        estado["nivel_estresse"] = max(0.0, estado["nivel_estresse"] - 0.20)
        barra_estresse.value = estado["nivel_estresse"]
        
        try:
            vibração_sistema.vibrate()
        except Exception:
            pass
            
        if estado["nivel_estresse"] > 0.70:
            lbl_emoji_pet.value = "🤬"
            lbl_status.value = "🚨 COMPORTAMENTO AGRESSIVO! CLIQUE RÁPIDO! 🤬"
            lbl_status.color = "red"
        else:
            lbl_emoji_pet.value = "🐶"
            lbl_status.value = "O Bubu está adorando o carinho! 😮‍💨"
            lbl_status.color = "orange"
        page.update()

    # Envolve o texto do emoji em uma área clicável estável
    area_clicavel = ft.GestureDetector(
        content=lbl_emoji_pet,
        on_tap=ao_clicar_no_pet
    )

    # Loop contínuo que roda em background controlando o tempo
    async def loop_tempo():
        global RECORDE_GLOBAL
        await asyncio.sleep(0.5)
        try:
            musica_fundo.play()
        except Exception:
            pass

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
                    lbl_emoji_pet.value = "🤬"
                    lbl_status.value = "🚨 ELE ESTÁ FICANDO BRAVO! CLIQUE RÁPIDO! 🤬"
                    lbl_status.color = "red"
                else:
                    lbl_emoji_pet.value = "🐶"
                    lbl_status.value = "O Bubu está feliz! 🎵"
                    lbl_status.color = "green"
                
                page.update()
            
            elif estado["nivel_estresse"] >= 1.0:
                estado["jogo_ativo"] = False
                lbl_emoji_pet.value = "🦁" # Vira um leão bravo de game over
                try:
                    musica_fundo.pause()
                except Exception:
                    pass
                
                if estado["pontuacao_atual"] > RECORDE_GLOBAL:
                    RECORDE_GLOBAL = estado["pontuacao_atual"]
                    lbl_recorde.value = f"🏆 Recorde: {RECORDE_GLOBAL}"
                    lbl_status.value = f"🔥 NOVO RECORDE! Fez {estado['pontuacao_atual']} pontos! 🎉"
                    lbl_status.color = "green"
                else:
                    lbl_status.value = f"Game Over! O Bubu mordeu! Fez {estado['pontuacao_atual']} pontos. 🦮💥"
                    lbl_status.color = "red"
                
                btn_reiniciar.visible = True
                page.update()

    def reiniciar_jogo(e):
        estado["nivel_estresse"] = 0.4
        estado["pontuacao_atual"] = 0
        estado["jogo_ativo"] = True
        
        barra_estresse.value = estado["nivel_estresse"]
        lbl_emoji_pet.value = "🐶"
        lbl_pontos.value = f"Pontos: {estado['pontuacao_atual']}"
        lbl_recorde.value = f"🏆 Recorde: {RECORDE_GLOBAL}"
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

    # Desenha os componentes na interface
    page.add(
        ft.Column([
            ft.Text("Angry Bubu - Game", size=24, weight=ft.FontWeight.BOLD, color="indigo"),
            ft.Divider(height=10, color="transparent"),
            placar_container,
            ft.Divider(height=20, color="transparent"),
            area_clicavel, # Área clicável contendo o Emoji Gigante
            ft.Divider(height=20, color="transparent"),
            barra_estresse,
            ft.Divider(height=10, color="transparent"),
            lbl_status,
            btn_reiniciar
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    
    # Dispara o loop do game
    page.run_task(loop_tempo)

ft.app(target=main)
