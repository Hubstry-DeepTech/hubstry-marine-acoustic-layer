import * as Plot from "@observablehq/plot";
import "@fontsource/spectral/400.css";
import "@fontsource/spectral/600.css";
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "./style.css";

// ---------------------------------------------------------------------------------------------
// Tipos dos dados gerados por site/build_data.py
// ---------------------------------------------------------------------------------------------
type Mode = "hf" | "lf";
interface FileRef { path: string; sha256: string; url: string }
interface Provenance {
  set: string; execution_type: "github_actions" | "manual_vm"; execution_run_id: number | null;
  execution_url: string | null; experiment_commit: string; experiment_commit_url: string;
  experiment_commit_basis: string; publication_commit: string; files: FileRef[]; note: string | null;
}
interface BenchSet {
  id: string; receiver: string; criteria_version: string; matrix_version: string; date_utc: string; definitive: boolean;
  aggregate: { status: "trl3" | "trl4" | "inconsistent" | "incomplete" | "not_definitive"; rule: string;
               by_test_and_mode: Record<string, Record<Mode, boolean | null>> };
  per_mode_assessment: Record<Mode, string | undefined>;
  per_mode_results: Record<Mode, Record<string, boolean>>;
  snr_int_db: number[];
  b3_recovery_rate: Record<Mode, Record<string, number[]>>;
  b3_k1_rms_over_acrb: Record<Mode, number[]>;
  b4_min_recovery: Record<Mode, Record<string, number>>;
  b7: Record<Mode, { fpr: number; cp_upper_95: number; midpoints_rejected: number; midpoints_total: number }>;
  provenance: Provenance;
}
interface E1Day {
  day: string; computed_ci: number; reference_ci: number; relative_difference: number; valid_minutes: number;
  minutes: number; passed: boolean; wav_sha256: string; wav_key: string;
  series: { minute: number[]; ci: (number | null)[]; valid: boolean[] }; spectrogram: string; spectrogram_original: string;
}
interface SiteData {
  publication_commit: string; publication_commit_url: string; built_from_branch: string; repo_url: string;
  documents: { bench_criteria: string; preregistration_version: string; preregistration_status: string };
  bench: BenchSet[];
  e1: { passed: boolean; tolerance_relative: number; date_utc: string; source: string; license: string;
        env: Record<string, string>; days: E1Day[]; series_note: string; provenance: Provenance };
  reports: Record<string, { sha256: string; url: string }>;
}

// ---------------------------------------------------------------------------------------------
// utilidades
// ---------------------------------------------------------------------------------------------
const $ = (id: string) => document.getElementById(id)!;
const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
const nf = (x: number, d = 3) => x.toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d });
const pct = (x: number, d = 1) => `${(100 * x).toLocaleString("pt-BR", { maximumFractionDigits: d, minimumFractionDigits: d })}%`;
const short = (h: string) => h.slice(0, 7);
const dateBR = (iso: string) => new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short", timeZone: "UTC" }) + " UTC";
const css = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

const RUN_LABEL: Record<string, string> = {
  "v1-run41120505952": "Receptor v1",
  "v2-run41121711705": "Receptor v2, 1ª execução",
  "v2-run41131667005": "Receptor v2, 2ª execução (com dados por ensaio)",
};
const COND_LABEL: Record<string, string> = {
  k1: "1 canal", k2: "2 canais", k3: "3 canais", worst_pair_0: "par mais próximo (1/16 e 1/15)", worst_pair_1: "par mais próximo (14/15 e 15/16)",
};
const MODE_LABEL: Record<Mode, string> = { hf: "alta frequência (hf)", lf: "baixa frequência (lf)" };
const TEST_LABEL: Record<string, string> = {
  B1: "B1 dicionário", B2: "B2 precisão sem ruído", B3: "B3 recuperação com ruído", B4: "B4 desvio de escala com piloto",
  B5: "B5 periodicidade", B7: "B7 falsos alarmes e tons fora do dicionário",
};

