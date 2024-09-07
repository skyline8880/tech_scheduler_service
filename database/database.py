import psycopg
"""
Модуль для выполнения операций над базой данных, используется psycopg.

Импортирует соединение к базе данных, запросы на удаление, вставку, выборку и обновление.
"""
from database.connection import CreateConnection
from database.query.delete import DELETE_REQUEST
from database.query.insert import (INSERT_INTO_EMPLOYEE,
                                   INSERT_INTO_EMPLOYEE_HIRE,
                                   INSERT_INTO_REQUEST)
from database.query.select import (
    SELECT_ANY_ACTIVE_REQUEST_LIST, SELECT_BITRIX_ACCOUNT_BY_DEPARTMENT_ID,
    SELECT_BITRIX_FIELD_BY_DEPARTMENT_ID, SELECT_BITRIX_STAGE_BY_DEPARTMENT_ID,
    SELECT_CREATOR_ANY_ACTIVE_REQUEST_LIST,
    SELECT_CREATOR_DEPARTMENT_ACTIVE_REQUEST_LIST,
    SELECT_CURRENT_REQUEST_OF_DEPARTMENT,
    SELECT_DEPARTMENT_ACTIVE_REQUEST_LIST,
    SELECT_DEPARTMENT_REQUESTS_BY_STATUS, SELECT_DEPERTMENT_BY_SIGN,
    SELECT_EMPLOYEE_BY_SIGN, SELECT_EXECUTOR_OWN_ACTIVE_REQUEST_LIST,
    SELECT_EXECUTORS_BY_DEPRTMENT_ID, SELECT_POSITION_BY_SIGN, SELECT_REQUESTS,
    SELECT_REQUESTS_BY_DEPARTMENT, SELECT_REQUESTS_BY_STATUS,
    SELECT_STATISTIC_OF_DEPARTMENTS, SELECT_STATUS_BY_SIGN)
from database.query.update import (UPDATE_CREATOR_IN_REQUESTS,
                                   UPDATE_EMPLOYEE_ACTIVITY,
                                   UPDATE_EMPLOYEE_DATA_BY_PHONE,
                                   UPDATE_EMPLOYEE_DATA_BY_TELEGRAM_ID,
                                   UPDATE_EXECUTOR_IN_CURRENT_REQUEST,
                                   UPDATE_EXECUTOR_IN_REQUESTS,
                                   UPDATE_PHOTO_AND_REPORT_IN_REQUEST,
                                   UPDATE_POSITION_ID_DEPARTMENT_ID_EMPLOYEE,
                                   UPDATE_REPORT_IN_CURRENT_REQUEST,
                                   UPDATE_STATUS_ID_IN_CURRENT_REQUEST)


