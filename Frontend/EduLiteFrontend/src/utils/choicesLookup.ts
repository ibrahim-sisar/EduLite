import subjects from "@choices/subjects.json";
import countries from "@choices/countries.json";
import languages from "@choices/languages.json";

type ChoiceEntry = { value: string; label: string };

function toLookup(entries: ChoiceEntry[]): Record<string, string> {
  const map: Record<string, string> = {};
  for (const entry of entries) {
    map[entry.value] = entry.label;
  }
  return map;
}

export const SUBJECTS = toLookup(subjects);
export const COUNTRIES = toLookup(countries);
export const LANGUAGES = toLookup(languages);
