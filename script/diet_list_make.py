import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from enum import Enum, auto

# Tarif ve diyet anahtar kelimeleri için enum
class RecipeKeyword(str, Enum):
    MAHI_MAHI = "Mahi Mahi"
    IRAQI = "Iraqi"
    HIGH_IN = "High In..."
    MIXER = "Mixer"
    POLYNESIAN = "Polynesian"
    SPAGHETTI = "Spaghetti"
    JAPANESE = "Japanese"
    BREAKFAST_POTATOES = "Breakfast Potatoes"
    TOMATO_SAUCE = "Tomato Sauce"
    EGG_FREE = "Egg Free"
    MASHED_POTATOES = "Mashed Potatoes"
    WEEKNIGHT = "Weeknight"
    GRAPES = "Grapes"
    HIGH_PROTEIN = "High Protein"
    VIETNAMESE = "Vietnamese"
    BEEF_BARLEY_SOUP = "Beef Barley Soup"
    PEPPERS = "Peppers"
    MARINARA_SAUCE = "Marinara Sauce"
    GREEK = "Greek"
    THANKSGIVING = "Thanksgiving"
    LOW_PROTEIN = "Low Protein"
    EGGS_BREAKFAST = "Eggs Breakfast"
    HAWAIIAN = "Hawaiian"
    DAIRY_FREE_FOODS = "Dairy Free Foods"
    POT_ROAST = "Pot Roast"
    TROPICAL_FRUITS = "Tropical Fruits"
    CURRIES = "Curries"
    CORN = "Corn"
    EASY = "Easy"
    ARTICHOKE = "Artichoke"
    CABBAGE = "Cabbage"
    COLLARD_GREENS = "Collard Greens"
    POULTRY = "Poultry"
    QUAIL = "Quail"
    MALAYSIAN = "Malaysian"
    BAKED_BEANS = "Baked Beans"
    TORTILLA_SOUP = "Tortilla Soup"
    LESS_THAN_4_HOURS = "< 4 Hours"
    MEATLOAF = "Meatloaf"
    POTLUCK = "Potluck"
    SUDANESE = "Sudanese"
    CHRISTMAS = "Christmas"
    SOUTH_AFRICAN = "South African"
    DEEP_FRIED = "Deep Fried"
    WHITEFISH = "Whitefish"
    DUTCH = "Dutch"
    YAM_SWEET_POTATO = "Yam/Sweet Potato"
    ASIAN = "Asian"
    CREOLE = "Creole"
    ROAST_BEEF = "Roast Beef"
    CANNING = "Canning"
    PINEAPPLE = "Pineapple"
    NEW_ZEALAND = "New Zealand"
    BEAN_SOUP = "Bean Soup"
    CHERRIES = "Cherries"
    COCONUT_DESSERTS = "Coconut Desserts"
    PORK_LOIN = "Pork Loin"
    SZECHUAN = "Szechuan"
    NIGERIAN = "Nigerian"
    FREE_OF = "Free Of..."
    FRUIT = "Fruit"
    FOR_LARGE_GROUPS_HOLIDAY = "For Large Groups Holiday/Event"
    THAI = "Thai"
    ELK = "Elk"
    ICELANDIC = "Icelandic"
    PHEASANT = "Pheasant"
    VERY_LOW_CARBS = "Very Low Carbs"
    LESS_THAN_60_MINS = "< 60 Mins"
    BEEF_SAUCES = "Beef Sauces"
    MEXICAN = "Mexican"
    BEEF_KIDNEY = "Beef Kidney"
    SCANDINAVIAN = "Scandinavian"
    MUSSELS = "Mussels"
    TROUT = "Trout"
    CAJUN = "Cajun"
    MONGOLIAN = "Mongolian"
    KOSHER = "Kosher"
    CAULIFLOWER = "Cauliflower"
    AFRICAN = "African"
    KID_FRIENDLY = "Kid Friendly"
    FISH_HALIBUT = "Fish Halibut"
    BROWN_RICE = "Brown Rice"
    CHICKEN = "Chicken"
    SWEET = "Sweet"
    ORANGE_ROUGHY = "Orange Roughy"
    BEEF_LIVER = "Beef Liver"
    LENTIL = "Lentil"
    SHORT_GRAIN_RICE = "Short Grain Rice"
    SUMMER = "Summer"
    JELLIES = "Jellies"
    TODDLER_FRIENDLY = "Toddler Friendly"
    LACTOSE_FREE = "Lactose Free"
    PORK_CROCK_POT = "Pork Crock Pot"
    AUSTRALIAN = "Australian"
    HALIBUT = "Halibut"
    SPANISH = "Spanish"
    REFRIGERATOR = "Refrigerator"
    MELONS = "Melons"
    CANTONESE = "Cantonese"
    PORTUGUESE = "Portuguese"
    NO_BAKE_COOKIE = "No Bake Cookie"
    CUCUMBER = "Cucumber"
    POLISH = "Polish"
    STOVE_TOP = "Stove Top"
    BREAKFAST_EGGS = "Breakfast Eggs"
    CANDY = "Candy"
    INDONESIAN = "Indonesian"
    SAVORY = "Savory"
    STEAK = "Steak"
    VEAL = "Veal"
    WHOLE_CHICKEN = "Whole Chicken"
    SPICY = "Spicy"
    NATIVE_AMERICAN = "Native American"
    LESS_THAN_30_MINS = "< 30 Mins"
    SAUCES = "Sauces"
    LIME_DESSERTS = "Lime Desserts"
    HALLOWEEN = "Halloween"
    HANUKKAH = "Hanukkah"
    TURKISH = "Turkish"
    SMOOTHIES = "Smoothies"
    STRAWBERRY = "Strawberry"
    SPREADS = "Spreads"
    BEAR = "Bear"
    BAR_COOKIE = "Bar Cookie"
    NO_SHELL_FISH = "No Shell Fish"
    SALAD_DRESSINGS = "Salad Dressings"
    PERUVIAN = "Peruvian"
    BASS = "Bass"
    LIME = "Lime"
    PEARS = "Pears"
    BREADS = "Breads"
    SCOTTISH = "Scottish"
    AVOCADO = "Avocado"
    CRANBERRY_SAUCE = "Cranberry Sauce"
    BERRIES = "Berries"
    CROCK_POT_SLOW_COOKER = "Crock Pot Slow Cooker"
    HUNGARIAN = "Hungarian"
    CHOWDERS = "Chowders"
    GEORGIAN = "Georgian"
    AUSTRIAN = "Austrian"
    COSTA_RICAN = "Costa Rican"
    MEDIUM_GRAIN_RICE = "Medium Grain Rice"
    NORWEGIAN = "Norwegian"
    SOY_TOFU = "Soy/Tofu"
    ORANGES = "Oranges"
    BAKING = "Baking"
    FREEZER = "Freezer"
    QUICK_BREADS = "Quick Breads"
    SMALL_APPLIANCE = "Small Appliance"
    CUBAN = "Cuban"
    GOOSE = "Goose"
    PAKISTANI = "Pakistani"
    PASTA_SHELLS = "Pasta Shells"
    MOROCCAN = "Moroccan"
    STOCKS = "Stocks"
    STEAM = "Steam"
    CHICKEN_STEWS = "Chicken Stews"
    WELSH = "Welsh"
    CLEAR_SOUP = "Clear Soup"
    VEGAN = "Vegan"
    PUERTO_RICAN = "Puerto Rican"
    TEX_MEX = "Tex Mex"
    CHEESE = "Cheese"
    POT_PIE = "Pot Pie"
    ONE_DISH_MEAL = "One Dish Meal"
    REYNOLDS_WRAP_CONTEST = "Reynolds Wrap Contest"
    LUNCH_SNACKS = "Lunch/Snacks"
    CHICKEN_THIGH_LEG = "Chicken Thigh & Leg"
    DEER = "Deer"
    COLLEGE_FOOD = "College Food"
    STEW = "Stew"
    FILIPINO = "Filipino"
    CRAB = "Crab"
    STIR_FRY = "Stir Fry"
    BEGINNER_COOK = "Beginner Cook"
    WHITE_RICE = "White Rice"
    FOR_LARGE_GROUPS = "For Large Groups"
    LONG_GRAIN_RICE = "Long Grain Rice"
    DESSERT = "Dessert"
    KIWIFRUIT = "Kiwifruit"
    CARIBBEAN = "Caribbean"
    MANICOTTI = "Manicotti"
    SAVORY_PIES = "Savory Pies"
    NUTS = "Nuts"
    BRAZILIAN = "Brazilian"
    CAMPING = "Camping"
    PIE = "Pie"
    DUCK_BREASTS = "Duck Breasts"
    HONDURAN = "Honduran"
    TUNA = "Tuna"
    LESS_THAN_15_MINS = "< 15 Mins"
    PLUMS = "Plums"
    SOUTH_AMERICAN = "South American"
    FINNISH = "Finnish"
    CHEESECAKE = "Cheesecake"
    EGYPTIAN = "Egyptian"
    CATFISH = "Catfish"
    PALESTINIAN = "Palestinian"
    CAMBODIAN = "Cambodian"
    HIGH_FIBER = "High Fiber"
    SWISS = "Swiss"
    DUCK = "Duck"
    CHARD = "Chard"
    WHOLE_TURKEY = "Whole Turkey"
    POTATO = "Potato"
    COLOMBIAN = "Colombian"
    LEBANESE = "Lebanese"
    CANADIAN = "Canadian"
    PRESSURE_COOKER = "Pressure Cooker"
    GREENS = "Greens"
    MICROWAVE = "Microwave"
    SQUID = "Squid"
    DEHYDRATOR = "Dehydrator"
    PENNSYLVANIA_DUTCH = "Pennsylvania Dutch"
    HOMEOPATHY_REMEDIES = "Homeopathy/Remedies"
    SPRING = "Spring"
    PAPAYA = "Papaya"
    INDIAN = "Indian"
    STRAWBERRIES_DESSERTS = "Strawberries Desserts"
    ROAST = "Roast"
    SHAKES = "Shakes"
    BIRTHDAY = "Birthday"
    RAMADAN = "Ramadan"
    RICE = "Rice"
    VEGETABLE = "Vegetable"
    HAM = "Ham"
    HALLOWEEN_COCKTAIL = "Halloween Cocktail"
    MEATBALLS = "Meatballs"
    RASPBERRIES = "Raspberries"
    GRAINS = "Grains"
    SOMALIAN = "Somalian"
    ECUADOREAN = "Ecuadorean"
    WILD_GAME = "Wild Game"
    PERCH = "Perch"
    GUMBO = "Gumbo"
    KOREAN = "Korean"
    SOUTHWEST_ASIA = "Southwest Asia (middle East)"
    ST_PATRICKS_DAY = "St. Patrick's Day"
    CHINESE_NEW_YEAR = "Chinese New Year"
    LOBSTER = "Lobster"
    BEVERAGES = "Beverages"
    BRUNCH = "Brunch"
    WINTER = "Winter"
    GELATIN = "Gelatin"
    BELGIAN = "Belgian"
    PASTA_ELBOW = "Pasta Elbow"
    OVEN = "Oven"
    MOOSE = "Moose"
    NO_COOK = "No Cook"
    DESSERTS_EASY = "Desserts Easy"
    LEMON = "Lemon"
    ETHIOPIAN = "Ethiopian"
    SOUTHWESTERN_US = "Southwestern U.S."
    MEAT = "Meat"
    BEEF_CROCK_POT = "Beef Crock Pot"
    DANISH = "Danish"
    CITRUS = "Citrus"
    GUATEMALAN = "Guatemalan"
    BREAD_MACHINE = "Bread Machine"
    SERVED_HOT_NEW_YEARS = "Served Hot New Years"
    HOUSEHOLD_CLEANER = "Household Cleaner"
    YEAST_BREADS = "Yeast Breads"
    PORK = "Pork"
    FROM_SCRATCH = "From Scratch"
    LOW_CHOLESTEROL = "Low Cholesterol"
    BREAKFAST = "Breakfast"
    GERMAN = "German"
    TEMPEH = "Tempeh"
    INEXPENSIVE = "Inexpensive"
    COOKIE_BROWNIE = "Cookie & Brownie"
    PUNCH_BEVERAGE = "Punch Beverage"
    BROIL_GRILL = "Broil/Grill"
    BATH_BEAUTY = "Bath/Beauty"
    PEANUT_BUTTER = "Peanut Butter"
    OYSTERS = "Oysters"
    CHOCOLATE_CHIP_COOKIES = "Chocolate Chip Cookies"
    APPLE = "Apple"
    PUMPKIN = "Pumpkin"
    CHICKEN_BREAST = "Chicken Breast"
    CHICKEN_STEW = "Chicken Stew"
    FROZEN_DESSERTS = "Frozen Desserts"
    RUSSIAN = "Russian"
    CZECH = "Czech"
    OCTOPUS = "Octopus"
    LAMB_SHEEP = "Lamb/Sheep"
    NAVY_BEAN_SOUP = "Navy Bean Soup"
    COCONUT = "Coconut"
    NEPALESE = "Nepalese"
    WHOLE_DUCK = "Whole Duck"
    LABOR_DAY = "Labor Day"
    OATMEAL = "Oatmeal"
    SWEDISH = "Swedish"
    TILAPIA = "Tilapia"
    MANGO = "Mango"
    HUNAN = "Hunan"
    CHINESE = "Chinese"
    ICE_CREAM = "Ice Cream"
    TURKEY_BREASTS = "Turkey Breasts"
    HEALTHY = "Healthy"
    BEEF_SANDWICHES = "Beef Sandwiches"
    CRAWFISH = "Crawfish"
    MEMORIAL_DAY = "Memorial Day"
    BEEF_ORGAN_MEATS = "Beef Organ Meats"
    CHILEAN = "Chilean"
    SPINACH = "Spinach"
    EUROPEAN = "European"
    PENNE = "Penne"
    BLACK_BEANS = "Black Beans"
    HIGH_IN_DIABETIC_FRIENDLY = "High In... Diabetic Friendly"
    RABBIT = "Rabbit"
    ONIONS = "Onions"
    BEANS = "Beans"
    CHICKEN_LIVERS = "Chicken Livers"
    VENEZUELAN = "Venezuelan"

