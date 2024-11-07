import base64
import sys


def create_deal_json(
        title,
        assigned_by,
        category_id,
        stage_id,
        short_description,
        detailed_description,
        photo_path,
        short_description_field,
        detailed_description_field,
        photo_field):
    separator = '/'
    if sys.platform == 'win32':
        separator = '\\'
    photo_name = photo_path.split(separator)[-1]
    photo_encode = base64.b64encode(
        open(file=photo_path, mode='rb').read()).decode('utf-8')
    return {
        'fields': {
            'TITLE': title,
            'ASSIGNED_BY_ID': assigned_by,
            'CATEGORY_ID': category_id,
            'STAGE_ID': stage_id,
            f'{short_description_field}': short_description,
            f'{detailed_description_field}': detailed_description,
            f'{photo_field}': {
                'fileData': [
                    photo_name,
                    photo_encode
                ]
            },
        }
    }


def asign_deal_id_on_title(department_id, deal_id, title):
    return {
        'ID': deal_id,
        'fields': {
            'TITLE': f'{department_id}/{deal_id}: {title}',
        }
    }


def update_json(deal_id, params):
    return {
        'ID': deal_id,
        'fields': params
    }


def update_on_close_json(
        deal_id,
        stage_id,
        report,
        report_field):
    return {
        'ID': deal_id,
        'fields': {
            'STAGE_ID': stage_id,
            report_field: report,
        }
    }


def timeline_add_on_handover_json(deal_id, comment, user):
    return {
        'fields': {
            'ENTITY_ID': deal_id,
            'ENTITY_TYPE': 'deal',
            'COMMENT': f'{user}: {comment}',
        }
    }


def timeline_add_on_close_json(
        deal_id,
        photo_path,
        comment,
        user):
    separator = '/'
    if sys.platform == 'win32':
        separator = '\\'
    photo_name = photo_path.split(separator)[-1]
    photo_encode = base64.b64encode(
        open(file=photo_path, mode='rb').read()).decode('utf-8')
    return {
        'fields': {
            'ENTITY_ID': deal_id,
            'ENTITY_TYPE': 'deal',
            'COMMENT': f'{user}: {comment}',
            'FILES': {'fileData': [photo_name, photo_encode]}
        }
    }


def create_deal_result(data):
    return {
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
