from datetime import date
from sqlalchemy.orm import Session
from app.models import Agency, User, Destination, Flight, Hotel, Package
from app.services.auth_service import hash_password


DEPARTURE_HUBS = [
    ("Paris", "CDG", "europe"),
    ("Lyon", "LYS", "europe"),
    ("Marseille", "MRS", "europe"),
    ("Bruxelles", "BRU", "europe"),
    ("Cotonou", "COO", "afrique"),
    ("Abidjan", "ABJ", "afrique"),
    ("Dakar", "DSS", "afrique"),
    ("Casablanca", "CMN", "afrique"),
    ("Lome", "LFW", "afrique"),
    ("Douala", "DLA", "afrique"),
    ("Nairobi", "NBO", "afrique"),
    ("Le Caire", "CAI", "afrique"),
    ("Dubai", "DXB", "moyen_orient"),
    ("Istanbul", "IST", "europe"),
    ("Londres", "LHR", "europe"),
    ("New York", "JFK", "amerique"),
]

DESTINATIONS_DATA = [
    ("Marrakech", "Maroc",
     "Ville imperiale aux mille couleurs, Marrakech seduit par ses souks animes, ses palais somptueux et sa gastronomie genereuse.",
     "photo-1597212618440-806262de4f6b",
     ["Medina et souks", "Jardins de Majorelle", "Gastronomie", "Hammams traditionnels"],
     "Octobre a avril", "25C", "3h30", "culture", "RAK"),
    ("Lisbonne", "Portugal",
     "Capitale lumineuse du Portugal, Lisbonne charme par ses ruelles pavees, ses tramways historiques et ses pasteis de nata.",
     "photo-1585208798174-6cedd86e019a",
     ["Quartier de l'Alfama", "Tramway 28", "Pasteis de Belem", "Bord de mer a Cascais"],
     "Avril a octobre", "22C", "2h30", "culture", "LIS"),
    ("Bali", "Indonesie",
     "Ile des dieux, Bali offre des rizieres en terrasses spectaculaires, des temples millenaires et des plages de reve.",
     "photo-1537996194471-e657df975ab4",
     ["Rizieres de Tegallalang", "Temple d'Uluwatu", "Plages de Seminyak", "Snorkeling"],
     "Mai a septembre", "28C", "16h", "plage", "DPS"),
    ("Santorin", "Grece",
     "Joyau des Cyclades, Santorin enchante avec ses maisons blanches et bleues perchees sur la caldeira.",
     "photo-1613395877344-13d4a8e0d49e",
     ["Coucher de soleil a Oia", "Plage Rouge", "Vins locaux", "Villages perches"],
     "Mai a octobre", "26C", "3h30", "romantique", "JTR"),
    ("Dubai", "Emirats Arabes Unis",
     "Metropole futuriste entre desert et mer, Dubai impressionne par son architecture audacieuse.",
     "photo-1512453979798-5ea266f8880c",
     ["Burj Khalifa", "Desert safari", "Shopping", "Plages"],
     "Novembre a mars", "30C", "6h30", "aventure", "DXB"),
    ("Cotonou", "Benin",
     "Capitale economique du Benin, Cotonou melange marches colores, plages tropicales et culture vaudou fascinante.",
     "photo-1580060839134-75a5edca2e99",
     ["Marche Dantokpa", "Route des Peches", "Ganvie cite lacustre", "Culture vaudou"],
     "Novembre a mars", "28C", "6h", "culture", "COO"),
    ("Abidjan", "Cote d'Ivoire",
     "Perle des lagunes, Abidjan est une metropole vibrante alliant modernite, culture et plages magnifiques.",
     "photo-1504233529578-6d46baba6d34",
     ["Plateau quartier d'affaires", "Plage de Bassam", "Parc du Banco", "Marche de Cocody"],
     "Novembre a mars", "27C", "6h30", "culture", "ABJ"),
    ("Dakar", "Senegal",
     "Capitale du Senegal, Dakar seduit par ses traditions africaines, sa scene artistique et l'ile de Goree.",
     "photo-1580060839134-75a5edca2e99",
     ["Ile de Goree", "Lac Rose", "Monument de la Renaissance", "Marche Sandaga"],
     "Novembre a mai", "26C", "5h30", "culture", "DSS"),
    ("Zanzibar", "Tanzanie",
     "Archipel paradisiaque de l'ocean Indien, Zanzibar offre plages de sable blanc, epices et vieille ville UNESCO.",
     "photo-1548574505-5e239809ee19",
     ["Stone Town", "Plages de Nungwi", "Route des epices", "Snorkeling"],
     "Juin a octobre", "28C", "10h", "plage", "ZNZ"),
    ("Maldives", "Maldives",
     "Paradis sur terre, les Maldives offrent des lagons turquoise, des bungalows sur pilotis et une vie marine exceptionnelle.",
     "photo-1514282401047-d79a71a590e8",
     ["Bungalows sur pilotis", "Plongee sous-marine", "Lagons turquoise", "Couchers de soleil"],
     "Novembre a avril", "29C", "10h30", "plage", "MLE"),
    ("Paris", "France",
     "Ville lumiere, Paris fascine par ses monuments iconiques, sa gastronomie raffinee et son art de vivre.",
     "photo-1502602898657-3e91760cbb34",
     ["Tour Eiffel", "Louvre", "Champs-Elysees", "Montmartre"],
     "Avril a octobre", "18C", "-", "culture", "CDG"),
    ("Pekin", "Chine",
     "Capitale millenaire de la Chine, Pekin impressionne par la Grande Muraille et la Cite Interdite.",
     "photo-1508804185872-d7badad00f7d",
     ["Grande Muraille", "Cite Interdite", "Temple du Ciel", "Canard laque"],
     "Avril a octobre", "20C", "10h", "culture", "PEK"),
    ("Shanghai", "Chine",
     "Metropole futuriste, Shanghai allie gratte-ciel spectaculaires, jardins classiques et scene culinaire exceptionnelle.",
     "photo-1474181628-2a4727e59e4f",
     ["Le Bund", "Yu Garden", "Tour de Shanghai", "French Concession"],
     "Mars a mai", "22C", "11h", "culture", "PVG"),
    ("Tokyo", "Japon",
     "Capitale du Japon, Tokyo mele tradition et ultra-modernite avec ses temples, quartiers neons et cuisine raffinee.",
     "photo-1540959733332-eab4deabeeaf",
     ["Shibuya Crossing", "Temple Senso-ji", "Tsukiji Market", "Mont Fuji"],
     "Mars a mai", "20C", "12h", "culture", "NRT"),
    ("Bangkok", "Thailande",
     "Ville des anges, Bangkok envoute par ses temples dores, sa street food legendaire et ses marches flottants.",
     "photo-1508009603885-50cf7c579365",
     ["Grand Palais", "Wat Pho", "Marche flottant", "Street food"],
     "Novembre a fevrier", "30C", "11h", "culture", "BKK"),
    ("Singapour", "Singapour",
     "Cite-Etat ultramoderne, Singapour impressionne par ses jardins futuristes et sa diversite culinaire.",
     "photo-1525625293386-3f8f99389edd",
     ["Gardens by the Bay", "Marina Bay Sands", "Little India", "Hawker Centers"],
     "Toute l'annee", "30C", "12h", "culture", "SIN"),
    ("Hanoi", "Vietnam",
     "Capitale du Vietnam, Hanoi charme par son vieux quartier, ses lacs paisibles et sa cuisine de rue.",
     "photo-1583417319070-4a69db38a482",
     ["Vieux quartier", "Lac Hoan Kiem", "Baie d'Ha Long", "Pho"],
     "Octobre a avril", "24C", "11h", "culture", "HAN"),
    ("Seoul", "Coree du Sud",
     "Capitale dynamique, Seoul allie palais royaux, quartiers trendy, K-culture et gastronomie incomparable.",
     "photo-1534274988757-a28bf1a57c17",
     ["Palais Gyeongbokgung", "Quartier Gangnam", "Bukchon Hanok", "Kimchi et BBQ"],
     "Avril a juin", "18C", "11h30", "culture", "ICN"),
    ("Goa", "Inde",
     "Ancienne colonie portugaise, Goa melange plages dorees, architecture coloniale et spiritualite.",
     "photo-1512343879784-a960bf40e7f2",
     ["Plages de Palolem", "Eglises de Old Goa", "Marches nocturnes", "Yoga retreats"],
     "Novembre a mars", "30C", "10h", "plage", "GOI"),
    ("Le Caire", "Egypte",
     "Capitale de l'Egypte, Le Caire fascine par les pyramides de Gizeh, le Sphinx et le musee des antiquites.",
     "photo-1539650116574-8efeb43e2750",
     ["Pyramides de Gizeh", "Sphinx", "Musee egyptien", "Khan el-Khalili"],
     "Octobre a avril", "25C", "4h30", "culture", "CAI"),
    ("Le Cap", "Afrique du Sud",
     "Ville spectaculaire entre ocean et montagne, Le Cap offre paysages epoustouflants et culture vibrante.",
     "photo-1580060839134-75a5edca2e99",
     ["Table Mountain", "Cap de Bonne Esperance", "Robben Island", "Vignobles"],
     "Octobre a mars", "24C", "11h", "aventure", "CPT"),
    ("Nairobi", "Kenya",
     "Porte d'entree des safaris africains, Nairobi combine vie urbaine moderne et nature sauvage.",
     "photo-1547471080-7cc2caa01a7e",
     ["Safari Masai Mara", "Parc national de Nairobi", "Karen Blixen Museum", "Giraffe Centre"],
     "Juillet a octobre", "22C", "8h30", "aventure", "NBO"),
    ("Tunis", "Tunisie",
     "Capitale de la Tunisie, Tunis allie medina historique, ruines de Carthage et plages mediterraneennes.",
     "photo-1590073242678-70ee3fc28e8e",
     ["Medina de Tunis", "Ruines de Carthage", "Sidi Bou Said", "Musee du Bardo"],
     "Avril a octobre", "26C", "2h30", "culture", "TUN"),
    ("Ile Maurice", "Ile Maurice",
     "Joyau de l'ocean Indien, l'Ile Maurice offre plages paradisiaques, lagons turquoise et forets tropicales.",
     "photo-1544550581-5f7ceaf7f992",
     ["Plage de Trou aux Biches", "Chamarel", "Ile aux Cerfs", "Port Louis"],
     "Mai a novembre", "25C", "11h", "plage", "MRU"),
    ("Antananarivo", "Madagascar",
     "Capitale sur les hauts plateaux, Antananarivo est la porte d'entree d'une biodiversite unique au monde.",
     "photo-1580060839134-75a5edca2e99",
     ["Allee des Baobabs", "Parc de l'Isalo", "Lemuriens", "Nosy Be"],
     "Avril a octobre", "20C", "11h", "aventure", "TNR"),
    ("Lome", "Togo",
     "Capitale du Togo, Lome seduit par ses plages, son grand marche et sa culture fetichiste unique.",
     "photo-1580060839134-75a5edca2e99",
     ["Grand Marche", "Plage de Lome", "Marche des Feticheurs", "Kpalime"],
     "Novembre a mars", "28C", "6h", "culture", "LFW"),
    ("Accra", "Ghana",
     "Capitale du Ghana, Accra vibre au rythme de sa scene musicale, ses plages et ses forts historiques.",
     "photo-1580060839134-75a5edca2e99",
     ["Cape Coast Castle", "Plage de Labadi", "Marche de Makola", "Parc national de Kakum"],
     "Novembre a mars", "28C", "6h30", "culture", "ACC"),
    ("Rome", "Italie",
     "Ville eternelle, Rome enchante par ses vestiges antiques, sa cuisine divine et son art de vivre.",
     "photo-1552832230-c0197dd311b5",
     ["Colisee", "Vatican", "Fontaine de Trevi", "Trastevere"],
     "Avril a octobre", "24C", "2h", "culture", "FCO"),
    ("Barcelone", "Espagne",
     "Ville catalane, Barcelone brille par l'architecture de Gaudi, ses plages et sa vie nocturne.",
     "photo-1583422409516-2895a77efded",
     ["Sagrada Familia", "Parc Guell", "Las Ramblas", "Plage de Barceloneta"],
     "Mai a septembre", "25C", "2h", "culture", "BCN"),
    ("Amsterdam", "Pays-Bas",
     "Cite des canaux, Amsterdam charme par ses musees de renommee mondiale, ses velos et son ambiance unique.",
     "photo-1534351590666-13e3e96b5017",
     ["Musee Van Gogh", "Canaux", "Rijksmuseum", "Marche aux fleurs"],
     "Avril a septembre", "17C", "1h20", "culture", "AMS"),
    ("Prague", "Republique Tcheque",
     "Ville aux cent clochers, Prague seduit par son architecture medievale et ses ponts romantiques.",
     "photo-1541849546-216549ae216d",
     ["Pont Charles", "Chateau de Prague", "Place de la Vieille Ville", "Bieres artisanales"],
     "Avril a octobre", "16C", "1h45", "culture", "PRG"),
    ("Londres", "Royaume-Uni",
     "Capitale cosmopolite, Londres impressionne par ses monuments iconiques et sa diversite culturelle.",
     "photo-1513635269975-59663e0ac1ad",
     ["Big Ben", "British Museum", "Tower Bridge", "Camden Market"],
     "Mai a septembre", "18C", "1h15", "culture", "LHR"),
    ("Istanbul", "Turquie",
     "Ville entre deux continents, Istanbul fascine par ses mosquees majestueuses et le Bosphore.",
     "photo-1524231757912-21f4fe3a7200",
     ["Sainte-Sophie", "Grand Bazar", "Bosphore", "Palais de Topkapi"],
     "Avril a octobre", "22C", "3h30", "culture", "IST"),
    ("Dubrovnik", "Croatie",
     "Perle de l'Adriatique, Dubrovnik enchante par ses remparts medievaux et ses plages cristallines.",
     "photo-1555990793-da11153b2473",
     ["Remparts", "Vieille ville", "Ile de Lokrum", "Plages"],
     "Mai a septembre", "26C", "2h30", "romantique", "DBV"),
    ("Reykjavik", "Islande",
     "Capitale la plus septentrionale, Reykjavik est la porte des aurores boreales et glaciers d'Islande.",
     "photo-1504829857797-ddff29c27927",
     ["Aurores boreales", "Blue Lagoon", "Cercle d'Or", "Geysers"],
     "Septembre a mars", "5C", "3h30", "aventure", "KEF"),
    ("New York", "Etats-Unis",
     "La ville qui ne dort jamais, New York fascine par ses gratte-ciel et son energie incomparable.",
     "photo-1496442226666-8d4d0e62e6e9",
     ["Statue de la Liberte", "Central Park", "Times Square", "Brooklyn Bridge"],
     "Avril a juin", "18C", "8h", "culture", "JFK"),
    ("Cancun", "Mexique",
     "Station balneaire mythique, Cancun offre plages turquoise, ruines mayas et vie nocturne effervescente.",
     "photo-1552074284-5e88ef1aef18",
     ["Chichen Itza", "Plage de Tulum", "Isla Mujeres", "Cenotes"],
     "Decembre a avril", "28C", "10h", "plage", "CUN"),
    ("La Havane", "Cuba",
     "Capitale intemporelle, La Havane envoute par ses voitures vintage, sa musique et son architecture coloniale.",
     "photo-1500759285222-a95626b934cb",
     ["Vieille Havane", "Malecon", "Voitures vintage", "Mojitos et salsa"],
     "Novembre a avril", "27C", "10h30", "culture", "HAV"),
    ("Rio de Janeiro", "Bresil",
     "Ville merveilleuse, Rio enchante par ses plages iconiques, le Pain de Sucre et le Christ Redempteur.",
     "photo-1483729558449-99ef09a8c325",
     ["Christ Redempteur", "Copacabana", "Pain de Sucre", "Carnaval"],
     "Decembre a mars", "28C", "11h30", "plage", "GIG"),
    ("Buenos Aires", "Argentine",
     "Paris de l'Amerique du Sud, Buenos Aires seduit par son tango, son architecture et sa passion.",
     "photo-1589909202802-8f4aadce1849",
     ["La Boca", "Tango a San Telmo", "Recoleta", "Steaks et Malbec"],
     "Octobre a mars", "24C", "13h", "culture", "EZE"),
    ("Punta Cana", "Republique Dominicaine",
     "Paradis caribeen, Punta Cana offre des plages de cocotiers interminables et des resorts all-inclusive.",
     "photo-1548574505-5e239809ee19",
     ["Plage de Bavaro", "Ile Saona", "Golf", "Catamaran"],
     "Decembre a avril", "28C", "9h", "plage", "PUJ"),
    ("Cartagena", "Colombie",
     "Joyau colonial de la Colombie, Cartagena charme par ses rues colorees et ses fortifications.",
     "photo-1580060839134-75a5edca2e99",
     ["Vieille ville fortifiee", "Iles du Rosaire", "Castillo San Felipe", "Cuisine caribeenne"],
     "Decembre a avril", "30C", "10h30", "culture", "CTG"),
    ("Guadeloupe", "France (Outre-mer)",
     "Papillon caribeen, la Guadeloupe offre plages paradisiaques, volcans et culture creole authentique.",
     "photo-1548574505-5e239809ee19",
     ["Plage de Grande Anse", "Volcan la Soufriere", "Chutes du Carbet", "Pointe-a-Pitre"],
     "Decembre a mai", "27C", "8h30", "plage", "PTP"),
    ("Martinique", "France (Outre-mer)",
     "Ile aux fleurs, la Martinique seduit par ses plages, sa montagne Pelee et son rhum.",
     "photo-1548574505-5e239809ee19",
     ["Montagne Pelee", "Plage des Salines", "Distilleries de rhum", "Jardin de Balata"],
     "Decembre a mai", "27C", "8h30", "plage", "FDF"),
    ("Sydney", "Australie",
     "Ville iconique, Sydney impressionne par son Opera, Harbour Bridge et ses plages.",
     "photo-1506973035872-a4ec16b8e8d9",
     ["Opera de Sydney", "Harbour Bridge", "Bondi Beach", "Blue Mountains"],
     "Octobre a mars", "24C", "22h", "culture", "SYD"),
    ("La Reunion", "France (Outre-mer)",
     "Ile intense de l'ocean Indien, La Reunion offre volcans actifs, cirques majestueux et nature spectaculaire.",
     "photo-1544550581-5f7ceaf7f992",
     ["Piton de la Fournaise", "Cirque de Mafate", "Plage de l'Hermitage", "Randonnees"],
     "Mai a novembre", "24C", "11h", "aventure", "RUN"),
    ("Seychelles", "Seychelles",
     "Archipel de reve, les Seychelles offrent des plages de granit uniques et eaux cristallines.",
     "photo-1544550581-5f7ceaf7f992",
     ["Anse Source d'Argent", "Vallee de Mai", "Plongee", "Tortues geantes"],
     "Avril a mai", "28C", "10h", "plage", "SEZ"),
    ("Oman", "Oman",
     "Sultanat d'Oman, entre montagnes, desert et mer, offre wadis spectaculaires et hospitalite legendaire.",
     "photo-1512453979798-5ea266f8880c",
     ["Grande Mosquee de Mascate", "Wadi Shab", "Desert de Wahiba", "Fjords de Musandam"],
     "Octobre a mars", "28C", "7h", "aventure", "MCT"),
    ("Douala", "Cameroun",
     "Capitale economique du Cameroun, porte d'entree vers le Mont Cameroun et les plages de Kribi.",
     "photo-1580060839134-75a5edca2e99",
     ["Mont Cameroun", "Plages de Kribi", "Marche Central", "Chutes de la Lobe"],
     "Novembre a fevrier", "27C", "6h", "aventure", "DLA"),
    ("Casablanca", "Maroc",
     "Metropole du Maroc, Casablanca allie modernite et tradition avec sa mosquee Hassan II.",
     "photo-1597212618440-806262de4f6b",
     ["Mosquee Hassan II", "Corniche", "Quartier des Habous", "Art deco"],
     "Avril a octobre", "22C", "3h", "culture", "CMN"),
    ("Nosy Be", "Madagascar",
     "Ile aux parfums, Nosy Be offre plages paradisiaques, recifs coralliens et nature luxuriante.",
     "photo-1544550581-5f7ceaf7f992",
     ["Plage d'Andilana", "Reserve de Lokobe", "Ile de Nosy Komba", "Plongee"],
     "Avril a novembre", "28C", "13h", "plage", "NOS"),
]

