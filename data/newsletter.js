/* data/newsletter.js — Configuração da newsletter (editar aqui)
   Ver PRD.md § "Configuração do backend Google" para o passo a passo. */
window.NEWSLETTER_CONFIG = {
  /* URL do Web App do Apps Script (ex.: https://script.google.com/macros/s/AKfyc.../exec).
     Vazio = modo fallback: o formulário compõe um e-mail (mailto) para `contactEmail`. */
  webappUrl: "",

  /* E-mail de contato usado no fallback (mailto) quando o backend não está configurado. */
  contactEmail: "",

  /* URL pública do site (GitHub Pages). Usada no e-mail para logo e botão "Ver painel". */
  siteUrl: "https://ldanill01.github.io/monitor-editais/"
};
