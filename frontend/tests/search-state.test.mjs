import { test } from 'node:test';
import assert from 'node:assert/strict';
import { freshSearch, readSearch, searchUrl, safeBack } from '../lib/search-state.ts';

test('refinement URL restores the exact request after refresh', () => {
  const state = freshSearch('cafe in Goa');
  state.filters = [{ facet: 'when', level: 'month', label: 'February 2024', start: '2024-02-01T00:00:00', end: '2024-03-01T00:00:00' }, { facet: 'who', value: 'rahul', label: 'Rahul' }];
  state.removed_concept_ids = ['snowy'];
  state.want_drop = true;
  assert.deepEqual(readSearch(new URLSearchParams(searchUrl(state).split('?')[1])), state);
});

test('short screenshot URL produces the real month filter', () => {
  const state = readSearch(new URLSearchParams('q=cafe+in+Goa&month=2024-02'));
  assert.equal(state.query, 'cafe in Goa');
  assert.deepEqual(state.filters[0], { facet: 'when', level: 'month', label: 'February 2024', start: '2024-02-01T00:00:00', end: '2024-03-01T00:00:00' });
});

test('nearest-time override and removal survive URL serialization', () => {
  const state = freshSearch('cafe in Goa 2025');
  state.concept_overrides = [{ id: '2025', label: '2024', kind: 'time', year: 2024, synonyms: [] }];
  assert.deepEqual(readSearch(new URLSearchParams(searchUrl(state).split('?')[1])), state);
});

test('invalid state is handled and viewer back cannot leave the demo', () => {
  assert.deepEqual(readSearch(new URLSearchParams('filters=broken&overrides=%7B%7D&month=2024-13')).filters, []);
  assert.equal(safeBack('https://example.com'), '/');
  assert.equal(safeBack('//example.com'), '/');
  assert.equal(safeBack('javascript:alert(1)'), '/');
  assert.equal(safeBack('/search?q=cafe'), '/search?q=cafe');
});
