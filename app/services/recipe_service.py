import pandas as pd
from typing import List, Dict, Any

def get_recipe_names_by_keyword(keyword: str):
    """
    Verilen anahtar kelimeye göre tarif isimlerini döndürür.
    """
    # CSV dosyasını yükleme
    data = pd.read_csv('./data/dataset.csv')

    # Anahtar kelimeye göre filtreleme
    filtered_recipes = data[data['Keywords'].str.contains(keyword, na=False)]
    
    # Tariflerin isimlerini al
    recipe_names = filtered_recipes['Name'].tolist()
    return recipe_names

def get_breakfast_recipes() -> List[Dict[str, Any]]:
    """Sabah kahvaltısı için tarifler döndürür"""
    breakfast_recipes = [
        {
            "RecipeId": 101001,
            "Name": "Avokadolu Yumurta Ekmek",
            "CookTime": "PT5M",
            "PrepTime": "PT5M",
            "TotalTime": "PT10M",
            "RecipeIngredientParts": "c(\"tam buğday ekmeği\", \"avokado\", \"yumurta\", \"tuz\", \"karabiber\")",
            "Calories": 250.0,
            "FatContent": 15.0,
            "SaturatedFatContent": 3.5,
            "CholesterolContent": 180.0,
            "SodiumContent": 220.0,
            "CarbohydrateContent": 20.0,
            "FiberContent": 5.0,
            "SugarContent": 1.5,
            "ProteinContent": 10.0,
            "RecipeInstructions": "c(\"Ekmeği kızartın.\", \"Avokadoyu ezin ve üzerine yayın.\", \"Yumurtayı pişirin ve ekmeğin üzerine yerleştirin.\", \"Tuz ve karabiber serpin.\", \"Servis edin.\")"
        },
        {
            "RecipeId": 101002,
            "Name": "Yulaf Ezmesi ve Meyveler",
            "CookTime": "PT3M",
            "PrepTime": "PT2M",
            "TotalTime": "PT5M",
            "RecipeIngredientParts": "c(\"yulaf ezmesi\", \"süt\", \"bal\", \"muz\", \"çilek\", \"yaban mersini\")",
            "Calories": 280.0,
            "FatContent": 5.0,
            "SaturatedFatContent": 1.0,
            "CholesterolContent": 0.0,
            "SodiumContent": 50.0,
            "CarbohydrateContent": 50.0,
            "FiberContent": 6.0,
            "SugarContent": 20.0,
            "ProteinContent": 8.0,
            "RecipeInstructions": "c(\"Yulafı sütle karıştırın.\", \"Mikrodalga fırında 2 dakika pişirin.\", \"Meyveleri ekleyin.\", \"Bal ile tatlandırın.\")"
        },
        {
            "RecipeId": 101003,
            "Name": "Yulaflı Muz ve Fındık Ezmesi Smoothie",
            "CookTime": "PT0M",
            "PrepTime": "PT5M",
            "TotalTime": "PT5M",
            "RecipeIngredientParts": "c(\"muz\", \"yulaf\", \"fındık ezmesi\", \"süt\", \"bal\")",
            "Calories": 320.0,
            "FatContent": 12.0,
            "SaturatedFatContent": 2.5,
            "CholesterolContent": 0.0,
            "SodiumContent": 120.0,
            "CarbohydrateContent": 45.0,
            "FiberContent": 5.0,
            "SugarContent": 25.0,
            "ProteinContent": 12.0,
            "RecipeInstructions": "c(\"Tüm malzemeleri blendere koyun.\", \"Pürüzsüz olana kadar karıştırın.\", \"Hemen servis yapın.\")"
        }
    ]
    return breakfast_recipes

