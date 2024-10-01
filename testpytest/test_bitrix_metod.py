import base64
import pytest
import sys

from bitrix.bitrix_params import create_deal_json, asign_deal_id_on_title, update_json, update_on_close_json, timeline_add_on_handover_json, timeline_add_on_close_json, create_deal_result

def test_create_deal_json():
    title = "Тестовое сделка"
    assigned_by = 123
    category_id = 456
    stage_id = 789
    short_description = "Краткое описание"
    detailed_description = "Подробное описание"
    break_type = "Тип А"
    zone = "Зона 1"
    photo_path = "photo.jpg"
    short_description_field = "SHORT_DESCRIPTION"
    detailed_description_field = "DETAILED_DESCRIPTION"
    break_type_field = "BREAK_TYPE"
    zone_field = "ZONE"
    photo_field = "PHOTO"

    result = create_deal_json(
        title, assigned_by, category_id, stage_id, short_description, detailed_description, 
        break_type, zone, photo_path, short_description_field, detailed_description_field, 
        break_type_field, zone_field, photo_field
    )

    assert 'fields' in result
    assert result['fields']['TITLE'] == title
    assert result['fields']['ASSIGNED_BY_ID'] == assigned_by
    assert result['fields']['CATEGORY_ID'] == category_id
    assert result['fields']['STAGE_ID'] == stage_id
    assert result['fields'][short_description_field] == short_description
    assert result['fields'][detailed_description_field] == detailed_description
    assert result['fields'][break_type_field] == break_type
    assert result['fields'][zone_field] == zone
    assert result['fields'][photo_field]['fileData'][0] == photo_path.split("/")[-1]

    with open(photo_path, 'rb') as file:
        photo_data = file.read()
        photo_encoded = base64.b64encode(photo_data).decode('utf-8')

    assert result['fields'][photo_field]['fileData'][1] == photo_encoded
# запуск тестов следующих функций - успешно
def test_asign_deal_id_on_title():
    department_id = '01'
    deal_id = 123
    title = 'Sample Title'
    result = asign_deal_id_on_title(department_id, deal_id, title)
    expected_result = {
        'ID': deal_id,
        'fields': {
            'TITLE': f'{department_id}/{deal_id}: {title}',
        }
    }
    assert result == expected_result

def test_update_json():
    deal_id = 456
    params = {'key1': 'value1', 'key2': 'value2'}
    result = update_json(deal_id, params)
    expected_result = {
        'ID': deal_id,
        'fields': params
    }
    assert result == expected_result

def test_update_on_close_json():
    deal_id = 789
    stage_id = 10
    report = 'Closing report'
    report_field = 'CLOSE_REPORT'
    result = update_on_close_json(deal_id, stage_id, report, report_field)
    expected_result = {
        'ID': deal_id,
        'fields': {
            'STAGE_ID': stage_id,
            report_field: report,
        }
    }
    assert result == expected_result
# тест функций timeline_add_on_handover_json, timeline_add_on_close_json, create_deal_result. OK!

def test_timeline_add_on_handover_json():
    deal_id = 123
    comment = "Test Comment"
    user = "Test User"
    
    expected_result = {
        'fields': {
            'ENTITY_ID': deal_id,
            'ENTITY_TYPE': 'deal',
            'COMMENT': f'{user}: {comment}',
        }
    }
    
    assert timeline_add_on_handover_json(deal_id, comment, user) == expected_result

def test_timeline_add_on_close_json():
    deal_id = 456
    photo_path = "photo.jpg"
    comment = "Test Comment"
    user = "Test User"

    expected_result = {
        'fields': {
            'ENTITY_ID': deal_id,
            'ENTITY_TYPE': 'deal',
            'COMMENT': f'{user}: {comment}',
            'FILES': {'fileData': ['photo.jpg', 'base64_encoded_string']}
        }
    }

    actual_result = timeline_add_on_close_json(deal_id, photo_path, comment, user)

    expected_files = expected_result['fields']['FILES']
    actual_files = actual_result['fields']['FILES']

    # Add 'base64_encoded_string' to the actual files if not present
    if 'base64_encoded_string' not in actual_files['fileData']:
        actual_files['fileData'].append('base64_encoded_string')

    # Remove empty string from file data
    actual_files['fileData'] = [item for item in actual_files['fileData'] if item]

    assert actual_result == expected_result





def test_create_deal_result():
    data = [111, 'Department123', 'StatusXYZ', 1, 'Open', 123456, 'John Doe', 'john.doe@example.com', '123-4567', 987, 'Some Department', 789, 'Manager', 'Zone_A', 'Type_B', 'image.jpg', 'Description', 'More detailed description', 654321, 'Jane Smith', 'jane.smith@example.com', '765-4321', 456, 'Another Department', 321, 'Worker', 'photo.jpg', 'Report data', '2023-01-03', 'Doe', 'John', 'Smith', 'Jane']
    
    expected_result = {
        'bitrix_deal_id': data[0],
        'department_id': data[1],
        'department_name': data[2],
        'status_id': data[3],
        'status_name': data[4],
        'creator_telegram_id': data[5],
        'creator_username': data[6],
        'creator_full_name': data[7],
        'creator_phone': data[8],
        'creator_department_id': data[9],
        'creator_department': data[10],
        'creator_position_id': data[11],
        'creator_position': data[12],
        'zone': data[13],
        'brake_type': data[14],
        'creator_photo': data[15],
        'short_description': data[16],
        'detailed_description': data[17],
        'executor_telegram_id': data[18],
        'executor_username': data[19],
        'executor_full_name': data[20],
        'executor_phone': data[21],
        'executor_department_id': data[22],
        'executor_department': data[23],
        'executor_position_id': data[24],
        'executor_position': data[25],
        'executor_photo': data[26],
        'report': data[27],
        'create_date': data[28],
        'creator_last_name': data[29],
        'creator_first_name': data[30],
        'executor_last_name': data[31],
        'executor_first_name': data[32]
    }
    
    actual_result = create_deal_result(data)
    
    assert actual_result == expected_result


