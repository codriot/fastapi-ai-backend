import pandas as pd

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