AIRLINES = {
    "afrique_europe": [
        ("Air France", "AF", {"cabin": "12 kg", "checked": "23 kg"}),
        ("Ethiopian Airlines", "ET", {"cabin": "7 kg", "checked": "23 kg"}),
        ("Royal Air Maroc", "AT", {"cabin": "10 kg", "checked": "23 kg"}),
        ("Turkish Airlines", "TK", {"cabin": "8 kg", "checked": "23 kg"}),
    ],
    "afrique_afrique": [
        ("Ethiopian Airlines", "ET", {"cabin": "7 kg", "checked": "23 kg"}),
        ("Kenya Airways", "KQ", {"cabin": "7 kg", "checked": "23 kg"}),
        ("ASKY Airlines", "KP", {"cabin": "10 kg", "checked": "23 kg"}),
        ("Air Cote d'Ivoire", "HF", {"cabin": "10 kg", "checked": "23 kg"}),
        ("Royal Air Maroc", "AT", {"cabin": "10 kg", "checked": "23 kg"}),
    ],
    "europe_europe": [
        ("Air France", "AF", {"cabin": "12 kg", "checked": "23 kg"}),
        ("easyJet", "U2", {"cabin": "15 kg"}),
        ("Transavia", "TO", {"cabin": "10 kg"}),
        ("Vueling", "VY", {"cabin": "10 kg"}),
    ],
    "europe_asie": [
        ("Air France", "AF", {"cabin": "12 kg", "checked": "23 kg"}),
        ("Turkish Airlines", "TK", {"cabin": "8 kg", "checked": "23 kg"}),
        ("Emirates", "EK", {"cabin": "7 kg", "checked": "30 kg"}),
        ("Singapore Airlines", "SQ", {"cabin": "7 kg", "checked": "30 kg"}),
    ],
    "europe_amerique": [
        ("Air France", "AF", {"cabin": "12 kg", "checked": "23 kg"}),
        ("Air Caraibes", "TX", {"cabin": "12 kg", "checked": "23 kg"}),
        ("Corsair", "SS", {"cabin": "10 kg", "checked": "23 kg"}),
        ("LEVEL", "IB", {"cabin": "10 kg"}),
    ],
    "europe_ocean_indien": [
        ("Air France", "AF", {"cabin": "12 kg", "checked": "23 kg"}),
        ("Emirates", "EK", {"cabin": "7 kg", "checked": "30 kg"}),
        ("Turkish Airlines", "TK", {"cabin": "8 kg", "checked": "23 kg"}),
        ("Air Austral", "UU", {"cabin": "10 kg", "checked": "23 kg"}),
    ],
    "moyen_orient": [
        ("Emirates", "EK", {"cabin": "7 kg", "checked": "30 kg"}),
        ("Turkish Airlines", "TK", {"cabin": "8 kg", "checked": "23 kg"}),
        ("Qatar Airways", "QR", {"cabin": "7 kg", "checked": "30 kg"}),
        ("Oman Air", "WY", {"cabin": "7 kg", "checked": "30 kg"}),
    ],
}


