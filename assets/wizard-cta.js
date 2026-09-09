/* ============================================================
   Hogarex — wizard de solicitud + CTA flotante, compartido en
   todo el sitio (un solo archivo, referenciado desde cada página).
   
   1) Si la página no trae su propio wizard embebido (detectado por
      #srModal), se inyecta acá: CSS + modal + todo el motor JS
      (mismos datos de precio que /solicitud-enviar).
   2) El popup flotante "¿Necesitás un profesional?" se inyecta
      siempre (si no existe ya) y su botón abre el wizard en la
      misma página, nunca redirige.
   ============================================================ */
(function () {
  function injectStyle(css) {
    var tag = document.createElement('style');
    tag.textContent = css;
    document.head.appendChild(tag);
  }

  if (!document.getElementById('srModal')) {
    injectStyle("    /* \u2500\u2500 WIZARD DE SOLICITUD (embebido) \u2500\u2500 */\n    .sr-overlay { position: fixed; inset: 0; background: rgba(9,30,68,.55); opacity: 0; visibility: hidden; transition: opacity .25s ease; z-index: 998; }\n    .sr-overlay.open { opacity: 1; visibility: visible; }\n    .sr-modal { position: fixed; inset: 0; background: #ffffff; z-index: 999; display: flex; flex-direction: column; opacity: 0; visibility: hidden; transform: translateY(16px); transition: opacity .25s ease, transform .25s ease, visibility .25s; font-family: 'Inter', -apple-system, sans-serif; }\n    .sr-modal.open { opacity: 1; visibility: visible; transform: translateY(0); }\n    @media (min-width: 640px) {\n      .sr-modal { inset: auto; top: 50%; left: 50%; width: 100%; max-width: 560px; max-height: 88vh; height: auto; border-radius: 20px; box-shadow: 0 12px 40px rgba(13,42,94,0.22); transform: translate(-50%, -46%); }\n      .sr-modal.open { transform: translate(-50%, -50%); }\n    }\n    .sr-modal-head { flex-shrink: 0; padding: 16px 18px 0; }\n    .sr-head-top { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }\n    .sr-progress { flex: 1; height: 6px; background: #f0f2f5; border-radius: 999px; overflow: hidden; }\n    .sr-progress-bar { height: 100%; width: 0%; background: #206ff7; border-radius: 999px; transition: width .3s ease; }\n    .sr-close { background: none; border: none; font-size: 24px; line-height: 1; color: #6b7280; cursor: pointer; padding: 4px 6px; flex-shrink: 0; }\n    .sr-back { background: none; border: none; display: inline-flex; align-items: center; gap: 4px; color: #6b7280; font-size: 0.85rem; font-weight: 600; cursor: pointer; padding: 4px 0 10px; visibility: hidden; }\n    .sr-back.show { visibility: visible; }\n    .sr-direct-banner { display: none; align-items: center; gap: 8px; background: #eaf1ff; color: #003366; font-size: 0.82rem; font-weight: 700; padding: 10px 14px; border-radius: 10px; margin: 0 18px 12px; }\n    .sr-direct-banner.show { display: flex; }\n    .sr-direct-banner svg { flex-shrink: 0; color: #206ff7; }\n\n    .sr-body { flex: 1; overflow-y: auto; padding: 4px 18px 18px; }\n    .sr-step { display: none; }\n    .sr-step.active { display: block; animation: srFadeIn .2s ease; }\n    @keyframes srFadeIn { from { opacity: 0; transform: translateX(8px); } to { opacity: 1; transform: translateX(0); } }\n    .sr-step-title { font-family: 'Sora', sans-serif; font-size: 1.25rem; font-weight: 800; color: #003366; margin-bottom: 4px; line-height: 1.3; }\n    .sr-step-sub { font-size: 0.88rem; color: #6b7280; margin-bottom: 18px; }\n\n    .sr-options { display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; }\n    .sr-options.sr-options-1col { grid-template-columns: 1fr; }\n    .sr-opt { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; background: #ffffff; border: 1.5px solid #e5e9f0; border-radius: 12px; padding: 14px; cursor: pointer; text-align: left; font-family: inherit; transition: border-color .15s ease, background .15s ease; }\n    .sr-opt:hover { border-color: #206ff7; background: #eaf1ff; }\n    .sr-opt.selected { border-color: #206ff7; background: #eaf1ff; box-shadow: inset 0 0 0 1px #206ff7; }\n    .sr-opt-icon { width: 34px; height: 34px; border-radius: 9px; background: #eaf1ff; color: #206ff7; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }\n    .sr-opt.selected .sr-opt-icon { background: #206ff7; color: #fff; }\n    .sr-opt-label { font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.88rem; color: #003366; line-height: 1.3; }\n    .sr-opt-note { font-size: 0.74rem; color: #6b7280; }\n    .sr-opt-row { flex-direction: row; align-items: center; }\n    .sr-opt-row .sr-opt-icon { margin-bottom: 0; }\n\n    .sr-field { margin-bottom: 16px; }\n    .sr-field label { display: block; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.85rem; color: #003366; margin-bottom: 8px; }\n    .sr-input, .sr-select, .sr-textarea { width: 100%; border: 1.5px solid #e5e9f0; border-radius: 10px; padding: 13px 14px; font-size: 18px; font-family: inherit; color: #1a1a2e; background: #ffffff; }\n    .sr-input:focus, .sr-select:focus, .sr-textarea:focus { outline: none; border-color: #206ff7; }\n    .sr-textarea { resize: vertical; min-height: 80px; }\n    .sr-hint { font-size: 0.76rem; color: #6b7280; margin-top: 6px; }\n\n    .sr-estimate-card { background: linear-gradient(135deg, #003366 0%, #0a4a8c 100%); color: #fff; border-radius: 16px; padding: 24px 20px; text-align: center; margin-bottom: 18px; }\n    .sr-estimate-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; opacity: .8; margin-bottom: 8px; }\n    .sr-estimate-price { font-family: 'Sora', sans-serif; font-size: 1.7rem; font-weight: 800; margin-bottom: 6px; }\n    .sr-estimate-note { font-size: 0.82rem; opacity: .85; }\n    .sr-summary { background: #f8f9fb; border: 1px solid #f0f2f5; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px; }\n    .sr-summary-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 0.85rem; }\n    .sr-summary-row + .sr-summary-row { border-top: 1px solid #f0f2f5; }\n    .sr-summary-row span:first-child { color: #6b7280; }\n    .sr-summary-row span:last-child { color: #003366; font-weight: 700; text-align: right; }\n    .sr-summary-edit { background: none; border: none; color: #206ff7; font-weight: 700; font-size: 0.78rem; cursor: pointer; padding: 0; }\n\n    .sr-time-row { display: flex; align-items: center; gap: 10px; background: #e6f4ea; color: #1a7a3c; border-radius: 10px; padding: 12px 14px; font-size: 0.85rem; font-weight: 600; margin-bottom: 16px; }\n    .sr-time-row svg { flex-shrink: 0; }\n\n    .sr-footer { flex-shrink: 0; padding: 14px 18px; border-top: 1px solid #f0f2f5; display: flex; gap: 10px; }\n    .sr-btn { flex: 1; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.95rem; padding: 14px; border-radius: 999px; cursor: pointer; border: none; text-align: center; }\n    .sr-btn-yellow { background: #F5C518; color: #003366; }\n    .sr-btn-yellow:hover { background: #e0b200; }\n    .sr-btn-yellow:disabled { background: #e5e9f0; color: #6b7280; cursor: not-allowed; }\n    .sr-btn-outline { flex: 0 0 auto; background: #fff; color: #003366; border: 1.5px solid #e5e9f0; padding: 14px 18px; }\n    .sr-btn-whatsapp { background: #25D366; color: #fff; display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; }\n    .sr-btn-whatsapp:hover { background: #1eb958; }\n\n    .sr-success { text-align: center; padding: 20px 0; }\n    .sr-success-icon { width: 68px; height: 68px; border-radius: 50%; background: #e6f4ea; color: #1a7a3c; display: flex; align-items: center; justify-content: center; margin: 0 auto 18px; }\n    .sr-success h2 { font-family: 'Sora', sans-serif; font-size: 1.3rem; color: #003366; margin-bottom: 10px; }\n    .sr-success p { font-size: 0.92rem; color: #374151; line-height: 1.6; margin-bottom: 6px; }\n    body.sr-locked { overflow: hidden; }\n\n");
    document.body.insertAdjacentHTML('beforeend', "<div class=\"sr-overlay\" id=\"srOverlay\"></div>\n<div class=\"sr-modal\" id=\"srModal\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Solicitar presupuesto\">\n  <div class=\"sr-modal-head\">\n    <div class=\"sr-head-top\">\n      <button type=\"button\" class=\"sr-back\" id=\"srBackBtn\">\n        <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M15 18l-6-6 6-6\"/></svg>\n        Atr\u00e1s\n      </button>\n      <div class=\"sr-progress\"><div class=\"sr-progress-bar\" id=\"srProgressBar\"></div></div>\n      <button type=\"button\" class=\"sr-close\" id=\"srCloseBtn\" aria-label=\"Cerrar\">&times;</button>\n    </div>\n    <div class=\"sr-direct-banner\" id=\"srDirectBanner\">\n      <svg width=\"16\" height=\"16\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.5\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"8\" r=\"4\"/><path d=\"M4 21c0-4 3.5-7 8-7s8 3 8 7\"/></svg>\n      <span id=\"srDirectBannerText\">Solicitud directa</span>\n    </div>\n  </div>\n  <div class=\"sr-body\" id=\"srBody\"></div>\n  <div class=\"sr-footer\" id=\"srFooter\">\n    <button type=\"button\" class=\"sr-btn sr-btn-yellow\" id=\"srNextBtn\" disabled>Continuar</button>\n  </div>\n</div>");

/* ============================================================
   Wizard de solicitud embebido (mismo motor que /solicitud-enviar).
   Datos de precios: extraídos de /precios-mano-de-obra (AAIERIC, CAGP
   y relevamiento de mercado 2026). Rangos orientativos, no vinculantes.
   ============================================================ */
var ICONS = {
  zap: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  flame: '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
  droplet: '<path d="M12 22c3.87 0 7-3.13 7-7 0-4-3-7-7-13-4 6-7 9-7 13 0 3.87 3.13 7 7 7Z"/>',
  brush: '<path d="M18.37 2.63 14 7l-1.59-1.59a2 2 0 0 0-2.82 0L8 7l9 9 1.59-1.59a2 2 0 0 0 0-2.82L17 10l4.37-4.37a2.12 2.12 0 1 0-3-3Z"/><path d="M9 8c-2 3-4 3.5-7 4l8 8c2.5-2.5 3-4.5 4-7"/>',
  hammer: '<path d="m15 12-8.5 8.5a2.12 2.12 0 1 1-3-3L12 9"/><path d="M17.64 15 22 10.64"/><path d="m20.91 11.7-1.25-1.25c-.6-.6-.93-1.4-.93-2.25v-.86L16.01 4.6a5.56 5.56 0 0 0-3.94-1.64H9l.92.82A6.18 6.18 0 0 1 12 8.4v1.56l2 2h2.47l2.26 1.91"/>',
  wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  alert: '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  doc: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
  check: '<circle cx="12" cy="12" r="9"/><path d="m9 12 2 2 4-4"/>',
  snow: '<line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="7" x2="22" y2="17"/><line x1="2" y1="17" x2="22" y2="7"/>',
  cam: '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2Z"/><circle cx="12" cy="13" r="4"/>',
  box: '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="M3.27 6.96 12 12l8.73-5.04"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
  dots: '<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>'
};
function ic(name, size) {
  size = size || 20;
  return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + ICONS[name] + '</svg>';
}

var RUBROS = [
  { id: 'electricista', label: 'Electricista', icon: 'zap' },
  { id: 'gasista', label: 'Gasista', icon: 'flame' },
  { id: 'plomero', label: 'Plomero', icon: 'droplet' },
  { id: 'pintor', label: 'Pintor', icon: 'brush' },
  { id: 'carpintero', label: 'Carpintero', icon: 'hammer' },
  { id: 'instalaciones', label: 'Instalaciones', icon: 'wrench' }
];
var RUBRO_LABELS = {};
RUBROS.forEach(function (r) { RUBRO_LABELS[r.id] = r.label; });

var UBICACIONES = ['Buenos Aires (CABA)', 'Buenos Aires (GBA)', 'Córdoba Capital'];

var TIEMPO_NORMAL = 'Recibís respuesta en menos de 2 horas en horario hábil.';
var TIEMPO_URGENTE = 'Es una urgencia: en general hay profesionales disponibles el mismo día.';

var JOB_TREE = {
  electricista: {
    categorias: [
      { id: 'instalar', label: 'Instalar algo nuevo', icon: 'plus' },
      { id: 'falla', label: 'Arreglar una falla', icon: 'alert' },
      { id: 'certificado', label: 'Certificado eléctrico', icon: 'doc' },
      { id: 'mantenimiento', label: 'Mantenimiento / revisión', icon: 'check' }
    ],
    detalles: {
      instalar: [
        { id: 'toma', label: 'Toma o boca eléctrica', price: [19000, 108000] },
        { id: 'tablero', label: 'Tablero eléctrico completo', price: [320000, 910000] },
        { id: 'iluminacion', label: 'Luces / artefactos LED', price: [30000, 136000] },
        { id: 'aire', label: 'Punto para aire acondicionado', price: [43000, 78000] },
        { id: 'pat', label: 'Puesta a tierra', price: [150000, 180000] }
      ],
      falla: [
        { id: 'corte', label: 'Se corta la luz / salta la térmica', price: [54000, 130000] },
        { id: 'chispas', label: 'Chispas, olor a quemado', price: [80000, 150000], urgente: true },
        { id: 'tomacorriente', label: 'Un tomacorriente no funciona', price: [19000, 55000] },
        { id: 'otro', label: 'Otro problema', price: [54000, 110000] }
      ],
      certificado: [
        { id: 'alquilarvender', label: 'Para alquilar o vender', price: [400000, 600000] },
        { id: 'renovar', label: 'Para renovar el contrato de luz', price: [400000, 600000] },
        { id: 'noseguro', label: 'No estoy seguro cuál necesito', price: [54000, 600000] }
      ],
      mantenimiento: [
        { id: 'revision', label: 'Revisión general del tablero', price: [54000, 162000] },
        { id: 'pat', label: 'Puesta a tierra', price: [150000, 180000] },
        { id: 'otro', label: 'Otro', price: [54000, 130000] }
      ]
    }
  },
  gasista: {
    categorias: [
      { id: 'instalar', label: 'Instalar algo nuevo', icon: 'plus' },
      { id: 'falla', label: 'Arreglar una falla', icon: 'alert' },
      { id: 'certificado', label: 'Certificado de gas', icon: 'doc' },
      { id: 'mantenimiento', label: 'Mantenimiento / limpieza', icon: 'check' }
    ],
    detalles: {
      instalar: [
        { id: 'calefon', label: 'Calefón o termotanque', price: [148000, 206000] },
        { id: 'cocina', label: 'Cocina o anafe', price: [91000, 171000] },
        { id: 'calefactor', label: 'Calefactor o estufa', price: [92000, 201000] },
        { id: 'canieria', label: 'Cañería de gas nueva', price: [280000, 400000] }
      ],
      falla: [
        { id: 'olor', label: 'Olor a gas / pérdida', price: [90000, 150000], urgente: true },
        { id: 'calefonapagado', label: 'El calefón no enciende', price: [90000, 150000] },
        { id: 'otro', label: 'Otro problema', price: [90000, 180000] }
      ],
      certificado: [
        { id: 'gas3', label: 'Instalación de hasta 3 bocas', price: [520000, 725000] },
        { id: 'gas10', label: 'Instalación de hasta 10 bocas', price: [520000, 725000] },
        { id: 'noseguro', label: 'No estoy seguro', price: [200000, 725000] }
      ],
      mantenimiento: [
        { id: 'limpieza', label: 'Limpieza de artefactos', price: [90000, 150000] },
        { id: 'otro', label: 'Otro', price: [90000, 150000] }
      ]
    }
  },
  plomero: {
    categorias: [
      { id: 'instalar', label: 'Instalar algo nuevo', icon: 'plus' },
      { id: 'falla', label: 'Arreglar una falla', icon: 'alert' },
      { id: 'destape', label: 'Destape / caño tapado', icon: 'droplet' },
      { id: 'mantenimiento', label: 'Mantenimiento', icon: 'check' }
    ],
    detalles: {
      instalar: [
        { id: 'artefacto', label: 'Inodoro, bacha o grifería', price: [98000, 148000] },
        { id: 'termotanque', label: 'Termotanque nuevo', price: [125000, 183000] },
        { id: 'tanque', label: 'Tanque de agua', price: [241000, 480000] },
        { id: 'bomba', label: 'Bomba presurizadora', price: [109000, 240000] }
      ],
      falla: [
        { id: 'perdida', label: 'Pérdida de agua / caño roto', price: [69000, 182000], urgente: true },
        { id: 'canilla', label: 'Canilla que gotea', price: [20000, 91000] },
        { id: 'otro', label: 'Otro problema', price: [80000, 160000] }
      ],
      destape: [
        { id: 'horizontal', label: 'Cañería horizontal tapada', price: [90000, 140000] },
        { id: 'vertical', label: 'Cañería vertical tapada', price: [80000, 140000], urgente: true },
        { id: 'otro', label: 'No estoy seguro', price: [80000, 150000] }
      ],
      mantenimiento: [
        { id: 'tanquelimp', label: 'Limpieza de tanque de agua', price: [120000, 322000] },
        { id: 'otro', label: 'Revisión general', price: [90000, 160000] }
      ]
    }
  },
  pintor: {
    categorias: [
      { id: 'interior', label: 'Pintura de interior', icon: 'brush' },
      { id: 'exterior', label: 'Pintura de exterior / frente', icon: 'brush' },
      { id: 'reparacion', label: 'Reparación de paredes', icon: 'wrench' },
      { id: 'impermeabilizacion', label: 'Impermeabilización', icon: 'droplet' }
    ],
    detalles: {
      interior: [
        { id: 'monoambiente', label: '1 ambiente', price: [65000, 140000] },
        { id: 'dosambientes', label: '2 ambientes + baño', price: [105000, 230000] },
        { id: 'cielorraso', label: 'Solo cielorrasos', price: [40000, 100000] },
        { id: 'noseguro', label: 'Todavía no sé', price: [65000, 230000] }
      ],
      exterior: [
        { id: 'frente', label: 'Frente de casa o PH', price: [90000, 250000] },
        { id: 'altura', label: 'Pintura en altura', price: [110000, 280000], urgente: false },
        { id: 'noseguro', label: 'Todavía no sé', price: [90000, 280000] }
      ],
      reparacion: [
        { id: 'grietas', label: 'Grietas o humedad puntual', price: [40000, 110000] },
        { id: 'enduido', label: 'Enduido y repintado', price: [60000, 150000] }
      ],
      impermeabilizacion: [
        { id: 'azotea', label: 'Azotea o terraza', price: [90000, 220000] },
        { id: 'membrana', label: 'Colocación de membrana', price: [80000, 200000] }
      ]
    }
  },
  carpintero: {
    categorias: [
      { id: 'instalar', label: 'Mueble o instalación nueva', icon: 'plus' },
      { id: 'reparar', label: 'Reparar o restaurar', icon: 'wrench' },
      { id: 'puertas', label: 'Puertas y aberturas', icon: 'hammer' },
      { id: 'pisos', label: 'Pisos de madera', icon: 'hammer' }
    ],
    detalles: {
      instalar: [
        { id: 'cocina', label: 'Mueble de cocina a medida', price: [185000, 460000] },
        { id: 'placard', label: 'Placard o vestidor a medida', price: [200000, 450000] },
        { id: 'estanteria', label: 'Estantería o biblioteca', price: [80000, 250000] },
        { id: 'noseguro', label: 'Todavía no sé', price: [80000, 460000] }
      ],
      reparar: [
        { id: 'mueble', label: 'Mueble o cajón roto', price: [10000, 32000] },
        { id: 'restaurar', label: 'Restaurar mueble antiguo', price: [40000, 150000] }
      ],
      puertas: [
        { id: 'ajuste', label: 'Puerta que no cierra bien', price: [19000, 30000] },
        { id: 'colocar', label: 'Colocar puerta nueva', price: [40000, 92000] },
        { id: 'cerradura', label: 'Cambiar cerradura', price: [15000, 36000] }
      ],
      pisos: [
        { id: 'lijado', label: 'Lijado y barnizado (por m²)', price: [3400, 24500] },
        { id: 'colocacion', label: 'Colocación de piso nuevo (por m²)', price: [4700, 8200] },
        { id: 'reparar-tablas', label: 'Cambiar tablas dañadas (por m²)', price: [40000, 90000] }
      ]
    }
  },
  instalaciones: {
    categorias: [
      { id: 'aire', label: 'Aire acondicionado', icon: 'snow' },
      { id: 'seguridad', label: 'Cámaras / videoportero', icon: 'cam' },
      { id: 'mantenimiento', label: 'Mantenimiento', icon: 'check' },
      { id: 'otro', label: 'Otra instalación', icon: 'dots' }
    ],
    detalles: {
      aire: [
        { id: 'split-chico', label: 'Split hasta 3.000 frigorías', price: [90000, 175000] },
        { id: 'split-mediano', label: 'Split 3.000 a 4.500 frigorías', price: [130000, 200000] },
        { id: 'split-grande', label: 'Split más de 4.500 frigorías', price: [155000, 200000] },
        { id: 'desinstalar', label: 'Desinstalar equipo', price: [60000, 140000] }
      ],
      seguridad: [
        { id: 'camaras', label: 'Cámaras de seguridad', price: [90000, 180000] },
        { id: 'videoportero', label: 'Videoportero', price: [90000, 180000] }
      ],
      mantenimiento: [
        { id: 'limpieza-ac', label: 'Limpieza de aire acondicionado', price: [47000, 128000] },
        { id: 'gas-ac', label: 'Carga de gas refrigerante', price: [48000, 82000] },
        { id: 'diagnostico', label: 'Diagnóstico de falla', price: [35000, 90000] }
      ],
      otro: [
        { id: 'domotica', label: 'Domótica / automatización', price: [80000, 250000] },
        { id: 'noseguro', label: 'Prefiero contarlo con mis palabras', price: [60000, 200000] }
      ]
    }
  }
};

/* ============================================================
   Estado del wizard. presetCategoria/presetDetalle permiten que
   la sección "¿Cuál es tu problema hoy?" abra el wizard salteando
   directo a la ubicación, con el trabajo puntual ya resuelto.
   ============================================================ */
var qp = new URLSearchParams(window.location.search);
var presetRubro = normalizeRubro(qp.get('rubro'));
var presetUbicacion = qp.get('ubicacion') || '';
var presetTrader = qp.get('trader') || '';
var presetNombre = qp.get('nombre') || '';
var presetCategoria = '';
var presetDetalle = '';

function normalizeRubro(v) {
  if (!v) return '';
  var map = {
    electricista: 'electricista', electricistas: 'electricista',
    gasista: 'gasista', gasistas: 'gasista',
    plomero: 'plomero', plomeros: 'plomero',
    pintor: 'pintor', pintores: 'pintor',
    carpintero: 'carpintero', carpinteros: 'carpintero',
    instalaciones: 'instalaciones', instalacion: 'instalaciones'
  };
  return map[v.toLowerCase()] || '';
}

var state = {
  isDirect: !!presetTrader,
  trader: presetTrader,
  nombreProfesional: presetNombre,
  rubro: presetRubro || '',
  categoria: '',
  detalle: '',
  ubicacion: presetUbicacion || '',
  descripcion: '',
  nombre: '',
  telefono: ''
};

var STEP_ORDER = [];
function buildSteps() {
  STEP_ORDER = [];
  if (!presetRubro) STEP_ORDER.push('rubro');
  if (!presetCategoria) STEP_ORDER.push('categoria');
  /* Si el usuario contó el problema con sus palabras en "categoria", no
     tiene sentido pedirle que elija un detalle de una lista que no aplica. */
  if (!presetDetalle && state.categoria !== '__manual__') STEP_ORDER.push('detalle');
  if (!presetUbicacion) STEP_ORDER.push('ubicacion');
  STEP_ORDER.push('estimate');
  STEP_ORDER.push('contacto');
  STEP_ORDER.push('success');
}
buildSteps();
var stepIndex = 0;

var srOverlay = document.getElementById('srOverlay');
var srModal = document.getElementById('srModal');
var srBody = document.getElementById('srBody');
var srNextBtn = document.getElementById('srNextBtn');
var srBackBtn = document.getElementById('srBackBtn');
var srCloseBtn = document.getElementById('srCloseBtn');
var srProgressBar = document.getElementById('srProgressBar');
var srDirectBanner = document.getElementById('srDirectBanner');
var srDirectBannerText = document.getElementById('srDirectBannerText');
var srFooter = document.getElementById('srFooter');

function fmtPrice(n) {
  return '$' + Math.round(n).toLocaleString('es-AR');
}

function openWizard() {
  document.body.classList.add('sr-locked');
  srOverlay.classList.add('open');
  srModal.classList.add('open');
  renderStep();
}
function closeWizard() {
  document.body.classList.remove('sr-locked');
  srOverlay.classList.remove('open');
  srModal.classList.remove('open');
}
/* En index.html hay varios puntos de entrada al wizard en la misma
   carga de página (hero, chips de "¿cuál es tu problema hoy?", botón
   del menú). Sin este reset, los presets/estado de una apertura previa
   quedaban pisando la siguiente (ej: abrir un chip y después el botón
   del menú saltaba pasos de más). Cada entrada arranca de cero acá. */
function resetWizardState() {
  presetRubro = '';
  presetCategoria = '';
  presetDetalle = '';
  presetUbicacion = '';
  presetTrader = '';
  presetNombre = '';
  state = {
    isDirect: false,
    trader: '',
    nombreProfesional: '',
    rubro: '',
    categoria: '',
    detalle: '',
    ubicacion: '',
    descripcion: '',
    nombre: '',
    telefono: ''
  };
}
/* Punto de entrada "genérico": flujo completo desde cero. */
function openWizardFresh() {
  resetWizardState();
  buildSteps();
  stepIndex = 0;
  openWizard();
}
/* Abre el wizard directamente en una tarea puntual: rubro, categoría y
   detalle ya resueltos (usado por la sección "¿Cuál es tu problema hoy?"
   y por el formulario del hero cuando el rubro elegido tiene datos de
   precio de referencia). ubicacion queda sin presetear a propósito. */
function openWizardForTask(rubro, categoria, detalle) {
  resetWizardState();
  presetRubro = rubro;
  presetCategoria = categoria;
  presetDetalle = detalle;
  state.rubro = rubro;
  state.categoria = categoria;
  state.detalle = detalle;
  buildSteps();
  stepIndex = 0;
  openWizard();
}
/* Abre el wizard con rubro y ubicación ya resueltos (usado por el hero) */
function openWizardWithRubro(rubro, ubicacion) {
  resetWizardState();
  presetRubro = rubro;
  presetUbicacion = ubicacion || '';
  state.rubro = rubro;
  state.ubicacion = ubicacion || '';
  buildSteps();
  stepIndex = 0;
  openWizard();
}
srOverlay.addEventListener('click', closeWizard);
srCloseBtn.addEventListener('click', closeWizard);
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape' && srModal.classList.contains('open')) closeWizard();
});

srBackBtn.addEventListener('click', function () {
  if (stepIndex > 0) {
    stepIndex--;
    renderStep();
  }
});
srNextBtn.addEventListener('click', function () {
  goNext();
});

function currentStepId() {
  return STEP_ORDER[stepIndex];
}

function updateChrome() {
  var pct = Math.round(((stepIndex + 1) / STEP_ORDER.length) * 100);
  srProgressBar.style.width = pct + '%';
  srBackBtn.classList.toggle('show', stepIndex > 0 && currentStepId() !== 'success');
  if (state.isDirect) {
    srDirectBannerText.textContent = 'Solicitud directa' + (state.nombreProfesional ? ' a ' + state.nombreProfesional : ' a este profesional');
    srDirectBanner.classList.add('show');
  } else {
    srDirectBanner.classList.remove('show');
  }
}

function renderStep() {
  if (stepIndex >= STEP_ORDER.length) stepIndex = STEP_ORDER.length - 1;
  updateChrome();
  var id = currentStepId();
  srBody.innerHTML = STEP_RENDERERS[id]();
  bindStepEvents(id);
  validateStep();
  srFooter.style.display = (id === 'success') ? 'none' : 'flex';
  srBody.scrollTop = 0;
}

function goNext() {
  var id = currentStepId();
  if (id === 'contacto') {
    submitSolicitud();
    return;
  }
  if (stepIndex < STEP_ORDER.length - 1) {
    stepIndex++;
    renderStep();
  }
}

function selectAndAdvance() {
  setTimeout(function () {
    if (stepIndex < STEP_ORDER.length - 1) {
      stepIndex++;
      renderStep();
    }
  }, 220);
}

/* ---------- validación por paso ---------- */
function validateStep() {
  var id = currentStepId();
  var ok = true;
  if (id === 'rubro') ok = !!state.rubro;
  else if (id === 'categoria') ok = !!state.categoria && (state.categoria !== '__manual__' || !!(state.descripcion && state.descripcion.trim()));
  else if (id === 'detalle') ok = !!state.detalle && (state.detalle !== '__manual__' || !!(state.descripcion && state.descripcion.trim()));
  else if (id === 'ubicacion') ok = !!state.ubicacion;
  else if (id === 'estimate') ok = true;
  else if (id === 'contacto') ok = !!state.nombre && isValidPhone(state.telefono);
  srNextBtn.disabled = !ok;
  srNextBtn.textContent = id === 'contacto' ? 'Enviar solicitud' : (id === 'estimate' ? 'Continuar' : 'Continuar');
}
function isValidPhone(v) {
  var digits = (v || '').replace(/[^0-9]/g, '');
  return digits.length >= 8;
}

/* Busca el detalle elegido en el catálogo de precios. Devuelve undefined
   si el usuario contó el trabajo con sus palabras (categoria o detalle
   "__manual__"), o si por algún motivo no matchea ningún id conocido. */
function getDetalleObj() {
  var list = (JOB_TREE[state.rubro] && JOB_TREE[state.rubro].detalles[state.categoria]) || [];
  return list.filter(function (o) { return o.id === state.detalle; })[0];
}

/* ---------- renderers ---------- */
var STEP_RENDERERS = {
  rubro: function () {
    var html = '<div class="sr-step-title">¿Qué tipo de profesional necesitás?</div>' +
      '<div class="sr-step-sub">Elegí el rubro que mejor describe tu problema.</div>' +
      '<div class="sr-options" data-group="rubro">';
    RUBROS.forEach(function (r) {
      html += optCard('rubro', r.id, r.label, r.icon, state.rubro === r.id);
    });
    html += '</div>';
    return html;
  },
  categoria: function () {
    var tree = JOB_TREE[state.rubro];
    var html = '<div class="sr-step-title">¿Qué necesitás?</div>' +
      '<div class="sr-step-sub">' + RUBRO_LABELS[state.rubro] + ' &middot; elegí una opción</div>' +
      '<div class="sr-options" data-group="categoria">';
    tree.categorias.forEach(function (c) {
      html += optCard('categoria', c.id, c.label, c.icon, state.categoria === c.id);
    });
    html += optCard('categoria', '__manual__', 'Otro / no lo encuentro', 'dots', state.categoria === '__manual__');
    html += '</div>';
    if (state.categoria === '__manual__') {
      html += '<div class="sr-field" style="margin-top:14px"><label for="srCategoriaManual">Contanos qué necesitás</label>' +
        '<textarea class="sr-textarea" id="srCategoriaManual" placeholder="Ej: se me rompió la cañería del patio y pierde agua...">' + escapeHtml(state.descripcion) + '</textarea></div>';
    }
    return html;
  },
  detalle: function () {
    var opts = JOB_TREE[state.rubro].detalles[state.categoria] || [];
    var html = '<div class="sr-step-title">Un poco más de detalle</div>' +
      '<div class="sr-step-sub">Así calculamos un estimado más preciso.</div>' +
      '<div class="sr-options sr-options-1col" data-group="detalle">';
    opts.forEach(function (o) {
      var note = o.urgente ? 'Puede haber recargo por urgencia' : fmtPrice(o.price[0]) + ' – ' + fmtPrice(o.price[1]);
      html += optRow('detalle', o.id, o.label, note, state.detalle === o.id);
    });
    html += optRow('detalle', '__manual__', 'Otro / no lo encuentro', 'Contanos con tus palabras', state.detalle === '__manual__');
    html += '</div>';
    if (state.detalle === '__manual__') {
      html += '<div class="sr-field" style="margin-top:14px"><label for="srDetalleManual">Contanos más</label>' +
        '<textarea class="sr-textarea" id="srDetalleManual" placeholder="Describí el trabajo que necesitás...">' + escapeHtml(state.descripcion) + '</textarea></div>';
    }
    return html;
  },
  ubicacion: function () {
    var html = '<div class="sr-step-title">¿Dónde es el trabajo?</div>' +
      '<div class="sr-step-sub">Buscamos profesionales cerca de tu zona.</div>' +
      '<div class="sr-field"><select class="sr-select" id="srUbicacionSelect">' +
      '<option value="" disabled ' + (!state.ubicacion ? 'selected' : '') + '>Elegí tu ubicación</option>';
    UBICACIONES.forEach(function (u) {
      html += '<option value="' + u + '"' + (state.ubicacion === u ? ' selected' : '') + '>' + u + '</option>';
    });
    html += '</select></div>';
    return html;
  },
  estimate: function () {
    var detalleObj = getDetalleObj();
    var isManual = !detalleObj;
    var price = detalleObj ? detalleObj.price : null;
    var urgente = detalleObj && detalleObj.urgente;
    var trabajoLabel = detalleObj ? detalleObj.label : 'A confirmar con el profesional';
    var html = '<div class="sr-step-title">Tu estimado</div>' +
      '<div class="sr-step-sub">' + (isManual
        ? 'Nos contaste el trabajo con tus palabras: un profesional confirma el precio.'
        : 'Precio de referencia según valores 2026 de mano de obra en CABA/GBA.') + '</div>';
    if (isManual) {
      html += '<div class="sr-estimate-card">' +
          '<div class="sr-estimate-label">Sin estimado de referencia</div>' +
          '<div class="sr-estimate-note" style="opacity:1;font-size:.92rem">Como el trabajo no está en nuestra lista, el profesional revisa el detalle y te confirma el precio.</div>' +
        '</div>';
    } else {
      html += '<div class="sr-estimate-card">' +
          '<div class="sr-estimate-label">Rango estimado</div>' +
          '<div class="sr-estimate-price">' + fmtPrice(price[0]) + ' &ndash; ' + fmtPrice(price[1]) + '</div>' +
          '<div class="sr-estimate-note">Orientativo. El profesional confirma el precio final tras ver el trabajo.</div>' +
        '</div>';
    }
    html += '<div class="sr-time-row">' + ic('check', 18) + '<span>' + (urgente ? TIEMPO_URGENTE : TIEMPO_NORMAL) + '</span></div>' +
      '<div class="sr-summary">' +
        summaryRow('Rubro', RUBRO_LABELS[state.rubro], presetRubro ? null : 'rubro') +
        summaryRow('Trabajo', trabajoLabel, presetDetalle ? null : (state.categoria === '__manual__' ? 'categoria' : 'detalle')) +
        summaryRow('Ubicación', state.ubicacion, presetUbicacion ? null : 'ubicacion') +
      '</div>' +
      '<div class="sr-field"><label for="srDescripcion">Contanos más' + (isManual ? '' : ' (opcional)') + '</label>' +
      '<textarea class="sr-textarea" id="srDescripcion" placeholder="Ej: el corte pasa solo cuando prendo el microondas...">' + escapeHtml(state.descripcion) + '</textarea></div>';
    return html;
  },
  contacto: function () {
    var html = '<div class="sr-step-title">Último paso</div>' +
      '<div class="sr-step-sub">' + (state.isDirect ? 'Para que ' + (state.nombreProfesional || 'el profesional') + ' te contacte por WhatsApp.' : 'Para que los profesionales te contacten por WhatsApp.') + '</div>' +
      '<div class="sr-field"><label for="srNombre">Tu nombre</label>' +
      '<input class="sr-input" type="text" id="srNombre" placeholder="Nombre y apellido" value="' + escapeHtml(state.nombre) + '" /></div>' +
      '<div class="sr-field"><label for="srTelefono">WhatsApp</label>' +
      '<input class="sr-input" type="tel" id="srTelefono" placeholder="11 1234 5678" value="' + escapeHtml(state.telefono) + '" />' +
      '<div class="sr-hint">Solo lo va' + (state.isDirect ? '' : 'n') + ' a usar para contactarte por este trabajo.</div></div>';
    return html;
  },
  success: function () {
    var msg = state.isDirect
      ? 'Tu solicitud va a llegar directo a <strong>' + escapeHtml(state.nombreProfesional || 'este profesional') + '</strong> por WhatsApp.'
      : 'Vas a recibir hasta <strong>3 presupuestos por WhatsApp</strong> de profesionales verificados de tu zona.';
    var waUrl = window._hogarexWhatsappUrl || '#';
    return '<div class="sr-success">' +
      '<div class="sr-success-icon">' + ic('check', 32) + '</div>' +
      '<h2>¡Ya casi, ' + escapeHtml(state.nombre || '') + '!</h2>' +
      '<p>Preparamos tu solicitud de <strong>' + RUBRO_LABELS[state.rubro] + '</strong> en <strong>' + escapeHtml(state.ubicacion) + '</strong> y abrimos WhatsApp con todo cargado.</p>' +
      '<p>Si no se abrió solo, tocá el botón de abajo y confirmá el envío desde WhatsApp.</p>' +
      '<p>' + msg + '</p>' +
      '<p>' + ((getDetalleObj() || {}).urgente ? TIEMPO_URGENTE : TIEMPO_NORMAL) + '</p>' +
      '</div>' +
      '<div class="sr-footer" style="border-top:none;padding-top:4px;flex-direction:column;gap:10px">' +
      '<a class="sr-btn sr-btn-whatsapp" href="' + waUrl + '" target="_blank" rel="noopener">' +
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm5.8 14.14c-.24.68-1.4 1.32-1.93 1.38-.5.06-1.03.28-3.42-.71-2.9-1.2-4.76-4.15-4.9-4.34-.14-.19-1.16-1.55-1.16-2.95 0-1.4.73-2.09.99-2.37.26-.28.57-.35.76-.35.19 0 .38 0 .55.01.18.01.42-.07.65.5.24.58.82 2 .89 2.14.07.14.12.31.02.5-.1.19-.15.3-.29.47-.14.16-.3.36-.43.48-.14.14-.29.29-.13.57.17.28.75 1.24 1.62 2.01 1.11.99 2.05 1.3 2.33 1.44.28.14.44.12.6-.07.17-.19.71-.83.9-1.11.19-.28.38-.24.64-.14.26.1 1.68.79 1.97.94.28.14.47.21.54.33.07.12.07.68-.18 1.35z"/></svg>' +
        'Confirmar por WhatsApp' +
      '</a>' +
      '<button type="button" class="sr-btn sr-btn-outline" style="width:100%" onclick="closeWizard()">Volver al inicio</button>' +
      '</div>';
  }
};

function optCard(group, id, label, iconName, selected) {
  return '<button type="button" class="sr-opt' + (selected ? ' selected' : '') + '" data-group="' + group + '" data-id="' + id + '">' +
    '<span class="sr-opt-icon">' + ic(iconName, 18) + '</span>' +
    '<span class="sr-opt-label">' + escapeHtml(label) + '</span>' +
    '</button>';
}
function optRow(group, id, label, note, selected) {
  return '<button type="button" class="sr-opt sr-opt-row' + (selected ? ' selected' : '') + '" data-group="' + group + '" data-id="' + id + '">' +
    '<span class="sr-opt-icon">' + ic('dots', 16) + '</span>' +
    '<span style="flex:1"><span class="sr-opt-label" style="display:block">' + escapeHtml(label) + '</span>' +
    '<span class="sr-opt-note">' + note + '</span></span>' +
    '</button>';
}
function summaryRow(label, value, editTarget) {
  var editBtn = editTarget ? ' <button type="button" class="sr-summary-edit" data-edit="' + editTarget + '">Cambiar</button>' : '';
  return '<div class="sr-summary-row"><span>' + label + '</span><span>' + escapeHtml(value || '') + editBtn + '</span></div>';
}
function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}

