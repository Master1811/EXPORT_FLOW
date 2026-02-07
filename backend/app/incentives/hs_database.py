# HS Code Database with RoDTEP and RoSCTL Rates
# Source: DGFT Notifications (simplified for MVP)

HS_CODE_DATABASE = {
    # Chapter 61 - Articles of apparel and clothing accessories, knitted or crocheted
    "6101": {"description": "Men's overcoats, knitted", "rodtep": 4.3, "rosctl": 6.0, "drawback": 1.5, "chapter": "61"},
    "6102": {"description": "Women's overcoats, knitted", "rodtep": 4.3, "rosctl": 6.0, "drawback": 1.5, "chapter": "61"},
    "6103": {"description": "Men's suits, knitted", "rodtep": 4.3, "rosctl": 5.5, "drawback": 1.5, "chapter": "61"},
    "6104": {"description": "Women's suits, knitted", "rodtep": 4.3, "rosctl": 5.5, "drawback": 1.5, "chapter": "61"},
    "6105": {"description": "Men's shirts, knitted", "rodtep": 4.3, "rosctl": 6.0, "drawback": 1.8, "chapter": "61"},
    "6106": {"description": "Women's blouses, knitted", "rodtep": 4.3, "rosctl": 6.0, "drawback": 1.8, "chapter": "61"},
    "6109": {"description": "T-shirts, singlets, knitted", "rodtep": 4.3, "rosctl": 5.5, "drawback": 1.5, "chapter": "61"},
    "6110": {"description": "Sweaters, pullovers, knitted", "rodtep": 4.3, "rosctl": 5.0, "drawback": 1.5, "chapter": "61"},
    "6111": {"description": "Babies' garments, knitted", "rodtep": 4.3, "rosctl": 5.5, "drawback": 1.5, "chapter": "61"},
    "6115": {"description": "Hosiery, knitted", "rodtep": 4.3, "rosctl": 4.5, "drawback": 1.2, "chapter": "61"},
    
    # Chapter 62 - Articles of apparel and clothing accessories, not knitted
    "6201": {"description": "Men's overcoats, woven", "rodtep": 4.3, "rosctl": 6.5, "drawback": 1.8, "chapter": "62"},
    "6202": {"description": "Women's overcoats, woven", "rodtep": 4.3, "rosctl": 6.5, "drawback": 1.8, "chapter": "62"},
    "6203": {"description": "Men's suits, woven", "rodtep": 4.3, "rosctl": 6.0, "drawback": 1.8, "chapter": "62"},
    "6204": {"description": "Women's suits, woven", "rodtep": 4.3, "rosctl": 6.0, "drawback": 1.8, "chapter": "62"},
    "6205": {"description": "Men's shirts, woven", "rodtep": 4.3, "rosctl": 6.5, "drawback": 2.0, "chapter": "62"},
    "6206": {"description": "Women's blouses, woven", "rodtep": 4.3, "rosctl": 6.5, "drawback": 2.0, "chapter": "62"},
    "6207": {"description": "Men's underwear, woven", "rodtep": 4.3, "rosctl": 5.5, "drawback": 1.5, "chapter": "62"},
    "6208": {"description": "Women's underwear, woven", "rodtep": 4.3, "rosctl": 5.5, "drawback": 1.5, "chapter": "62"},
    "6211": {"description": "Tracksuits, ski suits", "rodtep": 4.3, "rosctl": 5.0, "drawback": 1.5, "chapter": "62"},
    
    # Chapter 63 - Made-up textile articles
    "6301": {"description": "Blankets and travelling rugs", "rodtep": 4.0, "rosctl": 5.0, "drawback": 1.5, "chapter": "63"},
    "6302": {"description": "Bed linen, table linen", "rodtep": 4.0, "rosctl": 5.5, "drawback": 1.8, "chapter": "63"},
    "6303": {"description": "Curtains, drapes", "rodtep": 4.0, "rosctl": 5.0, "drawback": 1.5, "chapter": "63"},
    "6304": {"description": "Furnishing articles", "rodtep": 4.0, "rosctl": 5.0, "drawback": 1.5, "chapter": "63"},
    "6305": {"description": "Sacks and bags", "rodtep": 3.5, "rosctl": 4.0, "drawback": 1.2, "chapter": "63"},
    
    # Chapter 52 - Cotton
    "5201": {"description": "Cotton, not carded", "rodtep": 0.5, "rosctl": 0, "drawback": 0, "chapter": "52"},
    "5205": {"description": "Cotton yarn", "rodtep": 2.5, "rosctl": 3.0, "drawback": 1.0, "chapter": "52"},
    "5208": {"description": "Woven cotton fabrics", "rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "chapter": "52"},
    "5209": {"description": "Woven cotton fabrics >200g/m2", "rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "chapter": "52"},
    "5210": {"description": "Cotton mixed fabrics", "rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "chapter": "52"},
    
    # Chapter 84 - Machinery and mechanical appliances
    "8401": {"description": "Nuclear reactors", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "84"},
    "8411": {"description": "Turbo-jets, turbo-propellers", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    "8414": {"description": "Air/vacuum pumps, compressors", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8418": {"description": "Refrigerators, freezers", "rodtep": 2.5, "rosctl": 0, "drawback": 1.2, "chapter": "84"},
    "8421": {"description": "Centrifuges, filtering machinery", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8422": {"description": "Dish washing machines", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8428": {"description": "Lifting/handling machinery", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    "8429": {"description": "Bulldozers, excavators", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    "8431": {"description": "Parts for machinery", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    "8443": {"description": "Printing machinery", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8450": {"description": "Washing machines", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8471": {"description": "Computers and peripherals", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "84"},
    "8473": {"description": "Parts for computers", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "84"},
    "8479": {"description": "Machines with specific functions", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8481": {"description": "Taps, valves, cocks", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "84"},
    "8482": {"description": "Ball/roller bearings", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    "8483": {"description": "Transmission shafts, gears", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    "8484": {"description": "Gaskets, mechanical seals", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "84"},
    
    # Chapter 85 - Electrical machinery and equipment
    "8501": {"description": "Electric motors, generators", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8502": {"description": "Electric generating sets", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8504": {"description": "Transformers, converters", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8506": {"description": "Primary cells and batteries", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "85"},
    "8507": {"description": "Electric accumulators", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8511": {"description": "Ignition equipment", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "85"},
    "8516": {"description": "Electric heaters, ovens", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8517": {"description": "Telephones, communication equipment", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8523": {"description": "Recording media", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8528": {"description": "Monitors, projectors, TVs", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8529": {"description": "Parts for TVs, radios", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8532": {"description": "Electrical capacitors", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8534": {"description": "Printed circuits", "rodtep": 2.5, "rosctl": 0, "drawback": 0.8, "chapter": "85"},
    "8536": {"description": "Switches, connectors", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8537": {"description": "Control panels", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8538": {"description": "Parts for switches", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    "8541": {"description": "Semiconductor devices", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8542": {"description": "Electronic integrated circuits", "rodtep": 2.0, "rosctl": 0, "drawback": 0.5, "chapter": "85"},
    "8544": {"description": "Insulated wire, cables", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "85"},
    
    # Chapter 87 - Vehicles
    "8701": {"description": "Tractors", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "87"},
    "8702": {"description": "Motor vehicles for passengers (>10)", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "87"},
    "8703": {"description": "Motor cars", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "87"},
    "8704": {"description": "Motor vehicles for goods", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "87"},
    "8708": {"description": "Parts for motor vehicles", "rodtep": 3.0, "rosctl": 0, "drawback": 1.5, "chapter": "87"},
    "8711": {"description": "Motorcycles", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "87"},
    "8714": {"description": "Parts for motorcycles", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "87"},
    
    # Chapter 90 - Optical, medical instruments
    "9001": {"description": "Optical fibres, lenses", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9002": {"description": "Lens, prism assemblies", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9003": {"description": "Spectacle frames", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "90"},
    "9004": {"description": "Spectacles, goggles", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "90"},
    "9018": {"description": "Medical instruments", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9021": {"description": "Orthopaedic appliances", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9025": {"description": "Thermometers, hydrometers", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9026": {"description": "Flow/level measuring instruments", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9027": {"description": "Analysis instruments", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9028": {"description": "Gas, liquid meters", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9031": {"description": "Measuring instruments", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    "9032": {"description": "Automatic regulating instruments", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "90"},
    
    # Chapter 94 - Furniture
    "9401": {"description": "Seats", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "94"},
    "9403": {"description": "Other furniture", "rodtep": 3.5, "rosctl": 0, "drawback": 1.5, "chapter": "94"},
    "9404": {"description": "Mattresses, quilts", "rodtep": 3.5, "rosctl": 4.0, "drawback": 1.5, "chapter": "94"},
    "9405": {"description": "Lamps and lighting", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "94"},
    
    # Chapter 03 - Fish and seafood
    "0301": {"description": "Live fish", "rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "chapter": "03"},
    "0302": {"description": "Fish, fresh or chilled", "rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "chapter": "03"},
    "0303": {"description": "Fish, frozen", "rodtep": 2.0, "rosctl": 0, "drawback": 1.0, "chapter": "03"},
    "0304": {"description": "Fish fillets", "rodtep": 2.5, "rosctl": 0, "drawback": 1.2, "chapter": "03"},
    "0306": {"description": "Crustaceans", "rodtep": 2.5, "rosctl": 0, "drawback": 1.2, "chapter": "03"},
    "0307": {"description": "Molluscs", "rodtep": 2.5, "rosctl": 0, "drawback": 1.2, "chapter": "03"},
    
    # Chapter 09 - Spices
    "0901": {"description": "Coffee", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "09"},
    "0902": {"description": "Tea", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "09"},
    "0904": {"description": "Pepper", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "09"},
    "0906": {"description": "Cinnamon", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "09"},
    "0908": {"description": "Nutmeg, cardamoms", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "09"},
    "0909": {"description": "Cumin, caraway seeds", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "09"},
    "0910": {"description": "Ginger, turmeric", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "09"},
    
    # Chapter 10 - Cereals
    "1001": {"description": "Wheat", "rodtep": 0.5, "rosctl": 0, "drawback": 0, "chapter": "10"},
    "1005": {"description": "Maize", "rodtep": 0.5, "rosctl": 0, "drawback": 0, "chapter": "10"},
    "1006": {"description": "Rice", "rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "chapter": "10"},
    
    # Chapter 29 - Organic chemicals
    "2901": {"description": "Acyclic hydrocarbons", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "29"},
    "2902": {"description": "Cyclic hydrocarbons", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "29"},
    "2905": {"description": "Acyclic alcohols", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "29"},
    "2915": {"description": "Acyclic acids", "rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "chapter": "29"},
    "2922": {"description": "Amino-compounds", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "29"},
    "2933": {"description": "Heterocyclic compounds", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "29"},
    "2941": {"description": "Antibiotics", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "29"},
    
    # Chapter 30 - Pharmaceutical products
    "3001": {"description": "Glands, extracts", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "30"},
    "3002": {"description": "Blood, antisera, vaccines", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "30"},
    "3003": {"description": "Medicaments (not dosed)", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "30"},
    "3004": {"description": "Medicaments (dosed)", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "30"},
    "3005": {"description": "Wadding, bandages", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "30"},
    
    # Chapter 71 - Precious stones, jewellery
    "7101": {"description": "Pearls", "rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "chapter": "71"},
    "7102": {"description": "Diamonds", "rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "chapter": "71"},
    "7103": {"description": "Precious stones", "rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "chapter": "71"},
    "7113": {"description": "Jewellery", "rodtep": 2.0, "rosctl": 0, "drawback": 1.0, "chapter": "71"},
    "7114": {"description": "Goldsmith articles", "rodtep": 2.0, "rosctl": 0, "drawback": 1.0, "chapter": "71"},
    "7117": {"description": "Imitation jewellery", "rodtep": 3.0, "rosctl": 0, "drawback": 1.5, "chapter": "71"},
    
    # Chapter 73 - Iron and steel articles
    "7301": {"description": "Sheet piling", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "73"},
    "7304": {"description": "Tubes, pipes (seamless)", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    "7306": {"description": "Tubes, pipes (welded)", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    "7307": {"description": "Tube fittings", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    "7308": {"description": "Structures, parts", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    "7318": {"description": "Screws, bolts, nuts", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    "7320": {"description": "Springs", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    "7323": {"description": "Table/kitchen articles", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "73"},
    "7324": {"description": "Sanitary ware", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "73"},
    "7326": {"description": "Other iron/steel articles", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "73"},
    
    # Chapter 74 - Copper and copper articles (Moradabad Handicrafts)
    "7418": {"description": "Copper utensils, table/kitchen articles", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "74"},
    "74181022": {"description": "Utensils of Copper (Bottles, Mugs, Jugs)", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "74"},
    "7419": {"description": "Other copper articles", "rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "chapter": "74"},
    "74198030": {"description": "Artware/Handicrafts of Brass (Moradabad Specialty)", "rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "chapter": "74"},
    
    # Chapter 68 - Stone articles (Marble, Decorative Stone)
    "6802": {"description": "Worked monumental/building stone", "rodtep": 1.5, "rosctl": 0, "drawback": 0.6, "chapter": "68"},
    "68022190": {"description": "Worked Marble/Stone Articles (Fusion Planters/Vases)", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "68"},
    
    # Chapter 94 - Furniture (Iron/Metal) - Moradabad style
    "94032010": {"description": "Iron/Metal Furniture (Chairs, Tables, Frames)", "rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "chapter": "94"},
    "94055000": {"description": "Non-Electrical Lamps & Lighting (Candle Stands/Lanterns)", "rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "chapter": "94"},
    
    # Chapter 73 - Iron Handicraft (Moradabad Metal Planters)
    "73269099": {"description": "Iron Handicraft Planters & Garden Accessories", "rodtep": 1.5, "rosctl": 0, "drawback": 0.6, "chapter": "73"},
}

# Chapter-level default rates (for codes not in database)
CHAPTER_DEFAULTS = {
    "01": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Live animals"},
    "02": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Meat"},
    "03": {"rodtep": 2.0, "rosctl": 0, "drawback": 1.0, "category": "Fish & seafood"},
    "04": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Dairy products"},
    "05": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Animal products"},
    "06": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Live plants"},
    "07": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Vegetables"},
    "08": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Fruits, nuts"},
    "09": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Spices"},
    "10": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Cereals"},
    "11": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Milling products"},
    "12": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Oil seeds"},
    "13": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Lac, gums"},
    "14": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Vegetable plaiting"},
    "15": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Animal/vegetable fats"},
    "16": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "category": "Meat preparations"},
    "17": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Sugars"},
    "18": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "category": "Cocoa"},
    "19": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "category": "Cereal preparations"},
    "20": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "category": "Vegetable preparations"},
    "21": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "category": "Misc food"},
    "22": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Beverages"},
    "23": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Food waste"},
    "24": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Tobacco"},
    "25": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Salt, sulphur, earth"},
    "26": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Ores, slag"},
    "27": {"rodtep": 0.5, "rosctl": 0, "drawback": 0, "category": "Mineral fuels"},
    "28": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "category": "Inorganic chemicals"},
    "29": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Organic chemicals"},
    "30": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Pharmaceuticals"},
    "31": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Fertilizers"},
    "32": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Dyes, paints"},
    "33": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Essential oils"},
    "34": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Soap, wax"},
    "35": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Albuminoidal"},
    "36": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Explosives"},
    "37": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Photographic goods"},
    "38": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Chemical products"},
    "39": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Plastics"},
    "40": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Rubber"},
    "41": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Raw hides, leather"},
    "42": {"rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "category": "Leather articles"},
    "43": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Furskins"},
    "44": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Wood"},
    "45": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Cork"},
    "46": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Straw, basketware"},
    "47": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Pulp"},
    "48": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Paper"},
    "49": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "category": "Printed books"},
    "50": {"rodtep": 3.0, "rosctl": 4.0, "drawback": 1.2, "category": "Silk"},
    "51": {"rodtep": 3.0, "rosctl": 4.0, "drawback": 1.2, "category": "Wool"},
    "52": {"rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "category": "Cotton"},
    "53": {"rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "category": "Vegetable fibres"},
    "54": {"rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "category": "Man-made filaments"},
    "55": {"rodtep": 3.0, "rosctl": 3.5, "drawback": 1.2, "category": "Man-made staple fibres"},
    "56": {"rodtep": 3.0, "rosctl": 4.0, "drawback": 1.2, "category": "Wadding, felt"},
    "57": {"rodtep": 3.5, "rosctl": 4.5, "drawback": 1.5, "category": "Carpets"},
    "58": {"rodtep": 3.5, "rosctl": 4.5, "drawback": 1.5, "category": "Special woven fabrics"},
    "59": {"rodtep": 3.0, "rosctl": 4.0, "drawback": 1.2, "category": "Impregnated textiles"},
    "60": {"rodtep": 3.5, "rosctl": 4.5, "drawback": 1.5, "category": "Knitted fabrics"},
    "61": {"rodtep": 4.3, "rosctl": 5.5, "drawback": 1.8, "category": "Knitted apparel"},
    "62": {"rodtep": 4.3, "rosctl": 6.0, "drawback": 2.0, "category": "Woven apparel"},
    "63": {"rodtep": 4.0, "rosctl": 5.0, "drawback": 1.5, "category": "Made-up textiles"},
    "64": {"rodtep": 3.5, "rosctl": 0, "drawback": 1.5, "category": "Footwear"},
    "65": {"rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "category": "Headgear"},
    "66": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Umbrellas"},
    "67": {"rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "category": "Feathers, flowers"},
    "68": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Stone, plaster"},
    "69": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Ceramic products"},
    "70": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Glass"},
    "71": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.8, "category": "Precious stones, jewellery"},
    "72": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "category": "Iron and steel"},
    "73": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Iron/steel articles"},
    "74": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Copper"},
    "75": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Nickel"},
    "76": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Aluminium"},
    "78": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "category": "Lead"},
    "79": {"rodtep": 1.5, "rosctl": 0, "drawback": 0.5, "category": "Zinc"},
    "80": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Tin"},
    "81": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Other base metals"},
    "82": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Tools, cutlery"},
    "83": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Metal misc articles"},
    "84": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Machinery"},
    "85": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Electrical machinery"},
    "86": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Railway"},
    "87": {"rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "category": "Vehicles"},
    "88": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Aircraft"},
    "89": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Ships, boats"},
    "90": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Optical, medical"},
    "91": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Clocks, watches"},
    "92": {"rodtep": 2.5, "rosctl": 0, "drawback": 1.0, "category": "Musical instruments"},
    "93": {"rodtep": 2.0, "rosctl": 0, "drawback": 0.8, "category": "Arms, ammunition"},
    "94": {"rodtep": 3.5, "rosctl": 0, "drawback": 1.5, "category": "Furniture"},
    "95": {"rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "category": "Toys, games"},
    "96": {"rodtep": 3.0, "rosctl": 0, "drawback": 1.2, "category": "Misc manufactured"},
    "97": {"rodtep": 1.0, "rosctl": 0, "drawback": 0.5, "category": "Works of art"},
}

def get_hs_code_info(hs_code: str) -> dict:
    """Get incentive rates for a given HS code"""
    # Clean the HS code
    hs_code = hs_code.replace(".", "").replace(" ", "")[:4]
    
    # Try exact match first
    if hs_code in HS_CODE_DATABASE:
        data = HS_CODE_DATABASE[hs_code]
        return {
            "hs_code": hs_code,
            "found": True,
            "exact_match": True,
            **data
        }
    
    # Try chapter default
    chapter = hs_code[:2]
    if chapter in CHAPTER_DEFAULTS:
        data = CHAPTER_DEFAULTS[chapter]
        return {
            "hs_code": hs_code,
            "found": True,
            "exact_match": False,
            "description": f"Chapter {chapter} - {data['category']}",
            "rodtep": data["rodtep"],
            "rosctl": data["rosctl"],
            "drawback": data["drawback"],
            "chapter": chapter
        }
    
    return {
        "hs_code": hs_code,
        "found": False,
        "exact_match": False,
        "description": "Unknown HS Code",
        "rodtep": 0,
        "rosctl": 0,
        "drawback": 0,
        "chapter": chapter
    }

def calculate_incentives(fob_value: float, hs_code: str, currency: str = "INR", exchange_rate: float = 1.0) -> dict:
    """Calculate all applicable incentives for a shipment"""
    hs_info = get_hs_code_info(hs_code)
    
    # Convert to INR if needed
    fob_inr = fob_value * exchange_rate if currency != "INR" else fob_value
    
    rodtep_amount = fob_inr * (hs_info["rodtep"] / 100)
    rosctl_amount = fob_inr * (hs_info["rosctl"] / 100)
    drawback_amount = fob_inr * (hs_info["drawback"] / 100)
    total_incentive = rodtep_amount + rosctl_amount + drawback_amount
    
    return {
        "fob_value": fob_value,
        "fob_value_inr": fob_inr,
        "currency": currency,
        "hs_code": hs_code,
        "hs_info": hs_info,
        "incentives": {
            "rodtep": {
                "rate": hs_info["rodtep"],
                "amount": round(rodtep_amount, 2),
                "scheme": "RoDTEP (Remission of Duties and Taxes on Exported Products)"
            },
            "rosctl": {
                "rate": hs_info["rosctl"],
                "amount": round(rosctl_amount, 2),
                "scheme": "RoSCTL (Rebate of State & Central Taxes and Levies)",
                "applicable": hs_info["rosctl"] > 0
            },
            "drawback": {
                "rate": hs_info["drawback"],
                "amount": round(drawback_amount, 2),
                "scheme": "Duty Drawback"
            }
        },
        "total_incentive": round(total_incentive, 2),
        "total_rate": round(hs_info["rodtep"] + hs_info["rosctl"] + hs_info["drawback"], 2)
    }

def search_hs_codes(query: str, limit: int = 20) -> list:
    """Search HS codes by description or code"""
    query = query.lower()
    results = []
    
    for code, data in HS_CODE_DATABASE.items():
        if query in code or query in data["description"].lower():
            results.append({
                "hs_code": code,
                **data
            })
            if len(results) >= limit:
                break
    
    return results
