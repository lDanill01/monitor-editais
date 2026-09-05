# Guia de ativação da newsletter

Este guia coloca a newsletter em funcionamento sem alterar o código. Execute os passos na ordem apresentada e marque cada item quando terminar.

## Antes de começar

Você precisará de:

- Uma conta Google que será dona da planilha e do Apps Script.
- Uma conta Gmail que enviará os e-mails. Pode ser a mesma conta Google.
- Acesso de edição a este projeto e ao repositório GitHub Pages.
- Um endereço de e-mail seu para os testes.

Não registre senhas, chaves ou URLs privadas no Git.

## 1. Criar a planilha de assinantes

- [ ] Acesse [Google Sheets](https://sheets.google.com) e crie uma planilha em branco.
- [ ] Renomeie a primeira aba para **Assinantes**.
- [ ] Dê à planilha um nome identificável, como `Radar de Editais — Assinantes`.
- [ ] Mantenha a planilha privada; ela armazenará nome, e-mail, status e tokens de confirmação.

Não crie as colunas manualmente. O Apps Script as cria na primeira assinatura.

## 2. Configurar o Apps Script

- [ ] Na planilha, acesse **Extensões → Apps Script**.
- [ ] Remova o código inicial do editor.
- [ ] Abra localmente [appsscript_subscribers.gs](/Users/danillosantanadearaujo/Documents/Python%20Scripts/monitor-editais/scripts/google/appsscript_subscribers.gs), copie todo o conteúdo e cole no editor.
- [ ] Localize a linha `var API_KEY = '';`.
- [ ] Substitua o valor vazio por uma chave longa e exclusiva. Guarde-a em local seguro, pois será usada novamente no passo 5.
- [ ] Clique em **Salvar**.

Exemplo de formato da chave:

```js
var API_KEY = 'troque-por-uma-chave-longa-e-aleatoria';
```

## 3. Publicar o Apps Script como Web App

- [ ] No Apps Script, clique em **Implantar → Nova implantação**.
- [ ] Em “Selecionar tipo”, escolha **Aplicativo da Web**.
- [ ] Em “Executar como”, escolha **Eu**.
- [ ] Em “Quem tem acesso”, escolha a opção que permite acesso a qualquer pessoa.
- [ ] Clique em **Implantar** e aceite as permissões solicitadas para Planilhas e Gmail.
- [ ] Copie a URL final da implantação. Ela deve terminar em `/exec`.

Guarde esta URL. Ela será usada pelo formulário público e pelo script de envio.

## 4. Conectar o formulário do site

Abra [data/newsletter.js](/Users/danillosantanadearaujo/Documents/Python%20Scripts/monitor-editais/data/newsletter.js) e preencha `webappUrl` com a URL copiada.

```js
webappUrl: "https://script.google.com/macros/s/SEU_ID/exec",
```

Abra [newsletter_config.json](/Users/danillosantanadearaujo/Documents/Python%20Scripts/monitor-editais/scripts/newsletter_config.json) e preencha `webapp_url` com a mesma URL.

```json
"webapp_url": "https://script.google.com/macros/s/SEU_ID/exec",
```

- [ ] As duas URLs são iguais e terminam em `/exec`.
- [ ] Nenhuma chave secreta foi colocada nesses dois arquivos.

## 5. Configurar a conta remetente no Gmail

- [ ] Entre na conta Gmail que enviará os digests.
- [ ] Ative a verificação em duas etapas da conta Google.
- [ ] Em **Segurança → Senhas de app**, gere uma senha de app para “E-mail”.
- [ ] Copie a senha de app; ela será mostrada uma única vez.

No terminal, dentro da pasta do projeto, defina as variáveis apenas para a sessão atual:

```zsh
export GMAIL_USER="seu-email@gmail.com"
export GMAIL_APP_PASSWORD="senha-de-app-gerada-pelo-gmail"
export NEWSLETTER_API_KEY="a-mesma-chave-definida-no-apps-script"
```

Para não repetir esse comando a cada uso, crie o arquivo local `scripts/newsletter_secrets.json`. Ele já é ignorado pelo Git.

```json
{
  "gmail_user": "seu-email@gmail.com",
  "gmail_app_password": "senha-de-app-gerada-pelo-gmail",
  "newsletter_api_key": "a-mesma-chave-definida-no-apps-script"
}
```

- [ ] O arquivo contém apenas valores reais, sem aspas extras ou comentários.
- [ ] `git status` não mostra `scripts/newsletter_secrets.json`.

## 6. Testar a assinatura completa

- [ ] Abra `index.html` no navegador ou publique uma versão de teste no GitHub Pages.
- [ ] Clique no botão laranja **Newsletter**.
- [ ] Preencha nome, e-mail de teste e consentimento.
- [ ] Envie o formulário e confirme que a mensagem informa o envio da confirmação.
- [ ] Abra o e-mail recebido e clique em **Confirmar assinatura**.
- [ ] Na planilha, confirme que o registro aparece com status `ativo`.
- [ ] Use o link de cancelamento recebido e confirme que o status muda para `cancelado`.
- [ ] Assine novamente e confirme a ativação para continuar o teste de envio.

Se o formulário não responder, confira se `webappUrl` contém a URL `/exec` e se a implantação está configurada para acesso público.

## 7. Revisar e enviar o primeiro digest

Gere uma prévia local. Este comando não envia e-mail:

```zsh
python3 scripts/send_newsletter.py --preview
```

- [ ] Abra o arquivo indicado dentro da pasta `newsletter/` e revise o conteúdo, os links e o rodapé.

Envie uma edição apenas para você:

```zsh
python3 scripts/send_newsletter.py --test-to seu-email@exemplo.com
```

- [ ] Confira caixa de entrada, spam, layout, links e botão de cancelamento.

Quando tudo estiver correto, envie aos assinantes ativos:

```zsh
python3 scripts/send_newsletter.py --send
```

O script registra quem recebeu a edição em `newsletter/sent_log.json`, evitando duplicidade se for executado novamente.

## 8. Publicar o site configurado

Depois de validar o formulário e o e-mail:

```zsh
git add data/newsletter.js scripts/newsletter_config.json
git commit -m "configura newsletter"
git push
```

- [ ] Abra o GitHub Pages e teste novamente o botão **Newsletter** na página pública.

## Rotina semanal

```zsh
python3 scripts/md_to_json.py data/Monitoramento_Editais_Inovacao_YYYY-MM-DD.md data/editais.json
python3 scripts/send_newsletter.py --preview
python3 scripts/send_newsletter.py --send
git push
```

Envie somente após revisar a prévia. Caso o lote seja maior que o limite configurado, o script informa quantos assinantes restam; reexecute no próximo dia para continuar sem duplicar os já enviados.

## Solução rápida de problemas

| Situação | Verificação e ação |
| --- | --- |
| O formulário mostra que assinaturas estão indisponíveis | Preencha `webappUrl` em `data/newsletter.js` e publique o site novamente. |
| Nenhum e-mail de confirmação chega | Verifique Spam; depois abra o histórico de execuções do Apps Script e confira as permissões do Gmail. |
| O script acusa `webapp_url vazio` | Preencha `scripts/newsletter_config.json` com a mesma URL `/exec`. |
| O script acusa chave recusada | Confirme que `NEWSLETTER_API_KEY` é idêntica a `API_KEY` do Apps Script. |
| O script não autentica no Gmail | Gere uma nova senha de app e confirme que a autenticação em duas etapas está ativa. |
| O e-mail foi enviado duas vezes | Não remova `newsletter/sent_log.json`; ele é a proteção contra duplicidade. |