# Veri setinin konumu
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'dataset.csv')

# Anahtar kelime kontrolü için yardımcı fonksiyon
def contains_keyword(text, keyword):
    """
    Verilen metinde anahtar kelimenin geçip geçmediğini kontrol eder
    """
    if not text or not isinstance(text, str):
        return False
    return keyword.lower() in text.lower()

def check_recipe_keyword(recipe, keyword):
    """
    Tarif içinde belirli bir anahtar kelimenin bulunup bulunmadığını kontrol eder
    Tarif ismi, içindekiler ve açıklama alanlarında arama yapar
    """
    if not isinstance(keyword, RecipeKeyword):
        keyword_value = keyword
    else:
        keyword_value = keyword.value
    
    # İsimde kontrol et
    if contains_keyword(recipe.get('Name', ''), keyword_value):
        return True
    
    # İçeriklerde kontrol et
    if contains_keyword(recipe.get('RecipeIngredientParts', ''), keyword_value):
        return True
    
    # Kategorilerde veya açıklamada kontrol et (eğer bu alanlar varsa)
    if contains_keyword(recipe.get('Category', ''), keyword_value):
        return True
    
    if contains_keyword(recipe.get('Description', ''), keyword_value):
        return True
    
    return False

def filter_recipes_by_keyword(recipes, keyword):
    """
    Tarifleri belirli bir anahtar kelimeye göre filtreler
    """
    if isinstance(recipes, pd.DataFrame):
        filtered = []
        for _, recipe in recipes.iterrows():
            if check_recipe_keyword(recipe, keyword):
                filtered.append(recipe)
        return pd.DataFrame(filtered) if filtered else pd.DataFrame()
    return pd.DataFrame()

