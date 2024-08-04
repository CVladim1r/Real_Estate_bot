import pandas as pd

def read_excel(file_path):
    return pd.read_excel(file_path)

def escape_single_quotes(value):
    if pd.isna(value):
        return value
    return str(value).replace("'", "''")

def generate_sql(df):
    properties_sql = "INSERT INTO properties (house_id, number, area, type, ownership_form, cadastral_number, ownership_doc, general_comment) VALUES\n"
    owners_sql = "INSERT INTO owners (property_id, fio, birth_date, share, comment) VALUES\n"
    
    properties_values = []
    owners_values = []
    
    property_id_mapping = {}
    next_property_id = 1

    for index, row in df.iterrows():
        number = row.get('Номер помещения по экспликации', None)
        area = row.get('Общая площадь помещения (без летних) кв.м.', None)
        type = row.get('Назначение помещения (жилое, не жилое)', None)
        ownership_form = row.get('Форма собственности (Федеральная, государственная города Москвы, частная)', None)
        house_id = 10
        area = pd.to_numeric(area, errors='coerce')
        if pd.isna(area):
            area = 'NULL'
        else:
            area = f"{area:.2f}"

        # Преобразуем номер в целое число
        try:
            number = int(number)
        except (ValueError, TypeError):
            number = 'NULL'

        # Если номер помещения еще не был обработан, добавляем его в список свойств
        if number != 'NULL' and number not in property_id_mapping:
            property_id = next_property_id
            property_id_mapping[number] = property_id
            next_property_id += 1
            properties_values.append(
                f"({house_id}, {number}, {area}, '{escape_single_quotes(type)}', '{escape_single_quotes(ownership_form)}', NULL, NULL, NULL)"
            )
        elif number != 'NULL':
            property_id = property_id_mapping[number]

        fio = row.get('Собственник помещения (ФИО физического либо юридического лица)', None)
        birth_date = row.get('Дата рождения собственника помещения', None)
        
        if pd.isna(birth_date) or birth_date in ['Не определено', '']:
            birth_date_str = 'NULL'
        else:
            try:
                birth_date = pd.to_datetime(birth_date, dayfirst=True, errors='coerce')
                if pd.isna(birth_date):
                    birth_date_str = 'NULL'
                else:
                    birth_date_str = f"'{birth_date.strftime('%Y-%m-%d')}'"
            except Exception as e:
                print(f"Error parsing date: {e}")
                birth_date_str = 'NULL'
        
        share = row.get('Площадь, принадлежащая каждому собственнику помещения (S3) кв.м.', None)
        share = pd.to_numeric(share, errors='coerce')
        if pd.isna(share):
            share = 'NULL'
        else:
            share = f"{share:.2f}"

        if number != 'NULL':
            owners_values.append(
                f"({property_id}, '{escape_single_quotes(fio)}', {birth_date_str}, {share}, NULL)"
            )

    properties_sql += ",\n".join(properties_values) + ";\n"
    owners_sql += ",\n".join(owners_values) + ";\n"

    return properties_sql + "\n" + owners_sql

def main():
    file_path = 'Хлобыстова ул. д.18 корп.1.xlsx'
    df = read_excel(file_path)
    sql = generate_sql(df)
    print(sql)

if __name__ == "__main__":
    main()