def _get_route_airlines(dep_region, dest_region):
    if dep_region == "afrique" and dest_region == "afrique":
        return AIRLINES["afrique_afrique"]
    if dep_region == "afrique" and dest_region == "europe":
        return AIRLINES["afrique_europe"]
    if dep_region == "europe" and dest_region == "afrique":
        return AIRLINES["afrique_europe"]
    if dep_region == "europe" and dest_region == "europe":
        return AIRLINES["europe_europe"]
    if dep_region in ("europe", "afrique") and dest_region == "asie":
        return AIRLINES["europe_asie"]
    if dep_region in ("europe", "afrique") and dest_region == "amerique":
        return AIRLINES["europe_amerique"]
    if dest_region == "ocean_indien":
        return AIRLINES["europe_ocean_indien"]
    if dest_region == "moyen_orient" or dep_region == "moyen_orient":
        return AIRLINES["moyen_orient"]
    return AIRLINES["afrique_europe"]


def _dest_region(country):
    asia = ["Indonesie", "Chine", "Japon", "Thailande", "Singapour", "Vietnam", "Coree du Sud", "Inde"]
    amerique = ["Etats-Unis", "Mexique", "Cuba", "Bresil", "Argentine", "Republique Dominicaine", "Colombie"]
    ocean_indien = ["Maldives", "Ile Maurice", "Madagascar", "Seychelles"]
    moyen_orient = ["Emirats Arabes Unis", "Oman"]
    afrique = ["Maroc", "Benin", "Cote d'Ivoire", "Senegal", "Tanzanie", "Egypte",
               "Afrique du Sud", "Kenya", "Tunisie", "Togo", "Ghana", "Cameroun"]
    dom_tom = ["France (Outre-mer)"]
    if country in asia:
        return "asie"
    if country in amerique:
        return "amerique"
    if country in ocean_indien:
        return "ocean_indien"
    if country in moyen_orient:
        return "moyen_orient"
    if country in afrique:
        return "afrique"
    if country in dom_tom:
        return "amerique"
    return "europe"


