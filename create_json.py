import csv, json, os, re

# pip install pyshp
import shapefile

import matplotlib.pyplot as plt
import numpy as np

import os

pjoin = os.path.join

# pip install Shapely
from shapely.geometry import Point

# https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
def area(x, y):
	return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

sf = shapefile.Reader(pjoin('data', 'tl_2017_us_county.shp'))

abbreviation_to_name = {
	"AL": "Alabama",
	"AK": "Alaska",
	"AZ": "Arizona",
	"AR": "Arkansas",
	"CA": "California",
	"CO": "Colorado",
	"CT": "Connecticut",
	"DE": "Delaware",
	"DC": "District of Columbia",
	"FL": "Florida",
	"GA": "Georgia",
	"GU": "Guam",
	"HI": "Hawaii",
	"ID": "Idaho",
	"IL": "Illinois",
	"IN": "Indiana",
	"IA": "Iowa",
	"KS": "Kansas",
	"KY": "Kentucky",
	"LA": "Louisiana",
	"ME": "Maine",
	"MD": "Maryland",
	"MA": "Massachusetts",
	"MI": "Michigan",
	"MN": "Minnesota",
	"MS": "Mississippi",
	"MO": "Missouri",
	"MT": "Montana",
	"NE": "Nebraska",
	"NV": "Nevada",
	"NH": "New Hampshire",
	"NJ": "New Jersey",
	"NM": "New Mexico",
	"NY": "New York",
	"NC": "North Carolina",
	"ND": "North Dakota",
	"OH": "Ohio",
	"OK": "Oklahoma",
	"OR": "Oregon",
	"PA": "Pennsylvania",
	"RI": "Rhode Island",
	"SC": "South Carolina",
	"SD": "South Dakota",
	"TN": "Tennessee",
	"TX": "Texas",
	"UT": "Utah",
	"VT": "Vermont",
	"VI": "Virgin Islands",
	"VA": "Virginia",
	"WA": "Washington",
	"WV": "West Virginia",
	"WI": "Wisconsin",
	"WY": "Wyoming",
}

fips_code_to_name = {
	"01": "Alabama",
	"02": "Alaska",
	"04": "Arizona",
	"05": "Arkansas",
	"06": "California",
	"08": "Colorado",
	"09": "Connecticut",
	"10": "Delaware",
	"11": "District of Columbia",
	"12": "Florida",
	"13": "Georgia",
	"15": "Hawaii",
	"16": "Idaho",
	"17": "Illinois",
	"18": "Indiana",
	"19": "Iowa",
	"20": "Kansas",
	"21": "Kentucky",
	"22": "Louisiana",
	"23": "Maine",
	"24": "Maryland",
	"25": "Massachusetts",
	"26": "Michigan",
	"27": "Minnesota",
	"28": "Mississippi",
	"29": "Missouri",
	"30": "Montana",
	"31": "Nebraska",
	"32": "Nevada",
	"33": "New Hampshire",
	"34": "New Jersey",
	"35": "New Mexico",
	"36": "New York",
	"37": "North Carolina",
	"38": "North Dakota",
	"39": "Ohio",
	"40": "Oklahoma",
	"41": "Oregon",
	"42": "Pennsylvania",
	"44": "Rhode Island",
	"45": "South Carolina",
	"46": "South Dakota",
	"47": "Tennessee",
	"48": "Texas",
	"49": "Utah",
	"50": "Vermont",
	"51": "Virginia",
	"53": "Washington",
	"54": "West Virginia",
	"55": "Wisconsin",
	"56": "Wyoming",
	"60": "American Samoa",
	"66": "Guam",
	"69": "Northern Mariana Islands",
	"72": "Puerto Rico",
	"78": "Virgin Islands",
}

not_states = set([
	"American Samoa",
	"Guam",
	"Northern Mariana Islands",
	"Puerto Rico",
	"Virgin Islands",
])