def load_recipe_data():
    """
    Tarif veri setini yükler, bulunamazsa örnek veri oluşturur
    """
    try:
        # CSV dosyasını oku
        data = pd.read_csv(DATA_PATH)
        print(f"Veri seti yüklendi: {len(data)} tarifler")
        return data
    except FileNotFoundError:
        print("Veri seti bulunamadı, örnek veri oluşturuluyor...")
        return create_sample_recipe_data()

def create_sample_recipe_data(n_samples=100):
    """
    Örnek tarif verileri oluşturur
    """
    np.random.seed(42)
    
    # Örnek tarifler için bileşenler
    ingredients = [
        "domates", "soğan", "sarımsak", "zeytinyağı", "tuz", "karabiber", "et", "tavuk",
        "nohut", "bulgur", "pirinç", "makarna", "un", "süt", "yoğurt", "peynir", "yumurta",
        "elma", "muz", "portakal", "çilek", "havuç", "patates", "patlıcan", "kabak"
    ]
    
    # İngilizce karşılıkları
    ingredients_en = [
        "tomato", "onion", "garlic", "olive oil", "salt", "pepper", "meat", "chicken",
        "chickpeas", "bulgur", "rice", "pasta", "flour", "milk", "yogurt", "cheese", "egg",
        "apple", "banana", "orange", "strawberry", "carrot", "potato", "eggplant", "zucchini"
    ]
    
    # Türkçe ve İngilizce tarif isimleri
    recipe_names_tr = [
        "Domates Çorbası", "Mercimek Çorbası", "Etli Güveç", "Tavuk Sote", "Kuru Fasulye",
        "Pilav", "Makarna Salatası", "Menemen", "Patlıcan Musakka", "Kabak Dolması"
    ]
    
    recipe_names_en = [
        "Tomato Soup", "Lentil Soup", "Meat Stew", "Chicken Saute", "Bean Stew",
        "Rice Pilaf", "Pasta Salad", "Turkish Egg Dish", "Eggplant Moussaka", "Stuffed Zucchini"
    ]
    
    # Veri çerçevesi oluştur
    data = []
    
    for i in range(n_samples):
        # Rastgele tarif içerikleri oluştur
        n_ingr = np.random.randint(3, 10)
        sample_ingredients_tr = np.random.choice(ingredients, size=n_ingr, replace=False)
        
        # İngilizce karşılıkları bul
        sample_ingredients_en = [ingredients_en[ingredients.index(ing)] for ing in sample_ingredients_tr]
        
        # Tarif adı seç
        recipe_name_tr = np.random.choice(recipe_names_tr)
        recipe_name_en = recipe_names_en[recipe_names_tr.index(recipe_name_tr)]
        
        # Kalori ve besinsel değerleri oluştur
        calories = np.random.randint(100, 800)
        carbs = np.random.randint(5, 80)
        protein = np.random.randint(2, 40)
        fat = np.random.randint(1, 30)
        
        # Tarifi oluştur
        recipe = {
            'Name': recipe_name_en,
            'TurkishName': recipe_name_tr,
            'RecipeIngredientParts': ', '.join(sample_ingredients_en),
            'TurkishIngredients': ', '.join(sample_ingredients_tr),
            'Calories': calories,
            'Carbs': carbs,
            'Protein': protein,
            'Fat': fat,
            'RecipeId': i
        }
        
        data.append(recipe)
    
    # DataFrame oluştur
    df = pd.DataFrame(data)
    
    # CSV olarak kaydet
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Örnek veri oluşturuldu ve kaydedildi: {DATA_PATH}")
    
    return df