def _flight_duration(dep_region, dest_region):
    matrix = {
        ("europe", "europe"): (90, 0),
        ("europe", "afrique"): (300, 0),
        ("europe", "asie"): (660, 1),
        ("europe", "amerique"): (510, 0),
        ("europe", "ocean_indien"): (600, 1),
        ("europe", "moyen_orient"): (360, 0),
        ("afrique", "afrique"): (240, 0),
        ("afrique", "europe"): (300, 0),
        ("afrique", "asie"): (720, 1),
        ("afrique", "amerique"): (660, 1),
        ("afrique", "ocean_indien"): (360, 1),
        ("afrique", "moyen_orient"): (420, 1),
        ("moyen_orient", "asie"): (360, 0),
        ("moyen_orient", "afrique"): (420, 1),
        ("moyen_orient", "europe"): (360, 0),
        ("moyen_orient", "amerique"): (780, 1),
        ("moyen_orient", "ocean_indien"): (300, 0),
        ("moyen_orient", "moyen_orient"): (120, 0),
        ("amerique", "europe"): (480, 0),
        ("amerique", "afrique"): (600, 1),
        ("amerique", "asie"): (840, 1),
        ("amerique", "amerique"): (300, 0),
        ("amerique", "ocean_indien"): (780, 1),
        ("amerique", "moyen_orient"): (660, 1),
    }
    key = (dep_region, dest_region)
    if key in matrix:
        return matrix[key]
    rev = (dest_region, dep_region)
    if rev in matrix:
        return matrix[rev]
    return (480, 1)


def _base_price(dep_region, dest_region):
    matrix = {
        ("europe", "europe"): 89,
        ("europe", "afrique"): 289,
        ("europe", "asie"): 449,
        ("europe", "amerique"): 349,
        ("europe", "ocean_indien"): 489,
        ("europe", "moyen_orient"): 299,
        ("afrique", "afrique"): 149,
        ("afrique", "europe"): 289,
        ("afrique", "asie"): 549,
        ("afrique", "amerique"): 499,
        ("afrique", "ocean_indien"): 349,
        ("afrique", "moyen_orient"): 349,
        ("moyen_orient", "asie"): 249,
        ("moyen_orient", "afrique"): 349,
        ("moyen_orient", "europe"): 299,
        ("moyen_orient", "amerique"): 549,
        ("moyen_orient", "ocean_indien"): 249,
        ("moyen_orient", "moyen_orient"): 99,
        ("amerique", "europe"): 349,
        ("amerique", "afrique"): 499,
        ("amerique", "asie"): 599,
        ("amerique", "amerique"): 199,
        ("amerique", "ocean_indien"): 649,
        ("amerique", "moyen_orient"): 549,
    }
    key = (dep_region, dest_region)
    if key in matrix:
        return matrix[key]
    rev = (dest_region, dep_region)
    if rev in matrix:
        return matrix[rev]
    return 399


