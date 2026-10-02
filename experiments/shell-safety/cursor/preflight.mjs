// Authentication/catalog check only: never starts an agent or executes tools.
import {Cursor} from '@cursor/sdk';
import {writeFileSync} from 'node:fs';

const status = await Cursor.auth.status();
if (!process.env.CURSOR_API_KEY && status.status !== 'logged-in') {
  console.error('Cursor authentication required: configure CURSOR_API_KEY or use Cursor.auth.login(). Do not put credentials in study artifacts.');
  process.exit(2);
}
const models = await Cursor.models.list();
const model = models.find(m => m.id === 'composer-2.5');
if (!model) throw new Error('composer-2.5 is not available to this account');
const fast = model.parameters?.find(p => p.id === 'fast');
if (!fast?.values.some(v => v.value === 'true')) {
  throw new Error('Catalog does not advertise fast=true; inspect before running');
}
const evidence = {
  checkedAt: new Date().toISOString(), sdkVersion: '1.0.35',
  requestedModel: {id: model.id, params: [{id: 'fast', value: 'true'}]},
  catalogModel: model, autoReviewRequested: true,
  classifierAvailability: 'not verified by catalog discovery',
  experimentReady: false,
};
writeFileSync(new URL('./preflight.json', import.meta.url), JSON.stringify(evidence, null, 2) + '\n');
console.log('Model catalog verified. Classifier routing and independent containment still require live validation. No agent was started.');
