/* Synthetic interaction checks for audit-template.html. Node 18+, no packages.
 * This small DOM harness exercises the page's actual script. It is not a browser
 * layout, accessibility, file-picker, or real-download integration test.
 * No corpus responses, sample keys, predictions, or human labels are read.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const source = fs.readFileSync(path.join(__dirname, 'audit-template.html'), 'utf8');
const script = [...source.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].at(-1)[1];
assert.equal(source.split('__AUDIT_PAYLOAD__').length - 1, 1);
assert.doesNotMatch(source, /https?:\/\//);
const payload = {
  schema: 'bestiary2-zoned-v1.1-audit-page/1',
  audit_id: 'synthetic-ui-only',
  items: [
    {item_id: 'a', prompt: 'Synthetic prompt A', response: '<b>Synthetic literal response A</b>', imaginary: false},
    {item_id: 'b', prompt: 'Synthetic imaginary prompt B', response: 'Synthetic response B', imaginary: true},
  ],
};

class Element {
  constructor() {
    this.listeners = {};
    this.children = [];
    this.value = '';
    this.textContent = '';
    this.hidden = this.checked = this.disabled = false;
    this.files = [];
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  replaceChildren() { this.children = []; }
  append(child) { this.children.push(child); }
  focus() {}
  scrollIntoView() {}
  click() {}
  remove() {}
}

function mount(storage = Object.create(null)) {
  const els = Object.fromEntries([...source.matchAll(/id="([^"]+)"/g)].map(match => [match[1], new Element()]));
  els['audit-data'].textContent = JSON.stringify(payload);
  const radios = [...source.matchAll(/<input type="radio" name="([^"]+)" value="([^"]+)"/g)].map(match =>
    Object.assign(new Element(), {name: match[1], value: match[2]}));
  const document = {
    hidden: false,
    body: new Element(),
    listeners: {},
    getElementById: name => els[name],
    createElement: () => new Element(),
    addEventListener(name, callback) { this.listeners[name] = callback; },
    querySelectorAll(selector) {
      return radios.filter(radio => radio.name === selector.match(/name="([^"]+)"/)[1]);
    },
    querySelector(selector) {
      const choices = this.querySelectorAll(selector);
      return selector.endsWith(':checked') ? choices.find(radio => radio.checked) || null : choices[0];
    },
  };
  let blob, clock = 0;
  const context = {
    document,
    localStorage: {getItem: key => storage[key] || null, setItem: (key, value) => { storage[key] = value; }},
    performance: {now: () => clock += 10},
    window: {addEventListener() {}},
    Blob,
    URL: {createObjectURL: value => { blob = value; return 'blob:test'; }, revokeObjectURL() {}},
    setTimeout: () => 0,
    console,
  };
  vm.createContext(context);
  vm.runInContext(script, context, {filename: 'audit-template.inline.js'});
  return {
    els, radios, storage,
    selected(name, value) { return radios.find(radio => radio.name === name && radio.value === value).checked; },
    choose(name, value) {
      radios.filter(radio => radio.name === name).forEach(radio => { radio.checked = radio.value === value; });
      els.labels.listeners.change();
    },
    submit() { els.labels.listeners.submit({preventDefault() {}}); },
    async download() { els.download.listeners.click(); return JSON.parse(await blob.text()); },
    async import(value) {
      const encoded = JSON.stringify(value);
      els.file.files = [{size: Buffer.byteLength(encoded), text: async () => encoded}];
      await els.file.listeners.change();
    },
  };
}

(async () => {
  let ui = mount();
  assert.equal(ui.radios.filter(radio => radio.checked).length, 0, 'New labels start blank.');
  assert.equal(ui.els.response.textContent, payload.items[0].response, 'The response is supplied as literal text.');

  ui.choose('nonrecognition', 'Y');
  let output = await ui.download();
  assert.equal(output.items.length, 0, 'Exports exclude incomplete labels.');
  ui.choose('description', 'N');
  assert.equal(ui.els['mark-group'].hidden, true);
  assert.match(ui.els['progress-text'].textContent, /1 complete/);
  output = await ui.download();
  assert.equal(output.items.length, 1);
  assert.equal(output.items[0].mark, null, 'No description requires no mark answer.');

  ui = mount(ui.storage);
  assert.equal(ui.selected('description', 'N'), true, 'Local autosave survives remounting.');
  ui.submit();
  assert.equal(ui.els.prompt.textContent, payload.items[1].prompt);
  assert.equal(ui.radios.filter(radio => radio.checked).length, 0, 'The next item has no inherited answers.');
  ui.choose('nonrecognition', 'N');
  ui.choose('description', 'H');
  assert.equal(ui.els['mark-group'].hidden, false);
  assert.equal(ui.els['echo-choice'].hidden, false);
  ui.submit();
  assert.match(ui.els.message.textContent, /question 3/, 'An applicable mark answer is required.');
  ui.choose('mark', 'E');
  ui.els.unsure.checked = true;
  ui.els.notes.value = 'Synthetic note';
  ui.els.labels.listeners.change();
  output = await ui.download();
  assert.equal(output.items.length, 2);
  assert.equal(output.items[1].mark, 'E');
  assert.equal(output.items[1].notes, 'Synthetic note');
  assert.equal(output.items[1].flagged_unsure, true);
  assert.ok(Number.isSafeInteger(output.items[1].ms) && output.items[1].ms >= 0);

  ui.choose('description', 'S');
  assert.equal(ui.els['mark-group'].hidden, true);
  output = await ui.download();
  assert.equal(output.items[1].mark, null, 'Substitution is separate and clears an earlier target mark.');
  ui.els.previous.listeners.click();
  assert.equal(ui.selected('description', 'N'), true, 'Navigation preserves saved judgments.');
  assert.equal(ui.els['echo-choice'].hidden, true);

  const invalid = [
    [{...output, audit_id: 'wrong'}, /different audit/],
    [{...output, items: [{...output.items[0], description: 'S', mark: 'Y'}]}, /must be null/],
    [{...output, items: [{...output.items[0], description: 'Y', mark: 'E'}]}, /unavailable/],
    [{...output, items: [output.items[0], output.items[0]]}, /twice/],
    [{...output, items: [{...output.items[0], item_id: 'unknown'}]}, /unknown response/],
    [{...output, items: [{...output.items[0], flagged_unsure: 1}]}, /true or false/],
    [{...output, items: [{...output.items[0], ms: -1}]}, /reading time/],
  ];
  for (const [candidate, expected] of invalid) {
    await ui.import(candidate);
    assert.match(ui.els.message.textContent, expected);
    assert.equal(ui.selected('description', 'N'), true, 'Rejected imports do not change existing answers.');
  }
  await ui.import({...output, items: [{...output.items[0], description: 'S', mark: null, notes: 'Imported note'}]});
  assert.match(ui.els.message.textContent, /Imported 1/);
  assert.equal(ui.els.notes.value, 'Imported note');
  assert.equal(ui.selected('description', 'S'), true);
  console.log('PASS: synthetic UI harness — blank labels, literal text, conditional marks, substitution, autosave, navigation, export, unsure/notes, import validation.');
})().catch(error => { console.error(error); process.exitCode = 1; });