class Database:
     """
    Класс для работы базой данных.

    Методы:
    
     - delete_request_of_department(department_id, bitrix_deal_id)
        Удаление запроса отдела по ID отдела и ID сделки в Bitrix.
    
     - insert_into_employee_auth(telegram_id, username, full_name, last_name, first_name, phone=None)
        Вставка данных сотрудника в таблицу employee_auth.
    """
     def __init__(self):
         """
        Инициализация объекта Database

        Атрибуты:
        connection: psycopg connection
            Соединение базой данных.
        cursor: psycopg cursor
            Объект курсора для выполнения запросов.
        """
         self.connection = None
         self.cursor = None

     async def delete_request_of_department(
            self, department_id, bitrix_deal_id):
        """
        Метод для удаления запроса отдела из базы данных

        Параметры:
        - department_id : int
            ID отдела.
        - bitrix_deal_id : int
            ID сделки в Bitrix.
        """
        connection = await CreateConnection()
        cursor = connection.cursor()
        await cursor.execute(
            query=DELETE_REQUEST,
            params={
                'department_id': department_id,
                'bitrix_deal_id': bitrix_deal_id})
        await connection.commit()
        await connection.close()

     async def insert_into_employee_auth(
            self,
            telegram_id,
            username,
            full_name,
            last_name,
            first_name,
            phone=None):
        """
        Метод для вставки данных сотрудника в таблицу employee_auth

        Parameters
        ----------
        telegram_id : int
            ID Telegram сотрудника.
        username : str
            Имя пользователя Telegram.
        full_name : str
            Полное имя сотрудника.
        last_name : str
            Фамилия сотрудника.
        first_name : str
            Имя сотрудника.
        phone : str, optional
            Номер телефона сотрудника.
        """
        if username is not None:
            username = f'@{username}'
        connection = await CreateConnection()
        cursor = connection.cursor()
        try:
            await cursor.execute(
                query=INSERT_INTO_EMPLOYEE,
                params={
                    'telegram_id': telegram_id,
                    'username': username,
                    'full_name': full_name,
                    'last_name': last_name,
                    'first_name': first_name,
                    'phone': phone})
        except psycopg.errors.UniqueViolation:
            await connection.rollback()
            await cursor.execute(
                query=UPDATE_EMPLOYEE_DATA_BY_PHONE,
                params={
                    'telegram_id': telegram_id,
                    'username': username,
                    'full_name': full_name,
                    'last_name': last_name,
                    'first_name': first_name,
                    'phone': phone})
            await cursor.execute(
                query=UPDATE_CREATOR_IN_REQUESTS,
                params={'creator_telegram_id': telegram_id})
            await cursor.execute(
                query=UPDATE_EXECUTOR_IN_REQUESTS,
                params={'executor_telegram_id': telegram_id})
        await connection.commit()
        await connection.close()

     async def insert_into_employee_hire(
            self, position_id, department_id, phone):
        """
        Добавляет запись по найму сотрудника в базу данных.

        Аргументы:
            position_id (int): ID должности нового сотрудника.
            department_id (int): ID отдела нового сотрудника.
            phone (str): Номер телефона нового сотрудника.

        Возвращает:
            None
        """
        connection = await CreateConnection() # соединяемся с базой
        cursor = connection.cursor()
        try: # запрос на добавление новой записи по найму сотрудника
            await cursor.execute(
                query=INSERT_INTO_EMPLOYEE_HIRE,
                params={
                    'position_id': position_id,
                    'department_id': department_id,
                    'phone': phone})
            # если возникает ошибка о нарушении уникальности, то
        except psycopg.errors.UniqueViolation:
            #откатываем транзакцию
            await connection.rollback()
            #запрос на обновление данных сотрудника
            await cursor.execute(
                query=UPDATE_POSITION_ID_DEPARTMENT_ID_EMPLOYEE,
                params={
                    'position_id': position_id,
                    'department_id': department_id,
                    'phone': phone})
        await connection.commit() #фикс изменений
        await connection.close() #закрытие соединения

     async def insert_into_request(
            self,
            bitrix_deal_id,
            department_id,
            status_id,
            creator_telegram_id,
            zone,
            break_type,
            photo,
            short_description,
            detailed_description
            ):
        """
        Вставляет новую заявку в базу данных.

        Аргументы:
            bitrix_deal_id (int): ID сделки в Bitrix.
            department_id (int): ID отдела.
            status_id (int): ID статуса заявки.
            creator_telegram_id (int): ID создателя заявки в Telegram.
            zone (str): Зона, к которой относится заявка.
            break_type (str): Тип поломки.
            photo (str): Фото, прикрепленное к заявке.
            short_description (str): Краткое описание заявки.
            detailed_description (str): Подробное описание заявки.

        Возвращает:
            None
        """
        connection = await CreateConnection() #установка соединения с базой
        cursor = connection.cursor()
        # Выполняем запрос на добавление новой заявки
        await cursor.execute(
            query=INSERT_INTO_REQUEST,
            params={
                'bitrix_deal_id': int(bitrix_deal_id),
                'department_id': int(department_id),
                'status_id': int(status_id),
                'creator_telegram_id': int(creator_telegram_id),
                'zone': zone,
                'break_type': break_type,
                'creator_photo': photo,
                'short_description': short_description,
                'detailed_description': detailed_description})
        await connection.commit() #фиксируем изменения
        await connection.close() #закрываем соединение

     async def get_department(self, department_sign):
        """
        Получает информацию про департамент по обозначению.

        Аргументы:
            department_sign (str): Обозначение департамента.

        Возвращает:
            Результат запроса к базе данных.
        """
        connection = await CreateConnection()
        cursor = connection.cursor()
        await cursor.execute(
            query=SELECT_DEPERTMENT_BY_SIGN,
            params={'department_sign': str(department_sign)})
        result = await cursor.fetchone()
        await connection.close()
        return result

     async def get_status(self, status_sign):
         """
        Получает информацию, статус по обозначению.

        Аргументы:
            status_sign (str): Обозначение статуса.

        Возвращает:
            Результат запроса к базе данных.
        """
         connection = await CreateConnection()
         cursor = connection.cursor()
         await cursor.execute(
            query=SELECT_STATUS_BY_SIGN,
            params={'status_sign': str(status_sign)})
         result = await cursor.fetchone()
         await connection.close()
         return result

     async def get_position(self, position_sign):
         """
        Получает информацию, должность по обозначению.

        Аргументы:
            position_sign (str): Обозначение должности.

        Возвращает:
            Результат запроса к базе данных.
        """
         connection = await CreateConnection()
         cursor = connection.cursor()
         await cursor.execute(
            query=SELECT_POSITION_BY_SIGN,
            params={'position_sign': str(position_sign)})
         result = await cursor.fetchone()
         await connection.close()
         return result

     async def get_bitrix_stage(self, department_id):
         """
         Асинхронный метод для получения стадии в Bitrix по идентификатору отдела.

         Параметры:
         department_id : int
         Идентификатор отдела для поиска стадии в Bitrix.

          Возвращает:
         dict
         Результат запроса - информация по стадии.

         Исключения:
         
         Exception
          при ошибке выполнения запроса
         """
         connection = await CreateConnection()
         cursor = connection.cursor()
         await cursor.execute(
            query=SELECT_BITRIX_STAGE_BY_DEPARTMENT_ID,
            params={'department_id': department_id})
         result = await cursor.fetchone()
         await connection.close()
         return result

     async def get_bitrix_field(self, department_id):
         """
         Асинхронный метод для получения поля в Bitrix по идентификатору отдела.

         Параметры:
          department_id : int
          Идентификатор отдела для поиска поля в Bitrix.

          Возвращает:
           - dict
         Результат запроса - информация по полю.

          Исключения:
          
          Exception
         при ошибке выполнения запроса
        """
         connection = await CreateConnection()
         cursor = connection.cursor()
         await cursor.execute(
            query=SELECT_BITRIX_FIELD_BY_DEPARTMENT_ID,
            params={'department_id': department_id})
         result = await cursor.fetchone()
         await connection.close()
         return result

     async def get_bitrix_account_by_department_id(self, department_id):
          """
         Асинхронный метод для получения учетной записи в Bitrix по идентификатору отдела.

         Параметры:
         
         - department_id : int
         Идентификатор отдела для поиска учетной записи в Bitrix.

         Возвращает: 
         - dict
         Результат запроса - информация учетной записи.

         Исключения:
         
         Exception
         при ошибке выполнения запроса
         """
          connection = await CreateConnection()
          cursor = connection.cursor()
          await cursor.execute(
            query=SELECT_BITRIX_ACCOUNT_BY_DEPARTMENT_ID,
            params={'department_id': department_id})
          result = await cursor.fetchone()
          await connection.close()
          return result

     async def get_employee_by_sign(self, employee_sign):
          """
         Асинхронный метод для получения информации по сотруднику по идентификатору.
         
         Параметры:
         
         - employee_sign : str
            Идентификатор сотрудника для поиска информации.
            
         Возвращает:
         
         - dict
            Результат запроса - информация по сотруднику.
            
         Исключения:
         
         Exception
            при ошибке выполнения запроса
         """
          connection = await CreateConnection()
          cursor = connection.cursor()
          await cursor.execute(
            query=SELECT_EMPLOYEE_BY_SIGN,
            params={'employee_sign': str(employee_sign)})
          result = await cursor.fetchone()
          await connection.close()
          return result

          async def get_requests(self):
             """
          Асинхронный метод для получения всех запросов.

         Возвращает:
         
         - dict
            Результат запроса - информация о запросах.

         Исключения:
          
         Exception
            при ошибке выполнения запроса
         """
          connection = await CreateConnection()
          cursor = connection.cursor()
          await cursor.execute(query=SELECT_REQUESTS)
          result = await cursor.fetchone()
          await connection.close()
          return result

     async def get_current_request_of_department(
            self, department_id, bitrix_deal_id):
            """
         Асинхронный метод для получения текущего запроса отдела по идентификатору отдела и сделки в Bitrix.

         Параметры:
          
         - department_id : int
            Идентификатор отдела для поиска текущего запроса.
         - bitrix_deal_id : int
            Идентификатор сделки в Bitrix для поиска текущего запроса.

         Возвращает:
          
         - dict
            Результат запроса - информация о текущем запросе отдела.

         Исключения:
         
         Exception
            при ошибке выполнения запроса
         """
            connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=SELECT_CURRENT_REQUEST_OF_DEPARTMENT,
            params={
                'department_id': department_id,
                'bitrix_deal_id': bitrix_deal_id})
            result = await cursor.fetchone()
            await connection.close()
            return result

            async def get_department_requests_by_status(
            self, department_id, status_id):
                """
             Асинхронный метод для получения запросов отдела по статусу.

             Параметры:
              
             - department_id : int
             Идентификатор отдела для поиска запросов.
             - status_id : int
              Идентификатор статуса для фильтрации запросов.

              Возвращает:
              
             - list
             Результат запроса - список запросов отдела по указанному статусу.

              Исключения:
              
             Exception
             при ошибке выполнения запроса
             """
                connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=SELECT_DEPARTMENT_REQUESTS_BY_STATUS,
            params={
                'department_id': department_id,
                'status_id': status_id})
            result = await cursor.fetchall()
            await connection.close()
            return result

            async def get_requests_by_status(self, status_id):
             """
             Асинхронный метод для получения запросов по статусу.

             Параметры:
              
             - status_id : int
               Идентификатор статуса для фильтрации запросов.

             Возвращает:
              
             - list
             Результат запроса - список запросов с указанным статусом.

             Исключения:
              
             Exception
              при ошибке выполнения запроса
             """
             connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=SELECT_REQUESTS_BY_STATUS,
            params={'status_id': status_id})
            result = await cursor.fetchall()
            await connection.close()
            return result

            async def get_requests_by_department(self, department_id):
             """
             Асинхронный метод для получения запросов по отделу.

             Параметры:
              
             - department_id : int
              Идентификатор отдела для поиска запросов по отделу.

             Возвращает:
              
            - list
             Результат запроса - список запросов от указанного отдела.

             Исключения:
              
             Exception
              при ошибке выполнения запроса
             """
             connection = await CreateConnection()
             cursor = connection.cursor()
             await cursor.execute(
            query=SELECT_REQUESTS_BY_DEPARTMENT,
            params={'department_id': department_id})
            result = await cursor.fetchall()
            await connection.close()
            return result

            async def get_request_list(self, position_id, department_id, is_own=None):
             """
             Получает список активных запросов в зависимости от position_id, department_id и is_own.

             Параметры:
             - position_id: int, идентификатор должности.
             - department_id: int, идентификатор отдела.
             - is_own: Optional[int], идентификатор создателя или исполнителя телеграм.

             Возвращает:
             - list: Список активных запросов в соответствии критериям.
             
             Исключения:
              
             Exception
              при ошибке выполнения запроса
             """
             connection = await CreateConnection()
             cursor = connection.cursor()
             if is_own is not None:
              if position_id == 3:
                await cursor.execute(
                    query=SELECT_CREATOR_DEPARTMENT_ACTIVE_REQUEST_LIST,
                    params={
                        'creator_telegram_id': is_own,
                        'department_id': department_id})
                result = await cursor.fetchall()
                await connection.close()
                return result
              elif position_id == 4:
                await cursor.execute(
                    query=SELECT_EXECUTOR_OWN_ACTIVE_REQUEST_LIST,
                    params={
                        'executor_telegram_id': is_own,
                        'department_id': department_id})
                result = await cursor.fetchall()
                await connection.close()
                return result
            await cursor.execute(
                query=SELECT_CREATOR_ANY_ACTIVE_REQUEST_LIST,
                params={'creator_telegram_id': is_own})
            result = await cursor.fetchall()
            await connection.close()
            return result
            if position_id in (3, 4):
             await cursor.execute(
                query=SELECT_DEPARTMENT_ACTIVE_REQUEST_LIST,
                params={'department_id': department_id})
            result = await cursor.fetchall()
            await connection.close()
            return result
            await cursor.execute(query=SELECT_ANY_ACTIVE_REQUEST_LIST)
            result = await cursor.fetchall()
            await connection.close()
            return result

            async def get_executors(self, department_id):
             """
             Получает список исполнителей по идентификатору отдела.

             Параметры:
             - department_id: int, идентификатор отдела.

             Возвращает:
             - list: Список исполнителей отдела.
         
             Исключения:
              
             Exception
              при ошибке выполнения запроса
             """   
             connection = await CreateConnection()
             cursor = connection.cursor()
             await cursor.execute(
             query=SELECT_EXECUTORS_BY_DEPRTMENT_ID,
             params={'department_id': department_id})
             result = await cursor.fetchall()
             await connection.close()
             return result

            async def get_statistic_of_departments(self, department_id=None):
             """
             Получает статистику по отделам опционально по идентификатору отдела.

             Параметры:
             - department_id: Optional[int], идентификатор отдела.

             Возвращает:
             - list: Статистика отделов в соответствии с критериями.

             Исключения:
              
             Exception: 
             при ошибке выполнения запроса
    """
             WHERE_DEPARTMENT_ID = '\nWHERE dep.id = %(department_id)s'
            params = {'department_id': department_id}
            if department_id is None:
             WHERE_DEPARTMENT_ID = ''
            params = None
            connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=(f'{SELECT_STATISTIC_OF_DEPARTMENTS}{WHERE_DEPARTMENT_ID}'),
            params=params)
            result = await cursor.fetchall()
            await connection.close()
            return result

            async def update_employee_activity(self, phone, is_active):
             """
             Обновляет активность сотрудника по номеру телефона.

             Параметры:
             - phone: str, номер телефона сотрудника.
             - is_active: bool, флаг активности сотрудника.

             Переменная:
             - bool: Флаг успешного выполнения запроса.

             Исключения:
             
             Exception: 
             при ошибке выполнения запроса
    """
             connection = await CreateConnection()
             cursor = connection.cursor()
             await cursor.execute(
            query=UPDATE_EMPLOYEE_ACTIVITY,
            params={
                'phone': phone,
                'is_active': is_active})
            await connection.commit()
            await connection.close()

            async def update_employee_by_telegram_id(self, message):
             """
             Обновляет данные сотрудника по telegram_id.
    
             Параметры:
             - message: Объект сообщения telegram.
    
               Исключения:
             Exception: 
             при ошибке выполнения запроса
             """
             telegram_id = message.from_user.id
             username = message.from_user.username
             full_name = message.from_user.full_name
             empl_data = await self.get_employee_by_sign(employee_sign=telegram_id)
             need_update = False
             if f'@{username}' != empl_data[2] or full_name != empl_data[3]:
              need_update = True
            if username is not None:
                username = f'@{username}'
            if need_update:
             connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
                query=UPDATE_EMPLOYEE_DATA_BY_TELEGRAM_ID,
                params={
                    'username': username,
                    'full_name': full_name,
                    'telegram_id': telegram_id})
            await connection.commit()
            await connection.close()

            async def update_executor_in_request(
            self,
            executor_telegram_id,
            department_id,
            bitrix_deal_id):
                 """
                 Обновляет исполнителя в текущем запросе.
    
                 Параметры:
                 - executor_telegram_id: ID исполнителя в Telegram.
                 - department_id: ID отдела.
                 - bitrix_deal_id: ID сделки в Bitrix.
    
                 Исключения:
                 Exception: 
                 при ошибке выполнения запроса
                 """
            connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=UPDATE_EXECUTOR_IN_CURRENT_REQUEST,
            params={
                'executor_telegram_id': executor_telegram_id,
                'department_id': department_id,
                'bitrix_deal_id': bitrix_deal_id})
            await connection.commit()
            await connection.close()

            async def update_photo_and_report_in_request(
            self,
            executor_photo,
            report,
            department_id,
            bitrix_deal_id):
                 """
                 Обновляет фото исполнителя и отчет в заявке.
                 
                 Параметры:

                 - executor_photo: Фото исполнителя.
                 - report: Отчет.
                 - department_id: ID отдела.
                 - bitrix_deal_id: ID сделки в Bitrix24.
                 """
            connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=UPDATE_PHOTO_AND_REPORT_IN_REQUEST,
            params={
                'executor_photo': executor_photo,
                'report': report,
                'department_id': department_id,
                'bitrix_deal_id': bitrix_deal_id})
            await connection.commit()
            await connection.close()

            async def update_status_id_in_request(
            self,
            status_id,
            department_id,
            bitrix_deal_id):
             """
             обновляет ID статуса в заявке.
 
             - status_id: ID статуса.
             - department_id: ID отдела.
             - bitrix_deal_id: ID сделки в Bitrix24.
             """
            connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=UPDATE_STATUS_ID_IN_CURRENT_REQUEST,
            params={
                'status_id': status_id,
                'department_id': department_id,
                'bitrix_deal_id': bitrix_deal_id})
            await connection.commit()
            await connection.close()

            async def update_report_in_request(
            self,
            report,
            department_id,
            bitrix_deal_id):
             """
             Асинхронно обновляет отчет в заявке.

              - report: Отчет.
              - department_id: ID отдела.
              - bitrix_deal_id: ID сделки в Bitrix24.
             """
            
            connection = await CreateConnection()
            cursor = connection.cursor()
            await cursor.execute(
            query=UPDATE_REPORT_IN_CURRENT_REQUEST,
            params={
                'report': report,
                'department_id': department_id,
                'bitrix_deal_id': bitrix_deal_id})
            await connection.commit()
            await connection.close()
