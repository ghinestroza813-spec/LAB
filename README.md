# TikTok Fight Arena — MVP 0.4

Protótipo local de jogo de luta para lives. Os eventos ainda são **simulados por teclado**; a conexão real com o TikTok não foi implementada.

## Controles

Dois lutadores: **Lado A** (vermelho, esquerda) e **Lado B** (azul, direita). Cada tecla faz o lado indicado atacar o outro.

|Lado A|Lado B|Golpe|Dano|
|:-:|:-:|-|:-:|
|`1`|`6`|Soco rápido (reação simulada)|5|
|`2`|`7`|Chute (reação simulada)|9|
|`3`|`8`|Especial (presente Rosa simulado)|16|
|`4`|`9`|Supergolpe (presente raro simulado)|30|
|`A`|`L`|Golpe manual de teste (soco)|5|

Outras teclas:

|Tecla|Ação|
|:-:|-|
|`TAB`|Mostra/esconde a história dos dois lutadores|
|`F1` / `F2`|Troca o personagem do Lado A / Lado B (reinicia a rodada)|
|`F3`|Troca o cenário (por padrão vale o cenário do Lado A)|
|`R`|Reinicia a rodada|
|`ESC`|Sai|

Teclas, golpes e danos são configurados em `gift\\\\\\\_rules.json`, sem mexer no código.

## Personagens

Todos são originais e fictícios (Polvo e Lagosta formam a dupla inicial). Cada um tem história, cidade de origem, estilo de luta, cores, ícone, cenário próprio e nomes próprios para os quatro golpes.

|Ícone|Lutador|Estilo|Cenário|
|-|-|-|-|
|🐙|**Candidato Polvo** (Aristides Moreira)|Fintas e golpes escorregadios|Eleições 2026|
|🦞|**Candidata Lagosta** (Lourdes Carapaça)|Defesa de casca grossa e contra-golpe|Eleições 2026|
|⚡|**Tempestade** (Ingrid Valença)|Combos rápidos e imprevisíveis|Praia do Pôr do Sol|
|🐍|**Cobra Coral** (Dante Salles)|Ginga enganosa e botes certeiros|Ginásio do Bairro|
|🔨|**Mestre Bigorna** (Osvaldo Ferraz)|Golpes lentos e devastadores|Forja do Vulcão|
|🌙|**Lua Rubra** (Valentina Duarte)|Acrobática, golpes aéreos|Cobertura de Noite|
|🐾|**Pantera do Norte** (Jurema Tapajós)|Paciente, contra-ataque letal|Clareira da Selva|
|💜|**Doutor Pixel** (Teo Brandão)|Combos de arcade, precisão de frame|Arcade Neon|

As histórias completas aparecem no jogo (`TAB`) e ficam em `characters.json`.

Há também o cenário **Eleições 2026** (praça com urnas, bandeirinhas e santinhos, só com imagens genéricas). Ele é o cenário inicial da dupla Polvo x Lagosta; para os outros lutadores, use `F3`.

### Editar ou criar personagens

* Edite `characters.json`: nome, história, cores (`color` e `accent`), `emblem` (`octopus`, `claw`, `bolt`, `fangs`, `anvil`, `crescent`, `paw`, `pixel\\\\\\\_heart`), cenário e `move\\\\\\\_names`.
* Para regenerar os PNGs depois de mudar cores ou emblemas (só para isso precisa do Pillow):

```powershell
  py -3.12 -m pip install pillow
  py -3.12 tools/make\\\\\\\_assets.py
  ```

* Para usar uma arte sua, substitua o PNG em `assets/icons/` (256×256) ou `assets/stages/` (960×540) mantendo o mesmo nome de arquivo. Se um arquivo faltar, o jogo desenha uma versão simples no lugar.

## Instalação no Windows

1. Instale o Python **3.10 a 3.13** (recomendado: 3.12): [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Durante a instalação, marque **Add python.exe to PATH** e **Install launcher for all users**.
Versões mais novas (como 3.14 ou 3.15) podem não ter pacotes pré-compilados do pygame e falhar ao instalar.
3. Abra o PowerShell nesta pasta.
4. Instale as dependências:

```powershell
   py -3.12 -m pip install -r requirements.txt
   ```

5. Execute o jogo:

```powershell
   py -3.12 main.py
   ```

O projeto usa o **pygame-ce** (fork mantido pela comunidade, compatível com `import pygame`).

### Opcional: ambiente virtual

```powershell
py -3.12 -m venv .venv
.venv\\\\\\\\Scripts\\\\\\\\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Se o PowerShell bloquear a ativação, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

No Prompt de Comando (cmd), ative com `.venv\\\\\\\\Scripts\\\\\\\\activate.bat`.

## Problemas comuns

* **`py` ou `python` não reconhecido:** reinstale o Python marcando as opções de PATH e do launcher, depois feche e reabra o terminal.
* **`python` abre a Microsoft Store:** desative os aliases `python.exe` e `python3.exe` em *Configurações > Aplicativos > Configurações avançadas de aplicativos > Aliases de execução de aplicativo*.
* **Erro ao compilar o pygame:** você está numa versão do Python sem pacote pré-compilado. Use o Python 3.12.

## Estrutura do projeto

|Arquivo|Função|
|-|-|
|`main.py`|Loop principal: lê entradas, consome a fila e desenha.|
|`game.py`|Regras de combate (vida, dano, vencedor), troca de personagem/cenário e renderização.|
|`characters.py`|Carrega o elenco, os ícones e os cenários.|
|`characters.json`|Personagens (história, cores, emblema, golpes) e cenários.|
|`assets/`|`icons/` (um PNG por lutador) e `stages/` (um PNG por cenário). `\\\\\\\_preview.png` é só uma prévia.|
|`tools/make\\\\\\\_assets.py`|Gera os PNGs a partir do `characters.json`.|
|`event\\\\\\\_queue.py`|Fila de eventos thread-safe. Rajadas de presentes entram na fila e o jogo consome poucos por quadro, sem travar. Se encher, descarta os mais antigos.|
|`tiktok\\\\\\\_adapter.py`|`RuleBook` (traduz evento em golpe), `KeyboardSource` (simulação) e `TikTokLiveSource` (ainda um esqueleto).|
|`gift\\\\\\\_rules.json`|Golpes, teclas simuladas e regras de associação evento → golpe.|

## Próximos passos

1. Escolher a fonte real de eventos da live e validar os termos e limitações do TikTok para esse uso.
2. Implementar `TikTokLiveSource` (em outra thread ou asyncio) chamando `queue.push()`.
3. Preencher as regras `tiktok` do `gift\\\\\\\_rules.json` com os nomes/IDs reais de presentes e reações.

## Importante

Os comandos atuais são simulados e não representam necessariamente os nomes/valores reais dos presentes ou reações disponíveis em todas as lives. A integração real dependerá de uma fonte de eventos compatível e da validação dos termos e limitações do TikTok.