HOTELS_BY_DESTINATION = {
    "Marrakech": [
        ("Riad Les Orangers", 4, "Medina", "Riad authentique au coeur de la medina avec patio et piscine", ["Piscine", "Wifi", "Climatisation", "Restaurant", "Hammam", "Terrasse"], "petit-dejeuner", 85),
        ("Atlas Medina & Spa", 5, "Gueliz", "Hotel 5 etoiles avec spa, piscine et vue sur l'Atlas", ["Spa", "Piscine", "Wifi", "Restaurant gastronomique", "Salle de sport", "Bar"], "demi-pension", 155),
    ],
    "Lisbonne": [
        ("Hotel Alfama Terrace", 4, "Alfama", "Hotel boutique avec terrasse panoramique sur le Tage", ["Wifi", "Terrasse", "Bar", "Concierge", "Climatisation"], "petit-dejeuner", 110),
        ("Lisbon Central Hostel+", 2, "Baixa", "Hebergement moderne en plein centre", ["Wifi", "Cuisine commune", "Terrasse"], "petit-dejeuner", 45),
    ],
    "Bali": [
        ("Ubud Rice Terrace Villa", 4, "Ubud", "Villa avec vue sur les rizieres et piscine a debordement", ["Piscine a debordement", "Spa", "Wifi", "Restaurant", "Yoga"], "petit-dejeuner", 75),
        ("Seminyak Beach Resort", 5, "Seminyak", "Resort en bord de mer avec acces direct a la plage", ["Plage privee", "3 piscines", "Spa", "4 restaurants", "Bar de plage", "Wifi"], "demi-pension", 120),
    ],
    "Santorin": [
        ("Caldera Sunset Suites", 5, "Oia", "Suites avec piscine privee et vue sur la caldeira", ["Piscine privee", "Wifi", "Vue caldeira", "Jacuzzi", "Concierge"], "petit-dejeuner", 280),
        ("Fira Blue Rooms", 3, "Fira", "Chambres confortables avec vue mer", ["Wifi", "Climatisation", "Vue mer", "Terrasse commune"], "petit-dejeuner", 95),
    ],
    "Dubai": [
        ("Marina Bay Hotel", 5, "Dubai Marina", "Hotel luxueux face a la Marina avec plage privee", ["Plage privee", "Piscine", "Spa", "6 restaurants", "Salle de sport", "Wifi"], "petit-dejeuner", 195),
        ("Downtown Suites", 4, "Downtown Dubai", "Suites modernes pres du Burj Khalifa", ["Piscine", "Wifi", "Restaurant", "Vue Burj Khalifa", "Salle de sport"], "petit-dejeuner", 145),
    ],
    "Cotonou": [
        ("Hotel du Lac", 4, "Cotonou Centre", "Hotel confortable au bord du lac Nokoue", ["Piscine", "Wifi", "Restaurant", "Terrasse", "Climatisation"], "petit-dejeuner", 65),
        ("Azalai Hotel", 4, "Cadjehoun", "Hotel moderne avec vue sur l'ocean", ["Piscine", "Wifi", "Restaurant", "Bar", "Salle de conference"], "petit-dejeuner", 80),
    ],
    "Abidjan": [
        ("Sofitel Ivoire", 5, "Cocody", "Hotel de luxe avec vue sur la lagune Ebrie", ["Piscine olympique", "Spa", "Wifi", "5 restaurants", "Casino", "Tennis"], "demi-pension", 135),
        ("Hotel Tiama", 3, "Plateau", "Hotel central au coeur du quartier des affaires", ["Wifi", "Restaurant", "Climatisation", "Bar"], "petit-dejeuner", 55),
    ],
    "Dakar": [
        ("Terrou-Bi Hotel", 5, "Corniche", "Resort de luxe en bord de mer avec plage privee", ["Plage privee", "Piscine", "Spa", "Casino", "Wifi", "4 restaurants"], "demi-pension", 120),
        ("Hotel Ngor Diarama", 3, "Ngor", "Hotel avec vue sur l'ile de Ngor", ["Piscine", "Wifi", "Restaurant", "Terrasse vue mer"], "petit-dejeuner", 60),
    ],
    "Zanzibar": [
        ("Zanzibar Beach Resort", 5, "Nungwi", "Resort pieds dans l'eau avec plage de sable blanc", ["Plage privee", "Piscine", "Spa", "Plongee", "Restaurant", "Wifi"], "all-inclusive", 180),
        ("Stone Town Boutique Hotel", 3, "Stone Town", "Hotel charme dans un batiment historique restaure", ["Wifi", "Restaurant", "Terrasse rooftop", "Climatisation"], "petit-dejeuner", 70),
    ],
    "Maldives": [
        ("Sunset Water Villa", 5, "Atoll Male Sud", "Villa sur pilotis avec acces direct au lagon", ["Villa sur pilotis", "Piscine privee", "Spa", "Plongee", "All-inclusive"], "all-inclusive", 350),
        ("Island Guesthouse", 3, "Maafushi", "Guesthouse locale sur une ile habitee", ["Wifi", "Climatisation", "Restaurant", "Excursions"], "petit-dejeuner", 85),
    ],
    "Paris": [
        ("Hotel Le Marais Charme", 4, "Le Marais", "Hotel boutique dans le quartier historique", ["Wifi", "Climatisation", "Bar", "Concierge", "Petit-dejeuner bio"], "petit-dejeuner", 160),
        ("Montmartre View Hotel", 3, "Montmartre", "Hotel avec vue sur le Sacre-Coeur", ["Wifi", "Climatisation", "Terrasse panoramique"], "petit-dejeuner", 95),
    ],
    "Pekin": [
        ("Beijing Palace Hotel", 5, "Dongcheng", "Hotel de luxe pres de la Cite Interdite", ["Piscine", "Spa", "Wifi", "Restaurant gastronomique", "Navette Grande Muraille"], "petit-dejeuner", 110),
        ("Hutong Courtyard Inn", 3, "Xicheng", "Maison traditionnelle dans les hutongs", ["Wifi", "Climatisation", "Jardin interieur", "Cours de cuisine"], "petit-dejeuner", 55),
    ],
    "Shanghai": [
        ("Bund Riverside Hotel", 5, "Huangpu", "Hotel avec vue imprenable sur le Bund et Pudong", ["Piscine", "Spa", "Wifi", "3 restaurants", "Bar rooftop"], "petit-dejeuner", 130),
        ("French Concession B&B", 3, "Xuhui", "Maison de caractere dans la concession francaise", ["Wifi", "Jardin", "Velos gratuits", "Petit-dejeuner maison"], "petit-dejeuner", 60),
    ],
    "Tokyo": [
        ("Shinjuku Grand Hotel", 5, "Shinjuku", "Hotel moderne au coeur de Tokyo", ["Onsen", "Wifi", "3 restaurants", "Bar panoramique", "Salle de sport"], "petit-dejeuner", 150),
        ("Asakusa Ryokan", 3, "Asakusa", "Ryokan traditionnel pres du temple Senso-ji", ["Futons", "Bain japonais", "Wifi", "Jardin zen"], "petit-dejeuner", 80),
    ],
    "Bangkok": [
        ("Riverside Mandarin", 5, "Riverside", "Hotel de luxe sur les rives du Chao Phraya", ["Piscine a debordement", "Spa thai", "Wifi", "4 restaurants", "Navette fluviale"], "petit-dejeuner", 95),
        ("Khao San Boutique", 3, "Phra Nakhon", "Hotel branche pres de Khao San Road", ["Wifi", "Restaurant", "Bar rooftop", "Climatisation"], "petit-dejeuner", 35),
    ],
    "Singapour": [
        ("Marina Bay Sands View", 5, "Marina Bay", "Hotel face au Marina Bay Sands", ["Piscine rooftop", "Spa", "Wifi", "2 restaurants", "Salle de sport"], "petit-dejeuner", 180),
        ("Little India Heritage", 3, "Little India", "Hotel charme dans le quartier indien", ["Wifi", "Restaurant indien", "Climatisation", "Terrasse"], "petit-dejeuner", 75),
    ],
    "Hanoi": [
        ("Old Quarter Silk Hotel", 4, "Hoan Kiem", "Hotel elegant dans le vieux quartier", ["Piscine rooftop", "Spa", "Wifi", "Restaurant", "Bar"], "petit-dejeuner", 55),
        ("Hanoi Homestay", 2, "Ba Dinh", "Maison d'hotes locale authentique", ["Wifi", "Cours de cuisine", "Velos gratuits"], "petit-dejeuner", 25),
    ],
    "Seoul": [
        ("Gangnam Luxury Tower", 5, "Gangnam", "Hotel de luxe au coeur de Gangnam", ["Spa", "Piscine", "Wifi", "Restaurant gastronomique", "Jjimjilbang"], "petit-dejeuner", 140),
        ("Bukchon Hanok Stay", 3, "Jongno", "Maison traditionnelle hanok renovee", ["Wifi", "Climatisation", "Jardin interieur", "Experience culturelle"], "petit-dejeuner", 70),
    ],
    "Goa": [
        ("Palolem Beach Resort", 4, "Palolem", "Resort en bord de plage avec vue sur la mer d'Oman", ["Plage", "Piscine", "Wifi", "Restaurant", "Yoga", "Ayurveda"], "petit-dejeuner", 50),
        ("Old Goa Heritage", 3, "Panaji", "Hotel colonial pres des eglises historiques", ["Wifi", "Restaurant", "Jardin", "Climatisation"], "petit-dejeuner", 35),
    ],
    "Le Caire": [
        ("Pyramids View Hotel", 4, "Gizeh", "Hotel avec vue directe sur les pyramides", ["Piscine", "Wifi", "Restaurant", "Vue pyramides", "Navette"], "petit-dejeuner", 70),
        ("Nile Ritz-Carlton", 5, "Centre-ville", "Hotel de luxe sur les rives du Nil", ["Piscine", "Spa", "Wifi", "5 restaurants", "Bar panoramique"], "demi-pension", 120),
    ],
    "Le Cap": [
        ("Table Bay Hotel", 5, "Waterfront", "Hotel de luxe avec vue Table Mountain", ["Piscine", "Spa", "Wifi", "3 restaurants", "Vue montagne"], "petit-dejeuner", 140),
        ("Bo-Kaap Guesthouse", 3, "Bo-Kaap", "Maison coloree dans le quartier malais historique", ["Wifi", "Petit-dejeuner sud-africain", "Terrasse"], "petit-dejeuner", 55),
    ],
    "Nairobi": [
        ("Safari Lodge Nairobi", 4, "Karen", "Lodge a l'oree du parc national", ["Piscine", "Wifi", "Restaurant", "Safari organise", "Jardin tropical"], "demi-pension", 95),
        ("Nairobi City Hotel", 3, "Centre-ville", "Hotel central bon rapport qualite-prix", ["Wifi", "Restaurant", "Climatisation", "Navette aeroport"], "petit-dejeuner", 50),
    ],
    "Tunis": [
        ("Dar El Medina", 4, "Medina", "Riad elegant dans la medina de Tunis", ["Wifi", "Patio", "Restaurant", "Hammam", "Terrasse"], "petit-dejeuner", 65),
        ("Carthage Thalasso", 5, "Gammarth", "Hotel thalasso en bord de mer", ["Thalasso", "Piscine", "Wifi", "3 restaurants", "Plage privee"], "demi-pension", 110),
    ],
    "Ile Maurice": [
        ("Trou aux Biches Resort", 5, "Trou aux Biches", "Resort de luxe pieds dans l'eau", ["Plage privee", "Spa", "Piscine", "5 restaurants", "Sports nautiques", "Wifi"], "all-inclusive", 220),
        ("Grand Baie Suites", 3, "Grand Baie", "Appartements avec vue sur la baie", ["Wifi", "Piscine", "Kitchenette", "Plage a 50m"], "petit-dejeuner", 75),
    ],
    "Antananarivo": [
        ("Carlton Hotel", 4, "Centre-ville", "Hotel historique au coeur de la capitale", ["Piscine", "Wifi", "Restaurant", "Bar", "Jardin"], "petit-dejeuner", 55),
        ("Tana Guesthouse", 2, "Isoraka", "Maison d'hotes chaleureuse", ["Wifi", "Petit-dejeuner malgache", "Jardin", "Conseils circuits"], "petit-dejeuner", 25),
    ],
    "Lome": [
        ("Hotel Sarakawa", 4, "Bord de mer", "Hotel de reference avec plage privee", ["Plage privee", "Piscine", "Wifi", "Restaurant", "Tennis"], "petit-dejeuner", 70),
        ("Lome Beach Hotel", 3, "Centre", "Hotel confortable pres du Grand Marche", ["Wifi", "Restaurant", "Climatisation", "Bar"], "petit-dejeuner", 40),
    ],
    "Accra": [
        ("Labadi Beach Hotel", 5, "Labadi", "Hotel de luxe sur la plage de Labadi", ["Plage privee", "Piscine", "Spa", "3 restaurants", "Wifi"], "petit-dejeuner", 120),
        ("Osu Oxford Street Hotel", 3, "Osu", "Hotel branche dans le quartier anime d'Osu", ["Wifi", "Restaurant", "Bar", "Climatisation"], "petit-dejeuner", 50),
    ],
    "Rome": [
        ("Hotel Trastevere Charme", 4, "Trastevere", "Hotel de charme dans le quartier boheme", ["Wifi", "Terrasse rooftop", "Bar", "Climatisation", "Concierge"], "petit-dejeuner", 130),
        ("Roma Centro B&B", 3, "Centro Storico", "B&B central pres du Pantheon", ["Wifi", "Climatisation", "Petit-dejeuner italien"], "petit-dejeuner", 75),
    ],
    "Barcelone": [
        ("Hotel Gaudi View", 4, "Eixample", "Hotel avec vue sur la Sagrada Familia", ["Piscine rooftop", "Wifi", "Restaurant", "Bar", "Climatisation"], "petit-dejeuner", 120),
        ("Gothic Quarter Hostal", 2, "Barri Gotic", "Hostal au coeur du quartier gothique", ["Wifi", "Terrasse", "Cuisine commune"], "petit-dejeuner", 50),
    ],
    "Amsterdam": [
        ("Canal Ring Hotel", 4, "Centrum", "Hotel charmant au bord d'un canal", ["Wifi", "Bar", "Velos gratuits", "Petit-dejeuner hollandais"], "petit-dejeuner", 140),
        ("Jordaan B&B", 3, "Jordaan", "B&B dans le quartier le plus pittoresque", ["Wifi", "Climatisation", "Petit-dejeuner bio"], "petit-dejeuner", 85),
    ],
    "Prague": [
        ("Old Town Residence", 4, "Stare Mesto", "Hotel dans un palais baroque restaure", ["Wifi", "Restaurant", "Bar", "Cave a vins", "Concierge"], "petit-dejeuner", 95),
        ("Mala Strana Pension", 3, "Mala Strana", "Pension familiale pres du pont Charles", ["Wifi", "Terrasse", "Petit-dejeuner tcheque"], "petit-dejeuner", 55),
    ],
    "Londres": [
        ("Kensington Palace Hotel", 4, "Kensington", "Hotel elegant pres de Hyde Park", ["Wifi", "Restaurant", "Bar", "Salle de sport", "Concierge"], "petit-dejeuner", 170),
        ("Camden Boutique Inn", 3, "Camden", "Hotel branche pres du marche de Camden", ["Wifi", "Bar", "Climatisation"], "petit-dejeuner", 95),
    ],
    "Istanbul": [
        ("Sultanahmet Palace Hotel", 5, "Sultanahmet", "Hotel de luxe face a Sainte-Sophie", ["Piscine", "Spa hammam", "Wifi", "Restaurant", "Vue Bosphore", "Terrasse"], "petit-dejeuner", 110),
        ("Galata Tower Hotel", 3, "Beyoglu", "Hotel avec vue sur la tour de Galata", ["Wifi", "Restaurant", "Terrasse rooftop", "Climatisation"], "petit-dejeuner", 60),
    ],
    "Dubrovnik": [
        ("Adriatic Luxury Suites", 5, "Vieille Ville", "Suites avec vue sur les remparts et la mer", ["Piscine", "Spa", "Wifi", "Restaurant", "Plage privee"], "petit-dejeuner", 200),
        ("Dubrovnik Old Town Rooms", 3, "Pile", "Chambres dans une maison en pierre", ["Wifi", "Climatisation", "Terrasse vue mer"], "petit-dejeuner", 80),
    ],
    "Reykjavik": [
        ("Aurora Sky Hotel", 4, "Centre", "Hotel ideal pour les aurores boreales", ["Wifi", "Restaurant", "Bar", "Excursions organisees", "Sauna"], "petit-dejeuner", 160),
        ("Reykjavik Guesthouse", 3, "Laugavegur", "Guesthouse dans la rue principale", ["Wifi", "Cuisine commune", "Chauffage geothermique"], "petit-dejeuner", 90),
    ],
    "New York": [
        ("Manhattan Skyline Hotel", 4, "Midtown", "Hotel avec vue sur l'Empire State Building", ["Wifi", "Restaurant", "Bar rooftop", "Salle de sport", "Concierge"], "petit-dejeuner", 195),
        ("Brooklyn Bridge Inn", 3, "Brooklyn", "Hotel tendance a Dumbo", ["Wifi", "Bar", "Terrasse vue Manhattan"], "petit-dejeuner", 120),
    ],
    "Cancun": [
        ("Riviera Maya All-Inclusive", 5, "Zone Hoteliere", "Resort all-inclusive face a la mer des Caraibes", ["Plage privee", "5 piscines", "Spa", "6 restaurants", "Sports nautiques", "Wifi"], "all-inclusive", 180),
        ("Cancun Centro Hotel", 3, "Centro", "Hotel confortable en centre-ville", ["Wifi", "Piscine", "Restaurant", "Climatisation"], "petit-dejeuner", 55),
    ],
    "La Havane": [
        ("Hotel Nacional de Cuba", 5, "Vedado", "Hotel mythique charge d'histoire", ["Piscine", "Wifi", "Restaurant", "Bar", "Jardin tropical", "Vue mer"], "petit-dejeuner", 110),
        ("Casa Particular Habana Vieja", 2, "Habana Vieja", "Maison coloniale chez l'habitant", ["Wifi", "Petit-dejeuner cubain", "Terrasse"], "petit-dejeuner", 35),
    ],
    "Rio de Janeiro": [
        ("Copacabana Palace View", 5, "Copacabana", "Hotel iconique face a Copacabana", ["Piscine", "Spa", "Wifi", "Restaurant gastronomique", "Salle de sport"], "petit-dejeuner", 160),
        ("Ipanema Guesthouse", 3, "Ipanema", "Guesthouse charmante pres de la plage", ["Wifi", "Terrasse", "Petit-dejeuner tropical"], "petit-dejeuner", 65),
    ],
    "Buenos Aires": [
        ("Palermo Soho Hotel", 4, "Palermo", "Hotel design dans le quartier tendance", ["Piscine rooftop", "Wifi", "Restaurant argentin", "Bar a vins", "Tango show"], "petit-dejeuner", 90),
        ("San Telmo Tango B&B", 3, "San Telmo", "B&B dans le berceau du tango", ["Wifi", "Cours de tango", "Petit-dejeuner argentin"], "petit-dejeuner", 45),
    ],
    "Punta Cana": [
        ("Bavaro Beach Resort", 5, "Bavaro", "Resort tout-inclus sur la plage de Bavaro", ["Plage privee", "4 piscines", "Spa", "8 restaurants", "Sports nautiques", "Kids club"], "all-inclusive", 160),
        ("Punta Cana Inn", 3, "El Cortecito", "Hotel simple a 100m de la plage", ["Wifi", "Piscine", "Restaurant", "Climatisation"], "petit-dejeuner", 50),
    ],
    "Cartagena": [
        ("Casa del Reloj", 4, "Ciudad Amurallada", "Maison coloniale transformee en hotel boutique", ["Piscine rooftop", "Wifi", "Restaurant", "Bar", "Spa"], "petit-dejeuner", 100),
        ("Getsemani Hostal", 2, "Getsemani", "Hostal colore dans le quartier artistique", ["Wifi", "Terrasse", "Cuisine commune", "Hammacs"], "petit-dejeuner", 30),
    ],
    "Guadeloupe": [
        ("La Toubana Hotel & Spa", 5, "Sainte-Anne", "Hotel de luxe surplombant la plage de Caravelle", ["Piscine a debordement", "Spa", "Wifi", "Restaurant creole", "Plage privee"], "demi-pension", 175),
        ("Ti Village Creole", 3, "Deshaies", "Bungalows creoles dans un jardin tropical", ["Wifi", "Piscine", "Jardin tropical", "Plage a 200m"], "petit-dejeuner", 70),
    ],
    "Martinique": [
        ("Cap Est Lagoon Resort", 5, "Le Francois", "Resort de luxe face aux fonds blancs", ["Piscine", "Spa", "Wifi", "2 restaurants", "Sports nautiques", "Plage"], "demi-pension", 185),
        ("Anse Noire Lodge", 3, "Les Anses d'Arlet", "Lodge les pieds dans l'eau", ["Wifi", "Plage", "Snorkeling", "Restaurant"], "petit-dejeuner", 65),
    ],
    "Sydney": [
        ("Harbour View Hotel", 5, "Circular Quay", "Hotel avec vue sur l'Opera et le Harbour Bridge", ["Piscine rooftop", "Spa", "Wifi", "Restaurant gastronomique", "Bar"], "petit-dejeuner", 200),
        ("Bondi Beach Apartment", 3, "Bondi", "Appartement moderne pres de Bondi Beach", ["Wifi", "Cuisine equipee", "Plage a 100m"], "petit-dejeuner", 100),
    ],
    "La Reunion": [
        ("Lux Saint-Gilles", 5, "Saint-Gilles", "Hotel de luxe sur la plage de l'Hermitage", ["Plage", "Piscine", "Spa", "Wifi", "2 restaurants", "Sports nautiques"], "demi-pension", 165),
        ("Gite du Volcan", 3, "Plaine des Cafres", "Gite de montagne pres du Piton de la Fournaise", ["Wifi", "Restaurant creole", "Randonnees guidees", "Jardin"], "petit-dejeuner", 55),
    ],
    "Seychelles": [
        ("Anse Source d'Argent Resort", 5, "La Digue", "Resort exclusif pres de la plus belle plage du monde", ["Plage privee", "Piscine", "Spa", "Restaurant", "Plongee", "Wifi"], "all-inclusive", 320),
        ("Mahe Beach Lodge", 3, "Beau Vallon", "Lodge confortable sur la plage de Beau Vallon", ["Wifi", "Restaurant", "Plage", "Snorkeling"], "petit-dejeuner", 90),
    ],
    "Oman": [
        ("Al Bustan Palace", 5, "Mascate", "Palais face a la mer avec plage privee", ["Plage privee", "Piscine", "Spa", "Wifi", "3 restaurants", "Marina"], "petit-dejeuner", 160),
        ("Desert Nights Camp", 4, "Wahiba Sands", "Camp de luxe dans le desert", ["Tentes climatisees", "Piscine", "Wifi", "Restaurant", "Safari dromadaire"], "demi-pension", 110),
    ],
    "Douala": [
        ("Akwa Palace Hotel", 4, "Akwa", "Hotel de reference a Douala", ["Piscine", "Wifi", "Restaurant", "Bar", "Salle de sport"], "petit-dejeuner", 75),
        ("Hotel Le Marin", 3, "Bonapriso", "Hotel confortable au quartier residentiel", ["Wifi", "Restaurant", "Climatisation", "Jardin"], "petit-dejeuner", 40),
    ],
    "Casablanca": [
        ("Hyatt Regency Casa", 5, "Centre-ville", "Hotel de luxe pres de la mosquee Hassan II", ["Piscine", "Spa", "Wifi", "3 restaurants", "Salle de sport", "Vue mer"], "petit-dejeuner", 130),
        ("Hotel Transatlantique", 3, "Maarif", "Hotel Art Deco au charme retro", ["Wifi", "Restaurant", "Bar", "Terrasse"], "petit-dejeuner", 55),
    ],
    "Nosy Be": [
        ("Ravintsara Wellness Hotel", 4, "Ambatoloaka", "Hotel spa dans un jardin tropical face a la mer", ["Piscine", "Spa", "Wifi", "Restaurant", "Plongee", "Plage"], "demi-pension", 95),
        ("Nosy Be Beach Bungalow", 2, "Madirokely", "Bungalows pieds dans l'eau", ["Wifi", "Restaurant", "Plage", "Kayak"], "petit-dejeuner", 40),
    ],
}