function statusBadge(b: BenchSet): string {
  const a = b.aggregate;
  const map: Record<string, [string, string]> = {
    trl3: ["fail", `TRL 3 sob os critérios ${b.criteria_version}`],
    trl4: ["pass", `TRL 4 sob os critérios ${b.criteria_version} (autoavaliação do subsistema)`],
    inconsistent: ["warn", "Inconsistente: o agregador não emite conclusão conjunta"],
    incomplete: ["warn", "Incompleto: o agregador não emite conclusão"],
    not_definitive: ["warn", "Não definitivo: sem conclusão de maturidade"],
  };
  const [cls, text] = map[a.status];
  return `<span class="badge ${cls}">${esc(text)}</span>`;
}

function verdict(v: boolean | null | undefined): string {
  if (v === true) return `<span class="v pass">aprovado</span>`;
  if (v === false) return `<span class="v fail">reprovado</span>`;
  return `<span class="v warn">ausente</span>`;
}

function provenanceBlock(p: Provenance, title = "Proveniência"): string {
  const exec = p.execution_type === "github_actions"
    ? `GitHub Actions, execução <a href="${p.execution_url}">${p.execution_run_id}</a>`
    : "execução manual numa máquina virtual, sem workflow associado";
  const files = p.files.map((f) => `<li><a href="${f.url}">${esc(f.path)}</a> <span class="hash" title="SHA-256 ${f.sha256}">${f.sha256.slice(0, 12)}…</span></li>`).join("");
  return `<details class="prov"><summary>${title}</summary>
    <dl>
      <dt>Execução</dt><dd>${exec}</dd>
      <dt>Código executado</dt><dd>commit <a href="${p.experiment_commit_url}">${short(p.experiment_commit)}</a>. ${esc(p.experiment_commit_basis)}.</dd>
      <dt>Publicação</dt><dd>commit ${short(p.publication_commit)} do ramo principal</dd>
      ${p.note ? `<dt>Observação</dt><dd>${esc(p.note)}</dd>` : ""}
    </dl>
    <p class="small">Arquivos e prefixo do SHA-256 conferido no build:</p>
    <ul class="files">${files}</ul>
  </details>`;
}

function dataTable(caption: string, head: string[], rows: (string | number)[][]): string {
  return `<details class="datatable"><summary>Tabela com os dados do gráfico</summary>
    <div class="table-wrap"><table><caption>${esc(caption)}</caption>
    <thead><tr>${head.map((h) => `<th scope="col">${esc(h)}</th>`).join("")}</tr></thead>
    <tbody>${rows.map((r) => `<tr>${r.map((c, i) => (i === 0 ? `<th scope="row">${c}</th>` : `<td>${c}</td>`)).join("")}</tr>`).join("")}</tbody>
    </table></div></details>`;
}

// ---------------------------------------------------------------------------------------------
// Régua harmônica (H_16)
// ---------------------------------------------------------------------------------------------
function gcd(a: number, b: number): number { return b ? gcd(b, a % b) : a; }