function bindStepEvents(id) {
  if (id === 'rubro' || id === 'categoria' || id === 'detalle') {
    var opts = srBody.querySelectorAll('.sr-opt');
    opts.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var group = btn.getAttribute('data-group');
        var val = btn.getAttribute('data-id');
        if (group === 'rubro') { state.rubro = val; state.categoria = ''; state.detalle = ''; }
        if (group === 'categoria') { state.categoria = val; state.detalle = ''; buildSteps(); }
        if (group === 'detalle') { state.detalle = val; }
        opts.forEach(function (b) { b.classList.remove('selected'); });
        btn.classList.add('selected');
        validateStep();
        /* La opción manual necesita que el usuario escriba antes de avanzar:
           re-renderizamos el paso para mostrar el textarea, sin auto-avance. */
        if (val === '__manual__') {
          renderStep();
        } else {
          selectAndAdvance();
        }
      });
    });
    var catManual = document.getElementById('srCategoriaManual');
    if (catManual) catManual.addEventListener('input', function () { state.descripcion = catManual.value; validateStep(); });
    var detManual = document.getElementById('srDetalleManual');
    if (detManual) detManual.addEventListener('input', function () { state.descripcion = detManual.value; validateStep(); });
  } else if (id === 'ubicacion') {
    var sel = document.getElementById('srUbicacionSelect');
    sel.addEventListener('change', function () { state.ubicacion = sel.value; validateStep(); });
  } else if (id === 'estimate') {
    var ta = document.getElementById('srDescripcion');
    ta.addEventListener('input', function () { state.descripcion = ta.value; });
    srBody.querySelectorAll('[data-edit]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var idx = STEP_ORDER.indexOf(btn.getAttribute('data-edit'));
        if (idx === -1) return;
        stepIndex = idx;
        renderStep();
      });
    });
  } else if (id === 'contacto') {
    var nombre = document.getElementById('srNombre');
    var tel = document.getElementById('srTelefono');
    nombre.addEventListener('input', function () { state.nombre = nombre.value; validateStep(); });
    tel.addEventListener('input', function () { state.telefono = tel.value; validateStep(); });
  }
}