# Add geometric data for countries.
states = {}
for s in sf:
	state = fips_code_to_name[s.record.STATEFP]
	if state in not_states:
		continue
	if state not in states:
		states[state] = {}
	# https://shapely.readthedocs.io/en/stable/manual.html#object.simplify
	# TODO use shapely to simplify the points and
	# write the points into the json.  This lets users
	# (e.g.) compute location however they want.
	X = np.array([p[0] for p in s.shape.points])
	Y = np.array([p[1] for p in s.shape.points])
	county_name = s.record.NAMELSAD.lower()

	assert county_name not in states[state]

	states[state][county_name] = {
		"area": area(X, Y),
		# A simple/naive "location" of the county.
		"location": [X.mean(), Y.mean()],
		"min_loation": [X.min(), Y.min()],
		"max_loation": [X.max(), Y.max()],
	}

def add_population(states):
	with open(pjoin('data', 'us_census.tsv'), 'r') as f:
		reader = csv.reader(f, delimiter='\t', quotechar='"')
		rows = [row for row in reader]
	header = rows[0]
	rows = rows[1:]
	for row in rows:
		county = ', '.join(row[0].split(', ')[:-1]).lower()
		state = row[0].split(', ')[-1]
		if state in not_states:
			continue
		if county not in states[state]:
			if county[-17:] == ' city and borough':
				county = county[:-17]
			if county[-7:] == ' county':
				county = county[:-7]
			if county[-5:] == ' city':
				county = county[:-5]
			if county[-7:] == ' parish':
				county = county[:-7]
			if county[-8:] == ' borough':
				county = county[:-8]
			if county[-12:] == ' census area':
				county = county[:-12]
			if county[-13:] == ' municipality':
				county = county[:-13]
		assert 'population' not in states[state][county]
		states[state][county]['population'] = {
			"2010": int(re.sub(r",", "", row[-10])),
			# "2011": int(re.sub(r",", "", row[-9])),
			# "2012": int(re.sub(r",", "", row[-8])),
			# "2013": int(re.sub(r",", "", row[-7])),
			# "2014": int(re.sub(r",", "", row[-6])),
			"2015": int(re.sub(r",", "", row[-5])),
			# "2016": int(re.sub(r",", "", row[-4])),
			# "2017": int(re.sub(r",", "", row[-3])),
			# "2018": int(re.sub(r",", "", row[-2])),
			"2019": int(re.sub(r",", "", row[-1]))
		}

	# Make sure we didn't miss any counties.
	for state in states:
		for county in states[state]:
			assert 'population' in states[state][county]

add_population(states)

