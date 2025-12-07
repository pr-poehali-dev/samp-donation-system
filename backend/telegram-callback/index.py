import json
import os
import psycopg2
import pymysql
import requests
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Обработка callback от Telegram кнопок: выдает донат рубли в БД SAMP при подтверждении
    Args: event - webhook от Telegram с callback_query
          context - контекст выполнения функции
    Returns: HTTP response с результатом операции
    '''
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body_data = json.loads(event.get('body', '{}'))
        
        if 'callback_query' not in body_data:
            return {
                'statusCode': 200,
                'body': json.dumps({'ok': True}),
                'isBase64Encoded': False
            }
        
        callback_query = body_data['callback_query']
        callback_data = callback_query['data']
        callback_id = callback_query['id']
        message_id = callback_query['message']['message_id']
        chat_id = callback_query['message']['chat']['id']
        
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        parts = callback_data.split('_')
        action = parts[0]
        donation_id = int(parts[1])
        
        db_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        if action == 'approve':
            nickname = parts[2]
            amount = int(parts[3])
            
            cursor.execute(
                "UPDATE donations SET status = %s WHERE id = %s",
                ('approved', donation_id)
            )
            conn.commit()
            
            samp_host = os.environ.get('SAMP_DB_HOST')
            samp_port = int(os.environ.get('SAMP_DB_PORT', '3306'))
            samp_user = os.environ.get('SAMP_DB_USER')
            samp_password = os.environ.get('SAMP_DB_PASSWORD')
            samp_db = os.environ.get('SAMP_DB_NAME')
            
            if all([samp_host, samp_user, samp_password, samp_db]):
                try:
                    samp_conn = pymysql.connect(
                        host=samp_host,
                        port=samp_port,
                        user=samp_user,
                        password=samp_password,
                        database=samp_db
                    )
                    samp_cursor = samp_conn.cursor()
                    
                    samp_cursor.execute(
                        "UPDATE accounts SET donate_money = donate_money + %s WHERE name = %s",
                        (amount, nickname)
                    )
                    samp_conn.commit()
                    samp_cursor.close()
                    samp_conn.close()
                    
                    new_message = f"""✅ ДОНАТ ПОДТВЕРЖДЕН!

👤 Игрок: {nickname}
💰 Начислено: {amount} донат рублей
📝 ID заявки: #{donation_id}

Донат рубли автоматически добавлены на аккаунт."""
                    
                except Exception as samp_error:
                    new_message = f"""⚠️ ОШИБКА ПОДКЛЮЧЕНИЯ К БД SAMP

👤 Игрок: {nickname}
💰 Сумма: {amount} донат рублей
❌ Ошибка: {str(samp_error)}

Проверьте настройки подключения к базе данных сервера."""
            else:
                new_message = f"""⚠️ Донат подтвержден, но БД SAMP не настроена

👤 Игрок: {nickname}
💰 Сумма: {amount} донат рублей

Добавьте данные подключения к БД сервера в настройках."""
        
        elif action == 'reject':
            cursor.execute(
                "UPDATE donations SET status = %s WHERE id = %s",
                ('rejected', donation_id)
            )
            conn.commit()
            
            new_message = f"""❌ ДОНАТ ОТКЛОНЕН

📝 ID заявки: #{donation_id}

Платеж не был получен."""
        
        cursor.close()
        conn.close()
        
        if telegram_token:
            requests.post(
                f"https://api.telegram.org/bot{telegram_token}/answerCallbackQuery",
                json={'callback_query_id': callback_id, 'text': 'Обработано!'},
                timeout=5
            )
            
            requests.post(
                f"https://api.telegram.org/bot{telegram_token}/editMessageText",
                json={
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'text': new_message
                },
                timeout=5
            )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