function drawRuler(): void {
  const el = $("ruler");
  const W = 1000, H = 130, pad = 14, base = H - 2;
  const ratios: { a: number; b: number; r: number }[] = [];
  for (let a = 1; a <= 16; a++) for (let b = 1; b <= 16; b++) if (gcd(a, b) === 1) ratios.push({ a, b, r: a / b });
  const L = Math.log(16);
  const x = (r: number) => pad + ((Math.log(r) + L) / (2 * L)) * (W - 2 * pad);
  const maxT = Math.log2(16 * 15);
  const ticks = ratios.map(({ a, b, r }) => {
    const t = Math.log2(a * b) / maxT; // complexidade de Tenney normalizada
    const h = 10 + (1 - t) * (base - 16);
    const cls = a * b <= 6 ? "simple" : "";
    return `<line class="${cls}" x1="${x(r).toFixed(2)}" x2="${x(r).toFixed(2)}" y1="${base}" y2="${(base - h).toFixed(2)}"><title>${a}/${b}</title></line>`;
  }).join("");
  // rótulos em HTML, posicionados em porcentagem, para não deformar com a largura da tela
  const narrow = window.matchMedia("(max-width: 600px)").matches;
  const marks = narrow ? [[1, 16], [1, 2], [1, 1], [2, 1], [16, 1]] : [[1, 16], [1, 4], [1, 2], [1, 1], [3, 2], [2, 1], [4, 1], [16, 1]];
  const labels = marks.map(([a, b]) => `<span style="left:${((x(a / b) / W) * 100).toFixed(2)}%">${a}/${b}</span>`).join("");
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">
    <line class="axis" x1="${pad}" x2="${W - pad}" y1="${base}" y2="${base}"></line>${ticks}</svg>
    <div class="ruler-labels" aria-hidden="true">${labels}</div>`;
}

// ---------------------------------------------------------------------------------------------
// Bancada
// ---------------------------------------------------------------------------------------------
let selectedRun = "v2-run41131667005";

function renderRuns(d: SiteData): void {
  const rows = d.bench.map((b) => {
    const modes = (["hf", "lf"] as Mode[]).map((m) => b.per_mode_assessment[m]).filter(Boolean);
    const perMode = b.aggregate.status === "inconsistent" && modes.length
      ? `<p class="small">Avaliação a partir dos vereditos de cada modo, registrada em summary.json: ${esc(modes[0]!.split(":")[0])} nos dois modos. Não é uma conclusão do agregador.</p>` : "";
    return `<tr>
      <th scope="row">${esc(RUN_LABEL[b.id] ?? b.id)}<br><span class="small">${dateBR(b.date_utc)}</span></th>
      <td>${b.criteria_version}<br><span class="small">matriz ${b.matrix_version}</span></td>
      <td>${statusBadge(b)}${perMode}</td>
    </tr>`;
  }).join("");
  const tests = Object.keys(d.bench[0].aggregate.by_test_and_mode);
  const head = d.bench.map((b) => `<th scope="col" colspan="2">${esc(RUN_LABEL[b.id] ?? b.id)}</th>`).join("");
  const sub = d.bench.map(() => `<th scope="col">hf</th><th scope="col">lf</th>`).join("");
  const body = tests.map((t) => `<tr><th scope="row">${esc(TEST_LABEL[t] ?? t)}</th>${d.bench.map((b) =>
    (["hf", "lf"] as Mode[]).map((m) => `<td>${verdict(b.aggregate.by_test_and_mode[t][m])}</td>`).join("")).join("")}</tr>`).join("");

  $("bench-runs").innerHTML = `
    <h3>Execuções definitivas sob os critérios v0.3.1</h3>
    <div class="table-wrap"><table class="runs">
      <thead><tr><th scope="col">Execução</th><th scope="col">Critérios</th><th scope="col">Status do agregador</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
    <h3>Veredito por ensaio e modo</h3>
    <div class="table-wrap"><table class="matrix">
      <thead><tr><th scope="col" rowspan="2">Ensaio</th>${head}</tr><tr>${sub}</tr></thead>
      <tbody>${body}</tbody></table></div>
    <p class="note">As duas execuções da v2 reprovam só no B3, pelo critério (c): erro de frequência até 1,5 vez o limite teórico a partir de 16 dB. Perto desse nível, uma única troca de canal em mil ensaios eleva o erro médio a milhares de vezes o limite. A v1 recupera melhor com pouco sinal, mas reprova no B4 e no B7. O <a href="${d.reports["REPORT_v1_v2.md"]?.url ?? "#"}">relatório comparativo</a> detalha os números.</p>`;
}