def add_demographics(states):
	age_code_to_group = {
	  0: "all",
		1: "0-4",
		2: "5-9",
		3: "10-14",
		4: "15-19",
		5: "20-24",
		6: "25-29",
		7: "30-34",
		8: "35-39",
		9: "40-44",
		10: "45-49",
		11: "50-54",
		12: "55-59",
		13: "60-64",
		14: "65-69",
		15: "70-74",
		16: "75-79",
		17: "80-84",
		18: "85+"
	}

	# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2018/cc-est2018-alldata.pdf
	year_code_to_year = {
		 "1": "4/1/2010",
		 "2": "4/1/2010", # sic
		 "3": "7/1/2010",
		 "4": "7/1/2011",
		 "5": "7/1/2012",
		 "6": "7/1/2013",
		 "7": "7/1/2014",
		 "8": "7/1/2015",
		 "9": "7/1/2016",
		"10": "7/1/2017",
		"11": "7/1/2018",
	}
	county_totals = {}
	for state in states:
		county_totals[state] = {}
	# After downloading this file you should open it with a text editor (
	# I use Sublime) and re-encode it as utf8.
	with open(pjoin('data', 'cc-est2018-alldata.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader]
		assert header[:7] == ['SUMLEV', 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR', 'AGEGRP']
		for row in rows:
			state = row[3]
			county = row[4].lower()

			# We only grab the latest year available and ignore the
			# other rows.
			if year_code_to_year[row[5]] != '7/1/2018':
				continue

			age_group = int(row[6])
			if age_group == 0:
				# age group "0" is everyone.  We grab racial data from
				# this row.  The racial break down done by the Census
				# Bureau is... intense, with 73 different columns.  To
				# keep the file size reasonable I don't track them all.

				# We assume this is the first row we see.
				states[state][county]['race_demographics'] = {}
				states[state][county]['age_demographics'] = {}

				# Fortunately the code and data is freely available so
				# it is trivial for you to add more columns if you like!
				states[state][county]['male'] = int(row[8])
				states[state][county]['female'] = int(row[9])

				total = int(row[7])
				# Save for age demographics
				county_totals[state][county] = total

				states[state][county]['race_demographics']['non_hispanic_white_alone_male'] = int(row[34]) / total
				states[state][county]['race_demographics']['non_hispanic_white_alone_female'] = int(row[35]) / total

				states[state][county]['race_demographics']['black_alone_male'] = int(row[12]) / total
				states[state][county]['race_demographics']['black_alone_female'] = int(row[13]) / total

				states[state][county]['race_demographics']['asian_alone_male'] = int(row[16]) / total
				states[state][county]['race_demographics']['asian_alone_female'] = int(row[17]) / total

				states[state][county]['race_demographics']['hispanic_male'] = int(row[56]) / total
				states[state][county]['race_demographics']['hispanic_female'] = int(row[57]) / total

			else:
				states[state][county]['age_demographics'][age_code_to_group[int(row[6])]] = int(row[7]) / county_totals[state][county]

			assert county in states[state]

	for state_name in states:
		for county_name in states[state_name]:
			assert 'race_demographics' in states[state_name][county_name]

add_demographics(states)

def add_cdc_deaths(states):
	cdc_to_census = {
		"Alaska": {
			"anchorage borough": "anchorage municipality",
			"juneau borough": "juneau city and borough",
			"petersburg borough/census area": "petersburg borough",
			"sitka borough": "sitka city and borough",
			"skagway-hoonah-angoon census area" : "skagway municipality",
			"wrangell-petersburg census area": "wrangell city and borough",
			"yakutat borough": "yakutat city and borough",
			# I should figure out why this is correct...
			"wade hampton census area": "kusilvak census area",
			# Renamed in 2008
			"prince of wales-outer ketchikan census area": "prince of wales-hyder census area",
		},
		"Indiana": {
			"de kalb county": "dekalb county",
			"la porte county": "laporte county",
		},
		"New Mexico": {
			"debaca county": "de baca county",
			"dona ana county": "doña ana county",
		},
		"Pennsylvania": {
			"mc kean county": "mckean county",
		},
		"South Dakota": {
			"shannon county": "oglala lakota county",
		},
	}

	# Maps formly independent cities to the counties they
	# now belong to.  This way we can add the deaths from
	# these cities (which the CDC keeps separate, since its
	# data goes back to 1999) to the counties the cities
	# now belong to.
	former_independent_cities_to_counties = {
		"Virginia": {
			"clifton forge city": "alleghany county",
			"bedford city": "bedford county",
		}
	}
	for varname, fn in zip(['deaths', 'suicides', 'firearm suicides'], ["Compressed Mortality, 1999-2016 (all deaths).txt", "Compressed Mortality, 1999-2016 (all suicides).txt", "Compressed Mortality, 1999-2016 (firearm suicides).txt"]):
		with open(pjoin('data', fn), 'r') as f:
			reader = csv.reader(f, delimiter='\t', quotechar='"')
			rows = [row for row in reader]
		header = rows[0]
		rows = rows[1:]
		rows = rows[:rows.index(['---']) - 1]
		former_independent_cities = {}
		for row in rows:
			_, county, _, deaths, population, _ = row
			county = county.lower()
			state = abbreviation_to_name[county.split(', ')[-1].upper()]
			county = ', '.join(county.split(', ')[:-1])

			if county in ['prince of wales-outer ketchikan census area', 'skagway-hoonah-angoon census area', "wrangell-petersburg census area"]:
				continue

			if state in cdc_to_census and county in cdc_to_census[state]:
				county = cdc_to_census[state][county]
			if deaths == 'Suppressed':
				deaths = None

			if state in former_independent_cities_to_counties and county in former_independent_cities_to_counties[state]:
				county = former_independent_cities_to_counties[state][county]
				if state not in former_independent_cities:
					former_independent_cities[state] = {}
				former_independent_cities[state][county] = deaths
				continue
			assert varname not in states[state][county]
			states[state][county][varname] = deaths

		# Add formly independent cities to their respective counties.
		for state in former_independent_cities:
			for county in former_independent_cities[state]:
				# If either value was suppressed, we keep the concatenated
				# value as None.
				if states[state][county][varname] is None:
					continue
				if former_independent_cities[state][county] is None:
					continue
				states[state][county][varname] += former_independent_cities[state][county]

		for state in states:
			for county in states[state]:
				assert varname in states[state][county]

add_cdc_deaths(states)

# Labor force data
# https://www.bls.gov/lau/#cntyaa

def add_labor_force(states):
	bls_to_census = {
		"Alaska": {
			"anchorage borough/municipality": "anchorage municipality",
			"juneau borough/city": "juneau city and borough",
			"sitka borough/city": "sitka city and borough",
			"wrangell borough/city": "wrangell city and borough",
			"yakutat borough/city": "yakutat city and borough",
			# I should figure out why this is correct...
			# "wade hampton census area": "kusilvak census area",
			# Renamed in 2008
			# "prince of wales-outer ketchikan census area": "prince of wales-hyder census area",
		},
		"California": {
			"san francisco county/city": "san francisco county",
		},
		"Colorado": {
			"broomfield county/city": "broomfield county",
		},
		"New Mexico": {
			"dona ana county": "doña ana county",
		},
	}

	with open(pjoin('data', 'laborforce.txt'), 'r') as f:
		lines = f.readlines()
		for line in lines[6:]:
			line = line.strip()
			if len(line) == 0:
				break
			laus_code, state_fips_code, county_fips_code, county_name, year, labor_force, employed, unemployed, unemployment_rate = re.sub(r"  +", "  ", line).split("  ")

			if county_name == "District of Columbia":
				state = "District of Columbia"
				county_name = state.lower()
			else:
				state = county_name.split(', ')[-1]
				if state not in abbreviation_to_name:
					continue
				state = abbreviation_to_name[state]
				county_name = ', '.join(county_name.split(', ')[:-1]).lower()

			if state in not_states:
				continue

			if county_name[-12:] == ' county/city':
				county_name = county_name[:-5]
			if county_name[-12:] == ' county/town':
				county_name = county_name[:-5]
			if state in bls_to_census and county_name in bls_to_census[state]:
				county_name = bls_to_census[state][county_name]

			county = states[state][county_name]

			assert 'labor_force' not in county
			county['labor_force'] = labor_force
			county['employed'] = employed
			county['unemployed'] = unemployed
			county['unemployment_rate'] = unemployment_rate

	# Missing county...
	states["Hawaii"]["kalawao county"]["labor_force"] = None
	states["Hawaii"]["kalawao county"]["employed"] = None
	states["Hawaii"]["kalawao county"]["unemployed"] = None
	states["Hawaii"]["kalawao county"]["unemployment_rate"] = None

	for state in states:
		for county in states[state]:
			assert 'labor_force' in states[state][county]

add_labor_force(states)

def add_fatal_police_shootings(states):
	washingpost_to_census = {
		"Alaska": {
			"anchorage borough": "anchorage municipality",
			"juneau borough": "juneau city and borough",
		},
		"New Mexico": {
			"dona ana county": "doña ana county",
		},
	}

	for varname, fn in zip(
		['fatal_police_shootings', 'unarmed_fatal_police_shootings', 'fatal_police_shootings_where_victim_had_firearm'],
		['shootings-by-county.json', 'unarmed-shootings-by-county.json', 'shootings-by-county-where-victim-had-firearm.json']):
		with open(pjoin('generated', fn), 'r') as f:
			shootings = json.load(f)

			for k in shootings:
				state_name = abbreviation_to_name[k[-2:].upper()]
				state = states[state_name]

				county_name = k[:-4]
				if state_name in washingpost_to_census and county_name in washingpost_to_census[state_name]:
					county_name = washingpost_to_census[state_name][county_name]
				elif county_name not in state:
					if county_name[-7:] == ' county':
						county_name = county_name[:-7]
					if county_name[-8:] == ' borough':
						county_name = county_name[:-8]

				state[county_name][varname] = shootings[k]

		# If a county is never present in the Washington Post database,
		# this is because it has no recorded fatal police shootings.
		for state in states:
			for county in states[state]:
				if varname not in states[state][county]:
					states[state][county][varname] = 0


add_fatal_police_shootings(states)


with open('states.json', 'w+') as f:
	json.dump(states, f, indent=1)

