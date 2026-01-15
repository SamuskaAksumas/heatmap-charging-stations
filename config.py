p                           = dict()
p['picklefolder']           = 'pickles'
# -----------------------------------

p['geocode']                = 'PLZ'

p["file_lstations"]         = "Ladesaeulenregister.csv"
# p["file_buildings"]         = "gebaeude.csv"
p["file_residents"]         = "plz_einwohner.csv"
# p["file_amounttraf"]        = "Verkehrsaufkommen.csv"

p["file_geodat_plz"]       = "geodata_berlin_plz.csv"
p["file_geodat_dis"]       = "geodata_berlin_dis.csv"

# p["gebaeude_filter"]        = ["Freistehendes Einzelgebäude", "Doppelhaushälfte"]

# -----------------------------------
# Admin settings
# NOTE: In production, use environment variables or .streamlit/secrets.toml
p["admin_password"]         = "advanced"

# -----------------------------------
pdict = p.copy()