def _get_hubs_for_dest(dest_name, dest_country, dest_region):
    hubs = []
    for hub_city, hub_code, hub_region in DEPARTURE_HUBS:
        if hub_city == dest_name:
            continue
        hubs.append((hub_city, hub_code, hub_region))
    return hubs[:6]


def seed_demo_data(db: Session):
    if db.query(Agency).first():
        return

    agency = Agency(
        name="Voyages Horizon",
        slug="demo",
        description="Agence de voyages partenaire GrowUp AI - Donnees de demonstration",
        primary_color="#1B3A5C",
        secondary_color="#C9A84C",
        currency="EUR",
        agent_name="Horizon",
        agent_tone="chaleureux",
        welcome_message=(
            "Bonjour ! Je suis Horizon, votre assistant voyage.\n\n"
            "Je suis la pour vous aider a trouver le sejour ideal : "
            "destinations, vols, hotels... Dites-moi simplement ce qui vous ferait envie !"
        ),
        payment_link_template="https://demo.growupai.com/paiement/{reference}",
        escalation_email="conseillers@voyages-horizon.demo",
    )
    db.add(agency)
    db.flush()

    admin = User(
        agency_id=agency.id,
        email="admin@demo.com",
        password_hash=hash_password("admin123"),
        first_name="Marie",
        last_name="Dupont",
        role="admin",
    )
    agent_user = User(
        agency_id=agency.id,
        email="agent@demo.com",
        password_hash=hash_password("agent123"),
        first_name="Thomas",
        last_name="Martin",
        role="agent",
    )
    db.add_all([admin, agent_user])
    db.flush()

    dest_objects = {}
    flight_counter = 0
    all_flights = []
    all_hotels = []

    for (name, country, desc, img_key, highlights, best_season,
         avg_temp, flight_paris, dest_type, arr_airport) in DESTINATIONS_DATA:

        dest = Destination(
            agency_id=agency.id,
            name=name,
            country=country,
            description=desc,
            image_url=f"https://images.unsplash.com/{img_key}?w=800",
            highlights=highlights,
            best_season=best_season,
            avg_temperature=avg_temp,
            flight_duration_from_paris=flight_paris,
            destination_type=dest_type,
        )
        db.add(dest)
        db.flush()
        dest_objects[name] = dest

        d_region = _dest_region(country)

        hubs = _get_hubs_for_dest(name, country, d_region)
        for hub_city, hub_code, hub_region in hubs:
            airlines = _get_route_airlines(hub_region, d_region)
            airline_info = airlines[flight_counter % len(airlines)]
            airline_name, airline_prefix, baggage = airline_info
            flight_counter += 1

            duration, stops = _flight_duration(hub_region, d_region)
            price = _base_price(hub_region, d_region)
            price_variation = (flight_counter * 37) % 80 - 20
            price = max(69, price + price_variation)

            dep_h = 6 + (flight_counter * 3) % 16
            dep_m = (flight_counter * 17) % 4 * 15
            arr_dur = duration + (stops * 120)
            arr_h = (dep_h + arr_dur // 60) % 24
            arr_m = (dep_m + arr_dur % 60) % 60

            fn = f"{airline_prefix}{1000 + flight_counter}"

            stop_cities_list = []
            if stops > 0:
                if hub_region == "afrique" and d_region == "asie":
                    stop_cities_list = ["Dubai"]
                elif hub_region == "europe" and d_region == "asie":
                    stop_cities_list = ["Istanbul"]
                elif hub_region == "europe" and d_region == "ocean_indien":
                    stop_cities_list = ["Dubai"]
                elif d_region == "amerique" and stops > 0:
                    stop_cities_list = ["Lisbonne"]
                else:
                    stop_cities_list = ["Casablanca"]

            flight = Flight(
                agency_id=agency.id,
                destination_id=dest.id,
                airline=airline_name,
                flight_number=fn,
                departure_city=hub_city,
                departure_airport=hub_code,
                departure_time=f"{dep_h:02d}:{dep_m:02d}",
                arrival_city=name,
                arrival_airport=arr_airport,
                arrival_time=f"{arr_h:02d}:{arr_m:02d}",
                duration_minutes=arr_dur,
                stops=stops,
                stop_cities=stop_cities_list if stop_cities_list else [],
                baggage_included=baggage,
                price_per_adult=float(price),
                price_per_child=float(int(price * 0.8)),
                price_per_infant=float(int(price * 0.1)),
                cancellation_policy="Annulation gratuite jusqu'a 48h avant le depart",
                modification_policy="Modification possible moyennant 50 EUR",
                available_seats=20 + (flight_counter * 7) % 40,
                valid_from=date(2026, 11, 1),
                valid_until=date(2027, 10, 31),
            )
            all_flights.append(flight)

        hotel_data = HOTELS_BY_DESTINATION.get(name, [])
        for (h_name, h_cat, h_city, h_desc, h_amenities, h_meal, h_price) in hotel_data:
            hotel = Hotel(
                agency_id=agency.id,
                destination_id=dest.id,
                name=h_name,
                category=h_cat,
                city=h_city,
                address=f"{h_city}, {name}",
                description=h_desc,
                amenities=h_amenities,
                meal_plan=h_meal,
                price_per_night=float(h_price),
                cancellation_policy="Annulation gratuite jusqu'a 48h avant l'arrivee",
            )
            all_hotels.append(hotel)

    db.add_all(all_flights)
    db.add_all(all_hotels)
    db.flush()

    packages = []
    sample_routes = [
        ("Marrakech", "Paris"),
        ("Bali", "Paris"),
        ("Zanzibar", "Cotonou"),
        ("Maldives", "Paris"),
        ("Dakar", "Abidjan"),
        ("Tokyo", "Paris"),
    ]
    for dest_name, dep_city in sample_routes:
        dest = dest_objects.get(dest_name)
        if not dest:
            continue
        flight = None
        for f in all_flights:
            if f.destination_id == dest.id and f.departure_city == dep_city:
                flight = f
                break
        hotel_list = [h for h in all_hotels if h.destination_id == dest.id]
        hotel = hotel_list[0] if hotel_list else None
        if flight and hotel:
            pkg_price = flight.price_per_adult + hotel.price_per_night * 7
            packages.append(Package(
                agency_id=agency.id,
                flight_id=flight.id,
                hotel_id=hotel.id,
                name=f"{dest_name} Essentiel - 7 nuits",
                description=f"Vol {flight.airline} depuis {dep_city} + {hotel.name}",
                price_per_adult=float(int(pkg_price * 0.92)),
                price_per_child=float(int(pkg_price * 0.75)),
                discount_percentage=8,
                valid_from=date(2026, 11, 1),
                valid_until=date(2027, 10, 31),
            ))

    if packages:
        db.add_all(packages)
    db.commit()

    n_dests = len(dest_objects)
    n_flights = len(all_flights)
    n_hotels = len(all_hotels)
    n_pkgs = len(packages)

    print(f"Donnees de demonstration creees pour '{agency.name}'")
    print(f"  - {n_dests} destinations")
    print(f"  - {n_flights} vols (multi-origines)")
    print(f"  - {n_hotels} hotels")
    print(f"  - {n_pkgs} forfaits")
    print(f"\nComptes de test :")
    print(f"  Admin : admin@demo.com / admin123")
    print(f"  Agent : agent@demo.com / agent123")
