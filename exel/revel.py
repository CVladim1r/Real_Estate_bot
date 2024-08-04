import pandas as pd
import os

def read_excel(file_path):
    return pd.read_excel(file_path)

def escape_single_quotes(value):
    if pd.isna(value):
        return value
    return str(value).replace("'", "''")

def generate_sql(df, house_id, next_property_id):
    properties_sql = "INSERT INTO properties (house_id, number, area, type, ownership_form, cadastral_number, ownership_doc, general_comment) VALUES\n"
    owners_sql = "INSERT INTO owners (property_id, fio, birth_date, share, comment) VALUES\n"
    
    properties_values = []
    owners_values = []
    
    property_id_mapping = {}

    for index, row in df.iterrows():
        number = row.get('Номер помещения по экспликации', None)
        area = row.get('Общая площадь помещения (без летних) кв.м.', None)
        type = row.get('Назначение помещения (жилое, не жилое)', None)
        ownership_form = row.get('Форма собственности (Федеральная, государственная города Москвы, частная)', None)
        
        area = pd.to_numeric(area, errors='coerce')
        if pd.isna(area):
            area = 'NULL'
        else:
            area = f"{area:.2f}"

        try:
            number = int(number)
        except (ValueError, TypeError):
            number = 'NULL'

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

    return properties_sql, owners_sql, next_property_id

def process_files(file_paths):
    all_properties_sql = ""
    all_owners_sql = ""
    
    house_id = 1  # Start house_id from 1
    next_property_id = 1  # Start property_id from 1

    for file_path in file_paths:
        df = read_excel(file_path)
        properties_sql, owners_sql, next_property_id = generate_sql(df, house_id, next_property_id)
        all_properties_sql += properties_sql + "\n"
        all_owners_sql += owners_sql + "\n"
        
        house_id += 1  # Increment house_id for each file

    return all_properties_sql, all_owners_sql

def save_sql_to_file(sql, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(sql)

def main():
    file_paths = [
        'Волгоградский_проспект,_дом_187_16_xls.xlsx',
        'Кузнецова генерала ул. д.13 корп.2.xlsx',
        'Привольная ул. д.19.xlsx',
        'Привольная ул. д.23 корп.2.xlsx',
        'Привольная ул. д.23.xlsx',
        'Привольная ул. д.25.xlsx',
        'Рязанский просп. д.64 корп.2.xlsx',
        'Самаркандский_бульв_,_квартал_134а_д_корп_2.xlsx',
        'Самаркандский_бульв_,_квартал_137а_д_корп_9.xlsx',
        'Хлобыстова ул. д.18 корп.1.xlsx'
    ]  # Add more file paths as needed
    
    all_properties_sql, all_owners_sql = process_files(file_paths)
    
    # Combine the SQL queries into one final output
    final_sql = all_properties_sql + "\n" + all_owners_sql
    
    # Save the combined SQL to a file
    save_sql_to_file(final_sql, 'combined_properties_and_owners.sql')
    
    # Print the combined SQL for owners
    print(all_owners_sql)

if __name__ == "__main__":
    main()
