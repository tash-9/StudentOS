let workspace,
  records = [],
  current = null,
  editing = null;
const $ = (q) => document.querySelector(q),
  esc = (x) =>
    String(x ?? '').replace(
      /[&<>"']/g,
      (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
    );
async function api(url, options = {}) {
  const r = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  const d = await r.json();
  if (!r.ok) throw Error(d.error || 'Request failed');
  return d;
}
function toast(s) {
  const t = $('#toast');
  t.textContent = s;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}
const dbInfo = (name) => workspace.databases.find((d) => d.name === name);
const labelFor = (d) => d.name;
function setupNav() {
  const menu = $('#navigation');
  let html = '';
  workspace.modules.forEach((m, i) => {
    const items = workspace.databases.filter((d) => d.module === i + 1);
    html +=
      `<div class="navlabel">${esc(m.name.replace(/^\S+\s+\d+\.\s*/, '').toUpperCase())}</div>` +
      items
        .map(
          (d) =>
            `<button class="nav" data-db="${esc(d.name)}">${iconFor(d.name)} <span>${esc(d.name)}</span></button>`
        )
        .join('');
  });
  menu.innerHTML = html;
  $('[data-page="home"]').onclick = () => navigate(null);
  document.querySelectorAll('[data-db]').forEach((b) => (b.onclick = () => navigate(b.dataset.db)));
}
function iconFor(name) {
  const map = {
    Courses: '▤',
    Semesters: '◷',
    'Class Timetable': '▦',
    Assignments: '▧',
    Attendance: '◉',
    Notes: '✎',
    Resources: '↗',
    'Reading Library': '▣',
    'Brain Dump Inbox': '✧',
    Exams: '◇',
    'Revision Planner': '↻',
    'Syllabus Tracker': '☷',
    Tasks: '✓',
    Projects: '⌘',
    'Daily Planner': '☀',
    'Weekly Planner': '▦',
    'Study Sessions': '◷',
    Habits: '◌',
    Goals: '⚑',
    'Personal Journal': '✎',
    Expenses: '＄',
    'Monthly Budget': '▤',
    'Savings Goals': '◈',
    Subscriptions: '↻',
    Skills: '✳',
    'Learning Roadmaps': '⌁',
    'Meeting Notes': '☷',
    Grades: '↗',
    Achievements: '✦',
    'Monthly Reviews': '◷',
    Contacts: '♙',
    Documents: '▤',
    'Scholarships & Opportunities': '✦',
  };
  return map[name] || '•';
}
async function refresh() {
  [workspace, records] = await Promise.all([api('/api/workspace'), api('/api/records')]);
  setupNav();
  renderHome();
  if (current) navigate(current);
}
function navigate(db) {
  current = db;
  $('#crumb').textContent = db || 'Overview';
  $('#home').classList.toggle('hidden', !!db);
  $('#database').classList.toggle('hidden', !db);
  document
    .querySelectorAll('.nav')
    .forEach((b) =>
      b.classList.toggle('active', b.dataset.db === db || (!db && b.dataset.page === 'home'))
    );
  $('#database').classList.toggle('hidden', !db);
  if (db) renderDb(db);
}
function renderHome() {
  const today = new Date(),
    summary = {};
  workspace.databases.forEach(
    (d) => (summary[d.name] = records.filter((r) => r.database === d.name).length)
  );
  const deadlines = [];
  for (const r of records) {
    const key = { Tasks: 'Due Date', Assignments: 'Due Date', Exams: 'Exam Date' }[r.database];
    if (!key || !r.data[key]) continue;
    const date = new Date(r.data[key] + 'T00:00:00');
    const days = (date - new Date(today.toDateString())) / 86400000;
    if (
      days >= 0 &&
      days <= 7 &&
      !['done', 'completed', 'submitted'].includes(String(r.data.Status || '').toLowerCase())
    )
      deadlines.push({
        title: r.data['Task Name'] || r.data['Assignment Name'] || r.data['Exam Name'],
        date,
        r,
      });
  }
  deadlines.sort((a, b) => a.date - b.date);
  const dt = today.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });
  $('#home').innerHTML =
    `<div class="hero"><div><div class="eyebrow">${esc(dt.toUpperCase())}</div><h1>Make today count<span style="color:#789474">.</span></h1><p>A little progress each day adds up to big results.</p></div><div class="heroart">📚</div></div><div class="stats"><div class="stat"><label>All records</label><div class="num">${records.length}</div><small>Across your workspace</small></div><div class="stat"><label>Databases</label><div class="num">${workspace.databases.length}</div><small>Ready to organize</small></div><div class="stat"><label>Coming up</label><div class="num">${deadlines.length}</div><small>Deadlines in the next 7 days</small></div><div class="stat"><label>Modules</label><div class="num">${workspace.modules.length}</div><small>Your student life, in one place</small></div></div><div class="grid"><div class="card"><div class="cardhead"><h3>Coming up</h3><span class="tag">NEXT 7 DAYS</span></div>${
      deadlines.length
        ? deadlines
            .slice(0, 7)
            .map(
              (x) =>
                `<div class="deadline"><div class="datebox"><span>${x.date.toLocaleDateString(undefined, { month: 'short' }).toUpperCase()}</span><b>${x.date.getDate()}</b></div><div class="dinfo"><b>${esc(x.title)}</b><small>${esc(x.r.database)} · ${esc(x.r.data.Priority || '')}</small></div><span class="tag ${String(x.r.data.Priority).toLowerCase() === 'high' ? 'high' : ''}">${esc(x.r.data.Priority || 'Due soon')}</span></div>`
            )
            .join('')
        : '<div class="empty">No deadlines in the next 7 days.</div>'
    }</div><div class="card"><div class="cardhead"><h3>Quick capture</h3><span class="tag">GET IT DOWN</span></div><p class="sub" style="line-height:1.7;margin:0 0 15px">Capture a task, note or study session before the thought slips away.</p><div style="display:flex;gap:7px;flex-wrap:wrap"><button class="quiet" data-quick="Tasks">＋ Task</button><button class="quiet" data-quick="Notes">＋ Note</button><button class="quiet" data-quick="Study Sessions">＋ Study session</button></div></div></div><div class="card" style="margin-top:14px"><div class="cardhead"><h3>Your workspace</h3><span class="tag">${workspace.databases.length} DATABASES</span></div><div class="modules">${workspace.modules
      .map((m, i) => {
        const dbs = workspace.databases.filter((d) => d.module === i + 1);
        return `<div class="module" data-open-module="${i + 1}"><b>${esc(m.name.replace(/^\S+\s+\d+\.\s*/, ''))}</b><em>${dbs.reduce((n, d) => n + (summary[d.name] || 0), 0)}</em><small>${dbs.length} databases · ${dbs
          .slice(0, 3)
          .map((d) => esc(d.name))
          .join(' · ')}${dbs.length > 3 ? '…' : ''}</small></div>`;
      })
      .join('')}</div></div>`;
  document
    .querySelectorAll('[data-quick]')
    .forEach((b) => (b.onclick = () => openEntry(b.dataset.quick)));
  document.querySelectorAll('[data-open-module]').forEach(
    (el) =>
      (el.onclick = () => {
        const d = workspace.databases.find((x) => x.module === Number(el.dataset.openModule));
        if (d) navigate(d.name);
      })
  );
}
function renderDb(name) {
  const d = dbInfo(name);
  if (!d) return;
  const list = records.filter((r) => r.database === name);
  const fields = d.fields;
  $('#database').innerHTML =
    `<div class="pagetitle"><div><div class="eyebrow">STUDENT OS / ${esc(workspace.modules[d.module - 1].name.replace(/^\S+\s+\d+\.\s*/, '').toUpperCase())}</div><h1>${esc(name)}</h1><p class="sub">${esc(d.description)} · ${list.length} entries</p></div><button class="button" id="add">＋ Add entry</button></div><div class="toolbar"><input class="search" id="search" placeholder="⌕  Search ${esc(name.toLowerCase())}…"><select class="select" id="sort"><option value="recent">Recently updated</option><option value="name">Name A–Z</option></select></div><div class="tablewrap"><table><thead><tr>${fields.map((f) => `<th>${esc(f.name.toUpperCase())}</th>`).join('')}<th>ACTIONS</th></tr></thead><tbody id="rows"></tbody></table><div id="no-rows" class="empty hidden">No entries yet. Add your first one to get started.</div></div>`;
  const draw = () => {
    let q = $('#search').value.toLowerCase(),
      shown = list.filter((r) =>
        fields.some((f) =>
          String(r.data[f.name] || '')
            .toLowerCase()
            .includes(q)
        )
      );
    if ($('#sort').value === 'name')
      shown.sort((a, b) =>
        String(Object.values(a.data)[0]).localeCompare(String(Object.values(b.data)[0]))
      );
    $('#rows').innerHTML = shown
      .map(
        (r) =>
          `<tr>${fields
            .map((f) => {
              let v = r.data[f.name] || '—';
              if (f.type === 'checkbox') v = v === 'Yes' ? '✓' : v === 'No' ? '—' : v;
              return `<td title="${esc(v)}">${esc(v)}</td>`;
            })
            .join(
              ''
            )}<td><div class="actions-row"><button class="act" data-edit="${r.id}" title="Edit">✎</button><button class="act" data-delete="${r.id}" title="Delete">⌫</button></div></td></tr>`
      )
      .join('');
    $('#no-rows').classList.toggle('hidden', shown.length > 0);
    document
      .querySelectorAll('[data-edit]')
      .forEach((b) => (b.onclick = () => openEntry(name, b.dataset.edit)));
    document
      .querySelectorAll('[data-delete]')
      .forEach((b) => (b.onclick = () => deleteEntry(b.dataset.delete)));
  };
  $('#search').oninput = draw;
  $('#sort').onchange = draw;
  $('#add').onclick = () => openEntry(name);
  draw();
}
function openEntry(name, id) {
  const d = dbInfo(name);
  editing = id || null;
  const rec = id ? records.find((r) => r.id === id) : null;
  $('#modal-title').textContent = `${id ? 'Edit' : 'Add'} ${name.replace(/s$/, '')}`;
  $('#fields').innerHTML = d.fields
    .map((f, i) => {
      const value = rec?.data[f.name] || '',
        escaped = esc(value),
        idAttr = `field-${i}`;
      let input = '';
      const options = (typeof f.detail === 'string' ? f.detail : '').split(' · ').filter(Boolean);
      if (f.type === 'checkbox')
        input = `<select id="${idAttr}"><option ${value !== 'Yes' ? 'selected' : ''}>No</option><option ${value === 'Yes' ? 'selected' : ''}>Yes</option></select>`;
      else if (f.type === 'relation') {
        const choices = records
          .filter((r) => r.database === f.target)
          .map((r) => Object.values(r.data)[0])
          .filter(Boolean);
        input = `<select id="${idAttr}" ${String(value).includes(',') ? 'multiple' : ''}><option value="">— Select —</option>${[
          ...new Set([
            ...choices,
            ...value
              .split(',')
              .map((v) => v.trim())
              .filter(Boolean),
          ]),
        ]
          .map(
            (v) =>
              `<option value="${esc(v)}" ${
                value
                  .split(',')
                  .map((x) => x.trim())
                  .includes(v)
                  ? 'selected'
                  : ''
              }>${esc(v)}</option>`
          )
          .join('')}</select>`;
      } else if (f.type === 'select' || f.type === 'status' || f.type === 'multi') {
        input =
          f.type === 'multi'
            ? `<input id="${idAttr}" value="${escaped}" placeholder="Choose or type, separated by commas">`
            : `<select id="${idAttr}"><option value="">— Select —</option>${options.map((v) => `<option ${v === value ? 'selected' : ''}>${esc(v)}</option>`).join('')}</select>`;
      } else {
        let t =
          f.type === 'date'
            ? 'date'
            : f.type === 'number'
              ? 'number'
              : f.type === 'url'
                ? 'url'
                : 'text';
        let wide =
          ['text', 'url', 'files'].includes(f.type) &&
          /notes|content|discussion|reflection|takeaway|feedback|highlights|challenges|gratitude|eligibility|action items|practice tasks|topics/i.test(
            f.name
          );
        input = wide
          ? `<textarea id="${idAttr}">${escaped}</textarea>`
          : `<input id="${idAttr}" type="${t}" value="${escaped}" ${t === 'number' ? 'step="any"' : ''}>`;
        return `<div class="field ${wide ? 'wide' : ''}"><label for="${idAttr}">${esc(f.name)}</label>${input}</div>`;
      }
      return `<div class="field"><label for="${idAttr}">${esc(f.name)}</label>${input}</div>`;
    })
    .join('');
  $('#modal').showModal();
  $('#form').onsubmit = async (e) => {
    e.preventDefault();
    const data = {};
    d.fields.forEach((f, i) => {
      const input = $(`#field-${i}`);
      data[f.name] = input.multiple
        ? [...input.selectedOptions]
            .map((o) => o.value)
            .filter(Boolean)
            .join(', ')
        : input.value;
    });
    try {
      await api(id ? `/api/records/${id}` : '/api/records', {
        method: id ? 'PUT' : 'POST',
        body: JSON.stringify(id ? { data } : { database: name, data }),
      });
      $('#modal').close();
      toast(id ? 'Entry updated' : 'Entry added');
      await refresh();
    } catch (err) {
      toast(err.message);
    }
  };
}
async function deleteEntry(id) {
  if (!confirm('Delete this entry? This cannot be undone.')) return;
  try {
    await api(`/api/records/${id}`, { method: 'DELETE' });
    toast('Entry deleted');
    await refresh();
  } catch (e) {
    toast(e.message);
  }
}
$('#new').onclick = () => openEntry(current || 'Tasks');
$('#close').onclick = $('#cancel').onclick = () => $('#modal').close();
$('#form').onsubmit = (e) => e.preventDefault();
$('#theme').onclick = () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('student-os-dark', document.body.classList.contains('dark'));
};
$('#today').textContent = new Date().toLocaleDateString(undefined, {
  weekday: 'short',
  month: 'short',
  day: 'numeric',
  year: 'numeric',
});
if (localStorage.getItem('student-os-dark') === 'true') document.body.classList.add('dark');
refresh().catch((err) => {
  $('#home').innerHTML =
    `<div class="card"><h3>Dashboard unavailable</h3><p>${esc(err.message)}. Start with <code>python -m student_os web</code>.</p></div>`;
});
