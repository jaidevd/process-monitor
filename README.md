# Process Monitor

## Setup

- [Install Gramex 1.x](https://learn.gramener.com/guide/install/)
- Clone this repository
- Copy assets from shared repo, e.g. `demo.gramener.com:/deploy/poc/altair-poc/`
- From the repo folder, run `gramex setup .`
- From the repo folder, run `gramex`

## Contributions

- Pratap Vardhan <pratap.vardhan@gramener.com>
- S Anand <s.anand@gramener.com>

### Folder structure

- `assets/img/`     has images
- `assets/data/`    has data files (e.g. topoJSON maps, XLSX, CSV, SQLite files)
- `assets/fonts/`   has custom fonts (if required)

## Notes

- Stage changes at var index = // 10, 250, 380, 420, 450, 500, 650

```
fields

Reactor Temperature,	Crystallizer Cooling Rate,	Crystallizer Stirring Speed,	Filter (1),
Slurry Tank,	Filter (3), Dryer Temperature,Drying Speed,Crushing speed,Outcome

Batch Number	Dryer Cycle Time (min)	Dryer Speed	Avg Dryer Temp	Crusher speed	Crushing time (min)
Avg Reactor Temp	Reaction Time (min)	Material A	Material B	Solvent Amt	Catalyzer Type	Crystallizer
Cooling Rate	Crystallizer Stirring Speed	Outcome
```

```
input sheet columns are changed

    rename = {
        'Dryer Cycle Time (min)': 'Avg Dryer Cycle Time (min)',
        'Dryer Speed': 'Avg Dryer Speed',
        'Crushing time (min)': 'Avg Crushing time (min)',
        'Reaction Time (min)': 'Avg Reaction Time (min)',
        'Crystallizer Cooling Rate': 'Avg Crystallizer Cooling Rate',
        'Crystallizer Stirring Speed': 'Avg Crystallizer Stirring Speed',
        'Avg Dryer Temp': 'Avg Dryer Temperature',
        'Crusher speed': 'Avg Crushing speed',
        'Avg Reactor Temp': 'Avg Reactor Temperature'
    }

df['Outcome'] = df['Outcome'].map({'Good(fine>90%)': 'Good', 'Bad(fine<90%)': 'Bad'}
```