function renderDetail(d: SiteData): void {
  const b = d.bench.find((x) => x.id === selectedRun)!;
  const v1 = d.bench.find((x) => x.receiver === "v1");
  const opts = d.bench.map((x) => `<label><input type="radio" name="run" value="${x.id}" ${x.id === selectedRun ? "checked" : ""}> ${esc(RUN_LABEL[x.id] ?? x.id)}</label>`).join("");
  $("bench-detail").innerHTML = `
    <h3>Recuperação dos canais com ruído (B3)</h3>
    <fieldset class="picker"><legend>Execução exibida nos gráficos</legend>${opts}</fieldset>
    <p class="intro">Fração dos mil ensaios por condição em que o receptor recuperou exatamente os canais transmitidos, em função da razão sinal-ruído integrada. A aprovação exige ao menos 99% a partir de 20 dB.</p>
    <div id="chart-recovery" class="chart"></div>
    ${dataTable("Taxa de recuperação por SNR integrada (dB)", ["SNR (dB)", ...(["hf", "lf"] as Mode[]).flatMap((m) => Object.keys(b.b3_recovery_rate[m]).map((c) => `${m} ${COND_LABEL[c] ?? c}`))],
      b.snr_int_db.map((s, i) => [s, ...(["hf", "lf"] as Mode[]).flatMap((m) => Object.values(b.b3_recovery_rate[m]).map((r) => pct(r[i])))]))}
    <h3>Erro de frequência com um canal, relativo ao limite teórico</h3>
    <p class="intro">Erro quadrático médio (RMS) dividido pelo limite de Cramér–Rao assintótico (ACRB), em escala logarítmica. O critério B3(c) da v0.3.1 exige até 1,5 a partir de 16 dB. Os saltos para milhares refletem trocas de canal, não imprecisão local.</p>
    <div id="chart-rms" class="chart"></div>
    ${dataTable("RMS/ACRB com um canal", ["SNR (dB)", "hf", "lf"], b.snr_int_db.map((s, i) => [s, nf(b.b3_k1_rms_over_acrb.hf[i], 2), nf(b.b3_k1_rms_over_acrb.lf[i], 2)]))}
    ${v1 && b.receiver !== "v1" ? `<h3>Perto do limiar: v1 e ${esc(RUN_LABEL[b.id] ?? b.id)}</h3>
    <p class="intro">Recuperação com um canal entre 8 e 22 dB. ${errorsAt(v1, 16)} ${errorsAt(b, 16)}</p>
    <div id="chart-compare" class="chart"></div>` : ""}
    <h3>Desvio de escala (B4) e falsos alarmes (B7)</h3>
    <div class="table-wrap"><table>
      <thead><tr><th scope="col">Execução</th><th scope="col">B4, menor recuperação (hf / lf)</th><th scope="col">B7, limite superior de falsos alarmes a 95% (hf / lf)</th><th scope="col">B7, tons entre canais rejeitados (hf / lf)</th></tr></thead>
      <tbody>${d.bench.map((x) => `<tr><th scope="row">${esc(RUN_LABEL[x.id] ?? x.id)}</th>
        <td>${pct(Math.min(...Object.values(x.b4_min_recovery.hf)))} / ${pct(Math.min(...Object.values(x.b4_min_recovery.lf)))}</td>
        <td>${pct(x.b7.hf.cp_upper_95, 2)} / ${pct(x.b7.lf.cp_upper_95, 2)}</td>
        <td>${x.b7.hf.midpoints_rejected} de ${x.b7.hf.midpoints_total} / ${x.b7.lf.midpoints_rejected} de ${x.b7.lf.midpoints_total}</td></tr>`).join("")}</tbody>
    </table></div>
    <p class="small">B4 exige ao menos 99% de recuperação; B7 exige limite superior até 1% e rejeição dos 158 tons colocados entre canais vizinhos.</p>
    ${provenanceBlock(b.provenance, `Proveniência: ${RUN_LABEL[b.id] ?? b.id}`)}
    <p class="small">Agregador, texto integral: ${esc(b.aggregate.rule)}</p>`;
  document.querySelectorAll<HTMLInputElement>('input[name="run"]').forEach((r) =>
    r.addEventListener("change", () => { selectedRun = r.value; renderDetail(d); drawBenchCharts(d); document.getElementById("chart-recovery")?.scrollIntoView({ block: "nearest" }); }));
  drawBenchCharts(d);
}

function errorsAt(b: BenchSet, snr: number): string {
  const i = b.snr_int_db.indexOf(snr);
  const n = (["hf", "lf"] as Mode[]).map((m) => Math.round((1 - b.b3_recovery_rate[m].k1[i]) * 1000));
  return `${b.receiver === "v1" ? "A v1" : "A v2"} falha ${n[0]} vezes em mil (hf) e ${n[1]} (lf) a ${snr} dB.`;
}

