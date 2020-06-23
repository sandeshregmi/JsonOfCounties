# County-level Data

This is a working repository of data broken down by US county.

While most of this repositoory is dedicated to providing the data and code that we used to produce the final dataset, the dataset itself is simply states.json.  An example entry:

```JSON
{
  // ...
  "Nebraska": {
    // ...
    "holt county": {
       "area": 0.68525076424703,
       "location": [
        -98.66118420812809,
        42.4859272567734
       ],
       "min_loation": [
        -99.25703899999999,
        42.087894999999996
       ],
       "max_loation": [
        -98.300212,
        42.896724
       ],
       "population": {
        "2010": 10434,
        "2015": 10263,
        "2019": 10067
       },
       "race_demographics": {
        "non_hispanic_white_alone_male": 0.4622715661230104,
        "non_hispanic_white_alone_female": 0.4660051090587542,
        "black_alone_male": 0.0020632737276478678,
        "black_alone_female": 0.0017685203379838867,
        "asian_alone_male": 0.0021615248575358615,
        "asian_alone_female": 0.003340538416191786,
        "hispanic_male": 0.02859107879740617,
        "hispanic_female": 0.024071526822558458
       },
       "age_demographics": {
        "0-4": 0.07044606012969148,
        "5-9": 0.0734918451562193,
        "10-14": 0.07142857142857142,
        "15-19": 0.05570839064649243,
        "20-24": 0.0500098251129888,
        "25-29": 0.04725879347612497,
        "30-34": 0.04951856946354883,
        "35-39": 0.0546276282177245,
        "40-44": 0.04666928669679701,
        "45-49": 0.046865788956573,
        "50-54": 0.056494399685596386,
        "55-59": 0.08351346040479465,
        "60-64": 0.078109648260955,
        "65-69": 0.06543525250540382,
        "70-74": 0.048143053645116916,
        "75-79": 0.039791707604637454,
        "80-84": 0.027706818628414228,
        "85+": 0.03478089998034977
       },
       "male": 5088,
       "female": 5090,
       "deaths": "2343",
       "suicides": "17",
       "firearm suicides": "12",
       "labor_force": "5,763",
       "employed": "5,613",
       "unemployed": "150",
       "unemployment_rate": "2.6",
       "fatal_police_shootings": 0,
       "unarmed_fatal_police_shootings": 0,
       "fatal_police_shootings_where_victim_had_firearm": 0
      },
    // ...
  },
  // ...
}
```

## Sources

1. State geometry (location, area, etc.) is computed from data.gov, specifically [here](https://catalog.data.gov/dataset/tiger-line-shapefile-2017-nation-u-s-current-county-and-equivalent-national-shapefile).  This data is NOT included in the repository because if is 122 MB.  State areas are computed naively, assuming longitude/latitude are x/y coordinates.  As a result they're not particularly accurate (because longitude sizes vary based on location) but should be useful for computing population density.  Some day I hope to get around to computing them [accurately](https://stackoverflow.com/questions/1340223/calculating-area-enclosed-by-arbitrary-polygon-on-earths-surface) (or a helpful Internet stranger like yourself might do it for me).

2. Population comes from the US 2010 census, as well as the official 2019 guesses.

3. Demographics also come from the Census Bureau, but come from the 2018 census ([here](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html#par_textimage_1383669527)).  This csv file is NOT included, as it is 154 MB.

3. Deaths, suicides, and firearm suicides come from the [CDC's website](https://wonder.cdc.gov/cmf-icd10.html), where you can request the totals for each county.  We manually requested totals for all deaths, all suicides, and firearm suicides, but adding other causes of deaths is easy if you can give us the [ICD-10 Codes](https://wonder.cdc.gov/wonder/help/cmf.html#ICD-10%20Codes) you're interested in.  This is the source of the vast majority of missing data (marked as null in the JSON), since the CDC suppresses data from counties with sufficiently few cases. 

4. Labor statistics comes from [here](https://www.bls.gov/lau/#cntyaa) (the BLS).

5. Police shootings data comes from the [Washington Post's dataset](https://github.com/washingtonpost/data-police-shootings).  In cases where the county is ambiguous, shootings are distributed fractionally.

Note that this "states.json" does NOT contain a superset of each data source.  For instance the racial/age demographic breakdown provided by "cc-est2018-alldata.csv" is extremely specific (giving race/sex break downs for every age bucket for 9 years!) but we don't include all of that in states.json.

Fortunately, it shouldn't be hard for somebody with some Python experience to modify "create_json.py" to add whatever additional data they might need.

## Why

