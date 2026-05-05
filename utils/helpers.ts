import * as fs   from 'fs';
import * as path from 'path';

export interface TestCase {
  search_query: string;
  max_price:    number;
  items_limit:  number;
  user_name:    string;
  password:     string;
}

export function loadTestData(): TestCase[] {
  const file = path.join(__dirname, '..', 'data', 'search_data.json');
  return JSON.parse(fs.readFileSync(file, 'utf-8'));
}

export function extractPrice(text: string): number {
  const firstPart = text.split('to')[0];
  const match     = firstPart.replace(/,/g, '').match(/\d+(?:\.\d+)?/);
  return match ? parseFloat(match[0]) : Infinity;
}

export function ensureDir(dir: string): void {
  fs.mkdirSync(dir, { recursive: true });
}