function condColors(): string[] { return [1, 2, 3, 4, 5].map((i) => css(`--c${i}`)); }

function drawBenchCharts(d: SiteData): void {
  const b = d.bench.find((x) => x.id === selectedRun)!;
  const ink = css("--ink"), muted = css("--muted"), line = css("--line");
  const font = "IBM Plex Sans, system-ui, sans-serif";
  const conds = Object.keys(b.b3_recovery_rate.hf);
  const rec = (["hf", "lf"] as Mode[]).flatMap((m) => conds.flatMap((c) =>
    b.snr_int_db.map((s, i) => ({ modo: MODE_LABEL[m], cond: COND_LABEL[c] ?? c, snr: s, r: b.b3_recovery_rate[m][c][i] }))));
  const width = Math.min(($("bench-detail").clientWidth || 800), 960);
  const common = { width, style: { fontFamily: font, fontSize: "13px", color: ink, background: "transparent" }, marginLeft: 52, marginBottom: 44 };
  $("chart-recovery").replaceChildren(Plot.plot({
    ...common, height: width < 600 ? 520 : 300,
    fx: width < 600 ? undefined : { label: null }, fy: width < 600 ? { label: null } : undefined,
    x: { label: "SNR integrada (dB)", grid: true, labelAnchor: "center", labelOffset: 38, labelArrow: "none" }, y: { label: "Recuperação exata", domain: [0, 1], tickFormat: "%", grid: true },
    color: { legend: true, domain: conds.map((c) => COND_LABEL[c] ?? c), range: condColors() },
    marks: [
      Plot.ruleY([0.99], { stroke: muted, strokeDasharray: "4,3" }),
      Plot.ruleX([20], { stroke: muted, strokeDasharray: "4,3" }),
      Plot.line(rec, { x: "snr", y: "r", stroke: "cond", strokeWidth: 1.6, ...(width < 600 ? { fy: "modo" } : { fx: "modo" }) }),
      Plot.frame({ stroke: line }),
    ],
  }));
  const rms = (["hf", "lf"] as Mode[]).flatMap((m) => b.snr_int_db.map((s, i) => ({ modo: MODE_LABEL[m], snr: s, v: b.b3_k1_rms_over_acrb[m][i] })));
  $("chart-rms").replaceChildren(Plot.plot({
    ...common, height: 300,
    x: { label: "SNR integrada (dB)", grid: true, labelAnchor: "center", labelOffset: 38, labelArrow: "none" }, y: { type: "log", label: "RMS / ACRB", grid: true, domain: [0.8, Math.max(...rms.map((r) => r.v)) * 1.3] },
    color: { legend: true, domain: Object.values(MODE_LABEL), range: [css("--c1"), css("--c4")] },
    marks: [
      Plot.ruleY([1.5], { stroke: muted, strokeDasharray: "4,3" }),
      Plot.ruleX([16], { stroke: muted, strokeDasharray: "4,3" }),
      Plot.text([{ x: 16, y: 1.5 }], { x: "x", y: "y", text: () => "limite do critério (1,5) a partir de 16 dB", dx: 6, dy: -8, textAnchor: "start", fill: muted }),
      Plot.line(rms, { x: "snr", y: "v", stroke: "modo", strokeWidth: 1.6 }),
      Plot.dot(rms, { x: "snr", y: "v", fill: "modo", r: 2.2 }),
      Plot.frame({ stroke: line }),
    ],
  }));
  const v1 = d.bench.find((x) => x.receiver === "v1");
  const cmp = document.getElementById("chart-compare");
  if (v1 && cmp) {
    const rows = [v1, b].flatMap((x) => (["hf", "lf"] as Mode[]).flatMap((m) => x.snr_int_db.map((s, i) => ({
      serie: `${x.receiver} ${m}`, snr: s, r: x.b3_recovery_rate[m].k1[i] })).filter((p) => p.snr >= 8 && p.snr <= 22)));
    cmp.replaceChildren(Plot.plot({
      ...common, height: 280,
      x: { label: "SNR integrada (dB)", grid: true, labelAnchor: "center", labelOffset: 38, labelArrow: "none" }, y: { label: "Recuperação exata, 1 canal", domain: [0, 1], tickFormat: "%", grid: true },
      color: { legend: true, domain: ["v1 hf", "v1 lf", "v2 hf", "v2 lf"], range: [css("--c2"), css("--c3"), css("--c1"), css("--c4")] },
      marks: [Plot.line(rows, { x: "snr", y: "r", stroke: "serie", strokeWidth: 1.6 }), Plot.dot(rows, { x: "snr", y: "r", fill: "serie", r: 2 }), Plot.frame({ stroke: line })],
    }));
  }
}