def get_lunch_recipes() -> List[Dict[str, Any]]:
    """Öğle yemeği için tarifler döndürür"""
    lunch_recipes = [
        {
            "RecipeId": 202001,
            "Name": "Tavuklu Kinoa Salatası",
            "CookTime": "PT15M",
            "PrepTime": "PT10M",
            "TotalTime": "PT25M",
            "RecipeIngredientParts": "c(\"kinoa\", \"ızgara tavuk göğsü\", \"domates\", \"salatalık\", \"kırmızı soğan\", \"feta peyniri\", \"zeytinyağı\", \"limon suyu\")",
            "Calories": 350.0,
            "FatContent": 14.0,
            "SaturatedFatContent": 4.0,
            "CholesterolContent": 65.0,
            "SodiumContent": 400.0,
            "CarbohydrateContent": 30.0,
            "FiberContent": 5.0,
            "SugarContent": 3.0,
            "ProteinContent": 28.0,
            "RecipeInstructions": "c(\"Kinoayı haşlayın.\", \"Tavuğu ızgarada pişirin ve küçük parçalara ayırın.\", \"Tüm malzemeleri karıştırın.\", \"Zeytinyağı ve limon suyu ile soslandırın.\")"
        },
        {
            "RecipeId": 202002,
            "Name": "Sebzeli Tavuk Sote",
            "CookTime": "PT20M",
            "PrepTime": "PT10M",
            "TotalTime": "PT30M",
            "RecipeIngredientParts": "c(\"tavuk göğsü\", \"kabak\", \"havuç\", \"kapya biber\", \"zeytinyağı\", \"tuz\", \"karabiber\")",
            "Calories": 310.0,
            "FatContent": 12.0,
            "SaturatedFatContent": 2.0,
            "CholesterolContent": 70.0,
            "SodiumContent": 300.0,
            "CarbohydrateContent": 10.0,
            "FiberContent": 3.0,
            "SugarContent": 4.0,
            "ProteinContent": 35.0,
            "RecipeInstructions": "c(\"Tavukları doğrayın ve soteleyin.\", \"Sebzeleri doğrayıp ekleyin.\", \"Zeytinyağı, tuz ve karabiber ile tatlandırın.\", \"Orta ateşte pişirin.\", \"Sıcak servis edin.\")"
        },
        {
            "RecipeId": 202003,
            "Name": "Mercimek Köftesi",
            "CookTime": "PT20M",
            "PrepTime": "PT15M",
            "TotalTime": "PT35M",
            "RecipeIngredientParts": "c(\"kırmızı mercimek\", \"ince bulgur\", \"soğan\", \"maydanoz\", \"zeytinyağı\", \"biber salçası\", \"tuz\", \"karabiber\", \"kimyon\")",
            "Calories": 220.0,
            "FatContent": 7.0,
            "SaturatedFatContent": 1.0,
            "CholesterolContent": 0.0,
            "SodiumContent": 350.0,
            "CarbohydrateContent": 35.0,
            "FiberContent": 8.0,
            "SugarContent": 2.0,
            "ProteinContent": 10.0,
            "RecipeInstructions": "c(\"Mercimeği haşlayın.\", \"Haşlanmış mercimeğe bulgur ekleyip demlenmeye bırakın.\", \"Soğanları kavurun ve karışıma ekleyin.\", \"Baharatlar ve maydanozu ekleyip karıştırın.\", \"Köfte şekli verip servis yapın.\")"
        }
    ]
    return lunch_recipes

def get_dinner_recipes() -> List[Dict[str, Any]]:
    """Akşam yemeği için tarifler döndürür"""
    dinner_recipes = [
        {
            "RecipeId": 303001,
            "Name": "Fırında Somon ve Sebzeler",
            "CookTime": "PT20M",
            "PrepTime": "PT10M",
            "TotalTime": "PT30M",
            "RecipeIngredientParts": "c(\"somon fileto\", \"brokoli\", \"havuç\", \"kabak\", \"zeytinyağı\", \"limon suyu\", \"sarımsak\", \"tuz\", \"karabiber\")",
            "Calories": 320.0,
            "FatContent": 18.0,
            "SaturatedFatContent": 3.0,
            "CholesterolContent": 80.0,
            "SodiumContent": 330.0,
            "CarbohydrateContent": 8.0,
            "FiberContent": 4.0,
            "SugarContent": 3.0,
            "ProteinContent": 32.0,
            "RecipeInstructions": "c(\"Somonu ve sebzeleri fırın tepsisine yerleştirin.\", \"Zeytinyağı, limon suyu, sarımsak, tuz ve karabiber karışımını üzerine dökün.\", \"200°C'de 20 dakika pişirin.\", \"Sıcak servis yapın.\")"
        },
        {
            "RecipeId": 303002,
            "Name": "Köfteli ve Sebzeli Güveç",
            "CookTime": "PT35M",
            "PrepTime": "PT15M",
            "TotalTime": "PT50M",
            "RecipeIngredientParts": "c(\"dana kıyma\", \"soğan\", \"sarımsak\", \"patates\", \"patlıcan\", \"kabak\", \"domates\", \"biber\", \"zeytinyağı\", \"tuz\", \"karabiber\")",
            "Calories": 380.0,
            "FatContent": 20.0,
            "SaturatedFatContent": 6.0,
            "CholesterolContent": 70.0,
            "SodiumContent": 450.0,
            "CarbohydrateContent": 25.0,
            "FiberContent": 6.0,
            "SugarContent": 8.0,
            "ProteinContent": 25.0,
            "RecipeInstructions": "c(\"Kıyma, soğan ve baharatlarla köfteler hazırlayın.\", \"Sebzeleri doğrayın.\", \"Güveci yağlayın ve sebzeleri yerleştirin.\", \"Köfteleri üzerine dizin.\", \"Domates sosunu üzerine dökün.\", \"180°C'de 35 dakika pişirin.\")"
        },
        {
            "RecipeId": 303003,
            "Name": "Mercimek Çorbası ve Tam Buğday Ekmeği",
            "CookTime": "PT25M",
            "PrepTime": "PT10M",
            "TotalTime": "PT35M",
            "RecipeIngredientParts": "c(\"kırmızı mercimek\", \"soğan\", \"havuç\", \"sarımsak\", \"zeytinyağı\", \"su\", \"tuz\", \"kimyon\")",
            "Calories": 180.0,
            "FatContent": 6.0,
            "SaturatedFatContent": 1.0,
            "CholesterolContent": 0.0,
            "SodiumContent": 400.0,
            "CarbohydrateContent": 25.0,
            "FiberContent": 5.0,
            "SugarContent": 3.0,
            "ProteinContent": 10.0,
            "RecipeInstructions": "c(\"Tüm malzemeleri tencereye koyun.\", \"Orta ateşte mercimekler yumuşayana kadar pişirin.\", \"Çorbayı blenderdan geçirin.\", \"İsteğe bağlı olarak limonla servis edin.\")"
        }
    ]
    return dinner_recipes