def create_diet_list(calorie_limit=2000):
    """
    Belirli bir kalori limitine göre diyet listesi oluşturur
    """
    # Veriyi yükle
    recipes = load_recipe_data()
    
    # Kahvaltı, öğle yemeği, akşam yemeği olarak bölümlendir
    breakfast = recipes[recipes['Calories'] <= calorie_limit * 0.3].sample(1)
    lunch = recipes[recipes['Calories'] <= calorie_limit * 0.35].sample(1)
    dinner = recipes[recipes['Calories'] <= calorie_limit * 0.35].sample(1)
    
    # Toplam kalori hesabı yap
    total_calories = breakfast['Calories'].sum() + lunch['Calories'].sum() + dinner['Calories'].sum()
    
    # Eğer atıştırmalık için yer varsa ekle
    if total_calories < calorie_limit:
        snack_limit = calorie_limit - total_calories
        snacks = recipes[(recipes['Calories'] <= snack_limit) & (recipes['Calories'] > 0)].sample(min(2, len(recipes)))
    else:
        snacks = pd.DataFrame()  # Boş DataFrame
    
    # Tüm öğünleri birleştir
    diet_plan = pd.concat([breakfast, lunch, dinner, snacks])
    
    # Yeni bir sütun ekleyerek öğün tipini belirt
    meal_types = ['Breakfast'] * len(breakfast) + ['Lunch'] * len(lunch) + ['Dinner'] * len(dinner) + ['Snack'] * len(snacks)
    diet_plan['MealType'] = meal_types
    
    return diet_plan