// ---------------------------------------------------------------------------------------------
// E1
// ---------------------------------------------------------------------------------------------
let selectedDay = "";

function renderE1(d: SiteData): void {
  const e = d.e1;
  selectedDay ||= e.days[0].day;
  const rows = e.days.map((x) => `<tr><th scope="row">${x.day}</th><td>${nf(x.reference_ci, 6)}</td><td>${nf(x.computed_ci, 6)}</td>
    <td>${x.relative_difference.toExponential(1).replace(".", ",")}</td><td>${x.valid_minutes} de ${x.minutes}</td><td>${verdict(x.passed)}</td></tr>`).join("");
  const opts = e.days.map((x) => `<label><input type="radio" name="day" value="${x.day}" ${x.day === selectedDay ? "checked" : ""}> ${x.day}</label>`).join("");
  const day = e.days.find((x) => x.day === selectedDay)!;
  $("e1-body").innerHTML = `
    <div class="table-wrap"><table>
      <caption>Média diária do índice: valor publicado pelo MBARI e valor recalculado pelo HMAL (tolerância relativa de ${pct(e.tolerance_relative, 0)})</caption>
      <thead><tr><th scope="col">Dia (UTC)</th><th scope="col">MBARI</th><th scope="col">HMAL</th><th scope="col">Diferença relativa</th><th scope="col">Minutos válidos</th><th scope="col">Resultado</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
    <fieldset class="picker"><legend>Dia exibido</legend>${opts}</fieldset>
    <figure class="spectro">
      <img src="${day.spectrogram}" loading="lazy" width="1200" height="660"
        alt="Espectrograma de 24 horas do hidrofone MARS em ${day.day}, de 0 a 150 Hz, com as faixas de 37, 43, 44 e 50 Hz marcadas, e abaixo a série do índice minuto a minuto." />
      <figcaption>Espectrograma calibrado de ${day.day} (UTC), 0 a 150 Hz. As linhas horizontais marcam a faixa do canto B (43 e 44 Hz) e as faixas de referência (37 e 50 Hz). <a href="${day.spectrogram_original}">Imagem original</a>.</figcaption>
    </figure>
    <h3>Índice minuto a minuto</h3>
    <div id="chart-e1" class="chart"></div>
    ${dataTable(`Índice por hora, média dos minutos válidos, ${day.day}`, ["Hora (UTC)", "Índice médio"],
      Array.from({ length: 24 }, (_, h) => {
        const v = day.series.ci.slice(h * 60, h * 60 + 60).filter((c, i) => c !== null && day.series.valid[h * 60 + i]) as number[];
        return [h, v.length ? nf(v.reduce((a, c) => a + c, 0) / v.length, 3) : "sem dados"];
      }))}
    <p class="small">${esc(e.series_note)}. Fonte: MBARI Pacific Sound, ${esc(e.license)}; dados processados e visualizados pela Hubstry. Arquivo WAV de ${day.day}: SHA-256 ${day.wav_sha256.slice(0, 12)}….</p>
    ${provenanceBlock(e.provenance, "Proveniência do E1")}`;
  document.querySelectorAll<HTMLInputElement>('input[name="day"]').forEach((r) =>
    r.addEventListener("change", () => { selectedDay = r.value; renderE1(d); }));
  drawE1(d);
}