/* ============================================================
   Envío. TODO: reemplazar por integración real con Bubble
   (API workflow que reciba este payload y notifique por WhatsApp
   a los profesionales correspondientes). Por ahora solo arma el
   payload estructurado y muestra la confirmación local.
   ============================================================ */
function buildPayload() {
  var detalleObj = getDetalleObj();
  return {
    tipo: state.isDirect ? 'directa' : 'general',
    trader_uid: state.trader || null,
    nombre_profesional: state.nombreProfesional || null,
    rubro: state.rubro,
    categoria: state.categoria,
    detalle: state.detalle,
    detalle_label: detalleObj ? detalleObj.label : (state.categoria === '__manual__' || state.detalle === '__manual__' ? 'Otro (ver descripción)' : ''),
    estimado_min: detalleObj ? detalleObj.price[0] : null,
    estimado_max: detalleObj ? detalleObj.price[1] : null,
    urgente: !!(detalleObj && detalleObj.urgente),
    ubicacion: state.ubicacion,
    descripcion: state.descripcion,
    nombre_cliente: state.nombre,
    telefono_cliente: state.telefono,
    origen: window.location.href
  };
}
var HOGAREX_WHATSAPP = '5491121820841';
function buildWhatsAppMessage(payload) {
  var lines = ['Nueva solicitud de presupuesto - Hogarex', ''];
  lines.push('Tipo: ' + (payload.tipo === 'directa'
    ? 'Directa a ' + (payload.nombre_profesional || 'un profesional')
    : 'General (hasta 3 profesionales)'));
  lines.push('Rubro: ' + (RUBRO_LABELS[payload.rubro] || payload.rubro));
  if (payload.detalle_label) lines.push('Trabajo: ' + payload.detalle_label);
  if (payload.estimado_min && payload.estimado_max) {
    lines.push('Estimado de referencia: ' + fmtPrice(payload.estimado_min) + ' - ' + fmtPrice(payload.estimado_max));
  }
  lines.push('Ubicación: ' + payload.ubicacion);
  if (payload.urgente) lines.push('Urgencia: Sí');
  if (payload.descripcion) lines.push('Descripción: ' + payload.descripcion);
  lines.push('');
  lines.push('Cliente: ' + payload.nombre_cliente);
  lines.push('WhatsApp del cliente: ' + payload.telefono_cliente);
  if (payload.tipo === 'directa' && payload.trader_uid) {
    lines.push('ID del profesional solicitado: ' + payload.trader_uid);
  }
  return lines.join('\n');
}
function whatsappUrl(message) {
  return 'https://wa.me/' + HOGAREX_WHATSAPP + '?text=' + encodeURIComponent(message);
}
function submitSolicitud() {
  var payload = buildPayload();
  window._hogarexUltimaSolicitud = payload;
  var waUrl = whatsappUrl(buildWhatsAppMessage(payload));
  window._hogarexWhatsappUrl = waUrl;
  window.open(waUrl, '_blank', 'noopener');
  stepIndex = STEP_ORDER.indexOf('success');
  renderStep();
}

