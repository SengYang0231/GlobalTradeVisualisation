"""
FIT2179 A2 — ISO Numeric Lookup Generator
Generates data/iso_numeric.csv for Chart 1 choropleth join.
world-110m.json uses numeric ISO codes; our CSVs use alpha-3.
This file bridges the two.

Run once: python prep_iso_lookup.py
Output:   data/iso_numeric.csv (columns: alpha3, numeric)
"""

import pandas as pd, os

os.makedirs("data", exist_ok=True)

# ISO 3166-1: alpha-3 → numeric mapping (all 249 countries/territories)
ISO = {
    "AFG":4,"ALB":8,"DZA":12,"ASM":16,"AND":20,"AGO":24,"AIA":660,
    "ATG":28,"ARG":32,"ARM":51,"ABW":533,"AUS":36,"AUT":40,"AZE":31,
    "BHS":44,"BHR":48,"BGD":50,"BRB":52,"BLR":112,"BEL":56,"BLZ":84,
    "BEN":204,"BMU":60,"BTN":64,"BOL":68,"BIH":70,"BWA":72,"BRA":76,
    "BRN":96,"BGR":100,"BFA":854,"BDI":108,"CPV":132,"KHM":116,
    "CMR":120,"CAN":124,"CAF":140,"TCD":148,"CHL":152,"CHN":156,
    "COL":170,"COM":174,"COD":180,"COG":178,"COK":184,"CRI":188,
    "CIV":384,"HRV":191,"CUB":192,"CYP":196,"CZE":203,"DNK":208,
    "DJI":262,"DMA":212,"DOM":214,"ECU":218,"EGY":818,"SLV":222,
    "GNQ":226,"ERI":232,"EST":233,"SWZ":748,"ETH":231,"FJI":242,
    "FIN":246,"FRA":250,"GAB":266,"GMB":270,"GEO":268,"DEU":276,
    "GHA":288,"GRC":300,"GRD":308,"GTM":320,"GIN":324,"GNB":624,
    "GUY":328,"HTI":332,"HND":340,"HKG":344,"HUN":348,"ISL":352,
    "IND":356,"IDN":360,"IRN":364,"IRQ":368,"IRL":372,"ISR":376,
    "ITA":380,"JAM":388,"JPN":392,"JOR":400,"KAZ":398,"KEN":404,
    "KIR":296,"PRK":408,"KOR":410,"KWT":414,"KGZ":417,"LAO":418,
    "LVA":428,"LBN":422,"LSO":426,"LBR":430,"LBY":434,"LIE":438,
    "LTU":440,"LUX":442,"MAC":446,"MDG":450,"MWI":454,"MYS":458,
    "MDV":462,"MLI":466,"MLT":470,"MHL":584,"MRT":478,"MUS":480,
    "MEX":484,"FSM":583,"MDA":498,"MCO":492,"MNG":496,"MNE":499,
    "MAR":504,"MOZ":508,"MMR":104,"NAM":516,"NRU":520,"NPL":524,
    "NLD":528,"NZL":554,"NIC":558,"NER":562,"NGA":566,"MKD":807,
    "NOR":578,"OMN":512,"PAK":586,"PLW":585,"PAN":591,"PNG":598,
    "PRY":600,"PER":604,"PHL":608,"POL":616,"PRT":620,"QAT":634,
    "ROU":642,"RUS":643,"RWA":646,"KNA":659,"LCA":662,"VCT":670,
    "WSM":882,"SMR":674,"STP":678,"SAU":682,"SEN":686,"SRB":688,
    "SYC":690,"SLE":694,"SGP":702,"SVK":703,"SVN":705,"SLB":90,
    "SOM":706,"ZAF":710,"SSD":728,"ESP":724,"LKA":144,"SDN":729,
    "SUR":740,"SWE":752,"CHE":756,"SYR":760,"TWN":158,"TJK":762,
    "TZA":834,"THA":764,"TLS":626,"TGO":768,"TON":776,"TTO":780,
    "TUN":788,"TUR":792,"TKM":795,"TUV":798,"UGA":800,"UKR":804,
    "ARE":784,"GBR":826,"USA":840,"URY":858,"UZB":860,"VUT":548,
    "VEN":862,"VNM":704,"YEM":887,"ZMB":894,"ZWE":716,
    # Extra territories sometimes in TopoJSON
    "GUF":254,"PYF":258,"GLP":312,"MTQ":474,"REU":638,"MYT":175,
    "NCL":540,"WLF":876,"SPM":666,"ESH":732,"PSE":275,"SJM":744,
    "ALA":248,"FLK":238,"GIB":292,"GGY":831,"IMN":833,"JEY":832,
    "SHN":654,"TKL":772,"CXR":162,"CCK":166,"NFK":574,"PN":612,
    "HMD":334,"IOT":86,"ATF":260,"UMI":581,"VIR":850,"PRI":630,
    "GUM":316,"ASM":16,"MNP":580,
}

df = pd.DataFrame([
    {"alpha3": a3, "numeric": num}
    for a3, num in ISO.items()
])

df.to_csv("data/iso_numeric.csv", index=False)
print(f"Saved {len(df)} rows → data/iso_numeric.csv")
print(df[df["alpha3"] == "MYS"])   # verify Malaysia