function drawE1(d: SiteData): void {
  const day = d.e1.days.find((x) => x.day === selectedDay)!;
  const pts = day.series.minute.map((m, i) => ({ h: m / 60, ci: day.series.valid[i] ? day.series.ci[i] : null }));
  const width = Math.min(($("e1-body").clientWidth || 800), 960);
  $("chart-e1").replaceChildren(Plot.plot({
    width, height: 230, marginLeft: 52, marginBottom: 44,
    style: { fontFamily: "IBM Plex Sans, system-ui, sans-serif", fontSize: "13px", color: css("--ink"), background: "transparent" },
    x: { label: "Hora (UTC)", domain: [0, 24], ticks: [0, 3, 6, 9, 12, 15, 18, 21, 24], labelAnchor: "center", labelOffset: 38, labelArrow: "none" }, y: { label: "Índice", grid: true },
    marks: [
      Plot.ruleY([day.computed_ci], { stroke: css("--muted"), strokeDasharray: "4,3" }),
      Plot.lineY(pts, { x: "h", y: "ci", stroke: css("--c1"), strokeWidth: 0.8 }),
      Plot.frame({ stroke: css("--line") }),
    ],
  }));
}

// ---------------------------------------------------------------------------------------------
// Documentos e rodapé
// ---------------------------------------------------------------------------------------------
function renderDocs(d: SiteData): void {
  const blob = (p: string) => `${d.repo_url}/blob/${d.publication_commit}/${p}`;
  $("docs").innerHTML = `
    <ul class="docs">
      <li><a href="${blob("lab/BENCH_CRITERIA.md")}">Critérios da bancada digital</a>: ${esc(d.documents.bench_criteria.replace(/\*\*/g, "").replace(/`/g, ""))}.</li>
      <li><a href="${blob("lab/bench/results/REPORT_v1_v2.md")}">Relatório comparativo dos receptores v1 e v2</a>, com resultado integral, ensaios reservados e diagnóstico de falhas.</li>
      <li><a href="${blob("lab/PREREGISTRATION.md")}">Pré-registro da hipótese H1</a>, versão ${esc(d.documents.preregistration_version)}, no estado que o próprio documento declara: ${esc(d.documents.preregistration_status.split("—")[0].trim().toLowerCase())}. Não autoriza inferência confirmatória.</li>
      <li><a href="${blob("docs/SPECIFICATION.md")}">Especificação técnica</a>, com a maturidade por componente.</li>
      <li><a href="${blob("lab/bench/results/MANIFEST.json")}">Manifesto de proveniência</a>: tipo e identificador de cada execução, commit do código executado e SHA-256 de cada arquivo.</li>
    </ul>
    <p>Uma revisão dos critérios (v0.4) está em preparação. Ela só aparecerá aqui depois de congelada, executada sobre uma matriz nova de ensaios e integrada ao ramo principal.</p>`;
  ($("lnk-license") as HTMLAnchorElement).href = blob("LICENSE");
  ($("lnk-ethics") as HTMLAnchorElement).href = blob("docs/ETHICS_GUIDELINES.md");
  $("foot-prov").innerHTML = `Página gerada a partir do commit <a href="${d.publication_commit_url}">${short(d.publication_commit)}</a> do <a href="${d.repo_url}">repositório do HMAL</a>. Os resultados numéricos desta página não são digitados à mão: são lidos dos arquivos versionados nesse commit, com SHA-256 conferido no build. Limiares e parâmetros citados no texto vêm dos critérios v0.3.1.`;
}

// ---------------------------------------------------------------------------------------------
async function main(): Promise<void> {
  drawRuler();
  let data: SiteData;
  try {
    const res = await fetch("./data/site.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch (err) {
    $("bench-runs").innerHTML = `<p class="note">Os dados não carregaram (${esc(String(err))}). Recarregue a página ou consulte o <a href="https://github.com/Hubstry-DeepTech/hubstry-marine-acoustic-layer">repositório</a>.</p>`;
    return;
  }
  renderRuns(data);
  renderDetail(data);
  renderE1(data);
  renderDocs(data);
  let t: number | undefined;
  const redraw = () => { clearTimeout(t); t = window.setTimeout(() => { drawBenchCharts(data); drawE1(data); }, 150); };
  window.addEventListener("resize", redraw);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", redraw);
}

main();
