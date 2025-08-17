import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# função para listar os dispositivos de áudio disponiveis
def listar_dispositivos_de_audio():
    """Lista todos os dispositivos de entrada de áudio (microfones) disponíveis."""
    p = pyaudio.PyAudio()
    dispositivos_de_entrada = {}
    print("Dispositivos de áudio de ENTRADA disponíveis:")
    for i in range(p.get_device_count()):
        info_dispositivo = p.get_device_info_by_index(i)
        if info_dispositivo.get('maxInputChannels') > 0:
            dispositivos_de_entrada[i] = info_dispositivo['name']
            print(f"  [{i}] - {info_dispositivo['name']}")
    p.terminate()
    return dispositivos_de_entrada, pyaudio.PyAudio()

# lógica principal do programa
def iniciar_visualizador():
    """Inicia o processo de visualização de áudio."""
    dispositivos, objeto_audio = listar_dispositivos_de_audio()

    if not dispositivos:
        print("\nNenhum dispositivo de entrada encontrado. Verifique suas conexões de microfone.")
        return

    while True:
        try:
            escolha = int(input("\nDigite o número do dispositivo que deseja usar: "))
            if escolha in dispositivos:
                indice_dispositivo = escolha
                break
            else:
                print("Escolha inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

    # configurações do áudio
    FORMATO_AUDIO = pyaudio.paInt16
    CANAIS = 1
    TAXA_AMOSTRAGEM = 44100
    TAMANHO_CHUNK = 1024

    # abre o fluxo de áudio com o dispositivo escolhido
    try:
        fluxo = objeto_audio.open(format=FORMATO_AUDIO,
                                 channels=CANAIS,
                                 rate=TAXA_AMOSTRAGEM,
                                 input=True,
                                 input_device_index=indice_dispositivo,
                                 frames_per_buffer=TAMANHO_CHUNK)
        print(f"\nMicrofone '{dispositivos[indice_dispositivo]}' ativado. Fale ou faça um som para ver as ondas.")
    except Exception as e:
        print(f"Não foi possível abrir o fluxo de áudio. Erro: {e}")
        objeto_audio.terminate()
        return

    # configuração do Matplotlib para o gráfico
    figura = plt.figure(figsize=(10, 6)) # define o tamanho da janela
    eixo = figura.add_subplot(1, 1, 1)
    eixo.set_title("Visualização de Onda Sonora do Microfone", fontsize=16)
    eixo.set_xlabel("Amostras de Áudio")
    eixo.set_ylabel("Amplitude")
    eixo.set_ylim(-30000, 30000)
    eixo.grid(True) # adiciona uma grade ao gráfico
    
    # cria uma lista de dados inicial para a linha do gráfico
    eixo_x = np.arange(0, TAMANHO_CHUNK, 1)
    eixo_y = np.zeros(TAMANHO_CHUNK)
    
    # visual da linha
    linha_onda, = eixo.plot(eixo_x, eixo_y, color='cyan', linewidth=2) 

    # função de animação OTIMIZADA
    def animar(i):
        """Atualiza a linha do gráfico com os novos dados de áudio."""
        try:
            dados_brutos = fluxo.read(TAMANHO_CHUNK, exception_on_overflow=False)
            dados_numericos = np.frombuffer(dados_brutos, dtype=np.int16)
            
            # apenas atualiza os dados da linha, sem redesenhar o eixo
            linha_onda.set_ydata(dados_numericos) 
        except IOError as e:
            # em alguns sistemas, isso pode ocorrer. Apenas ignora.
            pass

        # 
        return linha_onda,

    # animação
    # `blit=True` melhora a performance de desenho em alguns sistemas.
    ani = animation.FuncAnimation(figura, animar, interval=10, blit=True) 

    plt.show()

    # encerrar fluxo de áudio
    fluxo.stop_stream()
    fluxo.close()
    objeto_audio.terminate()
    print("Fluxo de áudio encerrado.")

# função principal para iniciar o programa
if __name__ == "__main__":
    iniciar_visualizador()