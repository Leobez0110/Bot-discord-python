# Bot-gerenciamento

Um bot completo para Discord, focado em automação de metas para jogos, controle de ausências, utilidades administrativas e diversão para servidores de comunidade ou jogos.

---

## ✨ Funcionalidades principais

- **Automação de metas**: Verifica, anuncia e processa prints de metas pagas.
- **Controle de ausências**: Reage automaticamente a mensagens no canal de ausências e permite análise manual de todas as mensagens antigas.
- **Comandos administrativos**: Limpeza de mensagens, edição de análises, ranking de prints, informações detalhadas de membros, cargos e canais.
- **Utilidades e diversão**: Sorteios, enquetes, rolagem de dados, cara ou coroa, mensagens coloridas, avatar, uptime, ping, entre outros.
- **Reações automáticas**: Adiciona reações em canais específicos conforme regras do servidor.

---

## 🚀 Como rodar o bot

1. **Clone o repositório**
   ```bash
   git clone https://github.com/SEU_USUARIO/bot-000.git
   cd bot-000
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o token do bot**
   - Crie um arquivo `.env` na raiz do projeto:
     ```
     DISCORD_TOKEN=SEU_TOKEN_AQUI
     ```
   - (Opcional) Adicione `.env` ao `.gitignore` para não subir seu token ao GitHub.

4. **Rode o bot**
   ```bash
   python3 main.py
   ```

---

## ⚙️ Principais comandos

| Comando                       | Descrição                                              |
|-------------------------------|--------------------------------------------------------|
| `.testar_meta`                | Teste manual da verificação de metas                   |
| `.verificar_hoje`             | Processa prints do dia                                 |
| `.editar_meta <id> <texto>`   | Edita análise de meta (admin)                          |
| `.ranking_prints`             | Ranking de prints enviadas                             |
| `.infos`                      | Informações do servidor                                |
| `.avatar [@membro]`           | Mostra avatar de um membro                             |
| `.sortear @m1 @m2 ...`        | Sorteia um membro                                      |
| `.ping`                       | Mostra latência do bot                                 |
| `.userinfo [@membro]`         | Info detalhada de um usuário                           |
| `.servericon`                 | Mostra o ícone do servidor                             |
| `.limpar <qtd>`               | Limpa mensagens (admin)                                |
| `.uptime`                     | Mostra há quanto tempo o bot está online               |
| `.oi`                         | O bot te cumprimenta                                   |
| `.dm @membro <mensagem>`      | Envia DM para alguém                                   |
| `.dado [lados]`               | Rola um dado                                           |
| `.moeda`                      | Cara ou coroa                                          |
| `.agora`                      | Mostra o horário atual                                 |
| `.serverbanner`               | Mostra o banner do servidor                            |
| `.cargos`                     | Lista todos os cargos                                  |
| `.emojis`                     | Lista todos os emojis                                  |
| `.enquete <pergunta> <opções>`| Cria uma enquete rápida                                |
| `.canalinfo [#canal]`         | Info de canal                                          |
| `.cargoinfo <cargo>`          | Info de cargo                                          |
| `.online`                     | Quantos membros online                                 |
| `.offline`                    | Quantos membros offline                                |
| `.emcall`                     | Quantos membros em call                                |
| `.serveravatar`               | Avatar do servidor                                     |
| `.latency`                    | Tempo de resposta do bot                               |
| `.reverso <texto>`            | Texto ao contrário                                     |
| `.membroscargo <cargo>`       | Quantos membros em um cargo                            |
| `.bots`                       | Lista todos os bots                                    |
| `.boosters`                   | Lista todos os boosters                                |
| `.cor <hex> <texto>`          | Mensagem colorida                                      |
| `.analisar_ausencias`         | Analisa todas as mensagens do canal de ausências       |

---

## 📝 Licença

Este projeto é open-source. Use, modifique e contribua como quiser!

---

## 💡 Créditos

Desenvolvido por Leonardo Cardoso.  
Baseado em discord.py