/* Si llega con rubro/trader por query string, abrir el wizard automáticamente */
if (presetRubro || presetTrader) {
  window.addEventListener('DOMContentLoaded', function () {
    openWizard();
  });
}


    window.openWizard = openWizard;
    window.closeWizard = closeWizard;
    window.openWizardFresh = openWizardFresh;
    window.openWizardForTask = openWizardForTask;
    window.openWizardWithRubro = openWizardWithRubro;
    /* Expuestos para que páginas con lógica propia (ej. el formulario del
       hero en index.html) puedan chequear si un rubro tiene datos de
       precio antes de decidir si abren el wizard acá o redirigen, sin
       tener que mantener su propia copia de estos datos. */
    window.HGX_JOB_TREE = JOB_TREE;
    window.hgxNormalizeRubro = normalizeRubro;
    /* Punto de entrada único para todos los botones "Pedir presupuesto"
       del sitio (tarjetas de profesionales, CTAs de rubro/ubicación,
       barra fija de perfil, etc.): si el rubro tiene datos de precio
       en el wizard lo abre directo ahí con la ubicación ya cargada; si
       no (rubro no cubierto, o sin datos), abre el wizard genérico
       desde el principio en vez de redirigir a otra página. */
    function openBudget(rubroLabel, ubicacion) {
      var norm = rubroLabel ? normalizeRubro(rubroLabel) : '';
      if (norm && JOB_TREE[norm]) {
        openWizardWithRubro(norm, ubicacion || '');
      } else {
        openWizardFresh();
      }
    }
    window.hgxOpenBudget = openBudget;
  }

  if (!document.getElementById('srPopup') && !window.HGX_NO_POPUP) {
    injectStyle("\n.sr-popup { position: fixed; bottom: 16px; right: 16px; left: 16px; max-width: 360px; margin-left: auto; background: #fff; border-radius: 16px; box-shadow: 0 12px 40px rgba(13,42,94,0.25); padding: 16px; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; z-index: 500; transform: translateY(24px); opacity: 0; visibility: hidden; transition: transform .3s ease, opacity .3s ease, visibility .3s; font-family: 'Inter', -apple-system, sans-serif; }\n.sr-popup.show { transform: translateY(0); opacity: 1; visibility: visible; }\n.sr-popup-close { position: absolute; top: 8px; right: 10px; background: none; border: none; font-size: 18px; line-height: 1; color: #6b7280; cursor: pointer; padding: 4px; }\n.sr-popup-icon { width: 36px; height: 36px; border-radius: 50%; background: #25D366; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }\n.sr-popup-body { flex: 1; min-width: 180px; }\n.sr-popup-body strong { display: block; font-family: 'Sora', sans-serif; font-size: 0.88rem; color: #003366; margin-bottom: 2px; }\n.sr-popup-body span { display: block; font-size: 0.78rem; color: #6b7280; line-height: 1.4; }\n.sr-popup-btn { width: 100%; text-align: center; background: #F5C518; color: #003366; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 0.85rem; padding: 10px; border-radius: 999px; text-decoration: none; border: none; cursor: pointer; }\n@media (min-width: 480px) { .sr-popup-btn { width: auto; } }\n");
    document.body.insertAdjacentHTML('beforeend', "<div class=\"sr-popup\" id=\"srPopup\">\n  <button type=\"button\" class=\"sr-popup-close\" id=\"srPopupClose\" aria-label=\"Cerrar\">&times;</button>\n  <div class=\"sr-popup-icon\">\n    <svg width=\"20\" height=\"20\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#fff\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z\"/></svg>\n  </div>\n  <div class=\"sr-popup-body\">\n    <strong>\u00bfNecesit\u00e1s un profesional?</strong>\n    <span>Envi\u00e1 tu solicitud gratis y recib\u00ed hasta 3 presupuestos por WhatsApp.</span>\n  </div>\n  <button type=\"button\" class=\"sr-popup-btn\" id=\"srPopupBtn\">Enviar solicitud</button>\n</div>");

    var KEY = 'hgx_sr_popup_dismissed';
    var popup = document.getElementById('srPopup');
    var closeBtn = document.getElementById('srPopupClose');
    var btn = document.getElementById('srPopupBtn');
    var shown = false;

    function showPopup() {
      if (shown) return;
      try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}
      shown = true;
      popup.classList.add('show');
    }
    function dismissPopup() {
      popup.classList.remove('show');
      try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
    }
    closeBtn.addEventListener('click', dismissPopup);
    btn.addEventListener('click', function () {
      dismissPopup();
      if (typeof window.openWizardFresh === 'function') {
        window.openWizardFresh();
      } else if (typeof window.openWizard === 'function') {
        window.openWizard();
      } else {
        window.location.href = 'https://hogarex.ar/solicitud-enviar';
      }
    });

    var initTimer = setTimeout(showPopup, 2000);
    window.addEventListener('scroll', function () {
      var max = document.body.scrollHeight - window.innerHeight;
      var scrolled = max > 0 ? window.scrollY / max : 0;
      if (scrolled > 0.4) showPopup();
    }, { passive: true });
  }
})();