import json
import os
import psycopg2
import pymysql
import requests
from typing import Dict, Any
from datetime import datetime

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Обработка платежей: сохраняет данные в БД и отправляет уведомление в Telegram с кнопками
    Args: event - данные HTTP запроса с nickname и amount
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
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body_data = json.loads(event.get('body', '{}'))
        nickname = body_data.get('nickname', '').strip()
        amount = body_data.get('amount')
        
        if not nickname or not amount:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Nickname and amount are required'}),
                'isBase64Encoded': False
            }
        
        amount = int(amount)
        if amount <= 0:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Amount must be positive'}),
                'isBase64Encoded': False
            }
        
        db_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO donations (nickname, amount, status) VALUES (%s, %s, %s) RETURNING id",
            (nickname, amount, 'pending')
        )
        donation_id = cursor.fetchone()[0]
        conn.commit()
        
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = '7569853207'
        
        message = f"""🎮 Новый донат SAMP!

👤 Игрок: {nickname}
💰 Сумма: {amount} донат рублей
💳 Карта: 2200 7020 5523 2552
📝 ID заявки: #{donation_id}
⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Ожидает подтверждения оплаты."""
        
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "✅ Оплатил",
                        "callback_data": f"approve_{donation_id}_{nickname}_{amount}"
                    },
                    {
                        "text": "❌ Не оплатил",
                        "callback_data": f"reject_{donation_id}"
                    }
                ]
            ]
        }
        
        telegram_sent = False
        if telegram_token:
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            telegram_response = requests.post(telegram_url, json={
                'chat_id': telegram_chat_id,
                'text': message,
                'reply_markup': keyboard
            }, timeout=10)
            
            if telegram_response.status_code == 200:
                telegram_sent = True
                cursor.execute(
                    "UPDATE donations SET telegram_sent = TRUE WHERE id = %s",
                    (donation_id,)
                )
                conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'donation_id': donation_id,
                'telegram_sent': telegram_sent,
                'message': 'Заявка создана и отправлена администратору'
            }),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