def create_diet_list_turkish(calorie_limit=2000):
    """
    Türkçe tariflerle diyet listesi oluşturur
    """
    diet_plan = create_diet_list(calorie_limit)
    
    # Türkçe tarif adlarını ve malzemeleri kullan
    diet_plan = diet_plan.rename(columns={
        'Name': 'EnglishName',
        'RecipeIngredientParts': 'EnglishIngredients'
    })
    
    diet_plan['Name'] = diet_plan['TurkishName']
    diet_plan['RecipeIngredientParts'] = diet_plan['TurkishIngredients']
    
    # Öğün tiplerini Türkçeye çevir
    meal_type_tr = {
        'Breakfast': 'Kahvaltı',
        'Lunch': 'Öğle Yemeği',
        'Dinner': 'Akşam Yemeği',
        'Snack': 'Atıştırmalık'
    }
    
    diet_plan['MealType'] = diet_plan['MealType'].map(meal_type_tr)
    
    return diet_plan

def recommend_recipes(recipe_index, n_recommendations=5):
    """
    Belirli bir tarife benzeyen tarifleri önerir
    """
    # Veriyi yükle
    recipes = load_recipe_data()
    
    if recipe_index >= len(recipes):
        recipe_index = 0  # Geçersiz indeks durumunda ilk tarifi kullan
    
    # TF-IDF vektörleştirici oluştur ve uygula
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(recipes['RecipeIngredientParts'].fillna(''))
    
    # Kosinüs benzerliklerini hesapla
    cosine_sim = cosine_similarity(tfidf_matrix[recipe_index:recipe_index+1], tfidf_matrix).flatten()
    
    # En benzer tariflerin indekslerini al (kendisi hariç)
    similar_indices = cosine_sim.argsort()[::-1][1:n_recommendations+1]
    
    return recipes.iloc[similar_indices]

def recommend_recipes_turkish(recipe_index, n_recommendations=5):
    """
    Türkçe tarif önerileri yapar
    """
    recommendations = recommend_recipes(recipe_index, n_recommendations)
    
    # Türkçe tarif adlarını ve malzemeleri kullan
    recommendations = recommendations.rename(columns={
        'Name': 'EnglishName',
        'RecipeIngredientParts': 'EnglishIngredients'
    })
    
    recommendations['Name'] = recommendations['TurkishName']
    recommendations['RecipeIngredientParts'] = recommendations['TurkishIngredients']
    
    return recommendations

if __name__ == "__main__":
    # Test amaçlı
    print("Örnek diyet listesi:")
    diet = create_diet_list(2000)
    print(diet[['Name', 'Calories', 'MealType']])
    
    print("\nTürkçe diyet listesi:")
    diet_tr = create_diet_list_turkish(2000)
    print(diet_tr[['Name', 'Calories', 'MealType']])
    
    print("\nBenzer tarifler:")
    similar = recommend_recipes(0, 3)
    print(similar[['Name', 'Calories']])