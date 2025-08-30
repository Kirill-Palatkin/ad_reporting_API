import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path("app.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            channel TEXT,
            campaign_id TEXT,
            impressions INTEGER,
            clicks INTEGER,
            cost REAL
        )
    ''')
    conn.commit()
    conn.close()


def insert_event(event: dict):
    return insert_events([event])


def insert_events(events: List[Dict[str, Any]]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for e in events:
        cursor.execute('''
            INSERT INTO events (date, channel, campaign_id, impressions, clicks, cost)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (e['date'], e['channel'], e['campaign_id'], e['impressions'], e['clicks'], e['cost']))
    conn.commit()
    conn.close()


def query_events(campaign_id: str = None, date_from: str = None, date_to: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT date, channel, campaign_id, impressions, clicks, cost FROM events WHERE 1=1"
    params = []
    if campaign_id:
        query += " AND campaign_id = ?"
        params.append(campaign_id)
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(['date','channel','campaign_id','impressions','clicks','cost'], row)) for row in rows]


def query_aggregated(channel: str = None, campaign_id: str = None, date_from: str = None, date_to: str = None):
    """
    Возвращает список словарей с агрегатами по каналам и/или кампаниям.
    Если указан только channel — аггрегируем по каналам.
    Если указан только campaign_id — по кампаниям.
    Если оба — по паре (channel, campaign_id)
    """
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()

    query = "SELECT channel, campaign_id, SUM(impressions), SUM(clicks), SUM(cost) FROM events WHERE 1=1"
    params = []

    if channel:
        query += " AND channel=?"
        params.append(channel)
    if campaign_id:
        query += " AND campaign_id=?"
        params.append(campaign_id)
    if date_from:
        query += " AND date>=?"
        params.append(date_from)
    if date_to:
        query += " AND date<=?"
        params.append(date_to)

    query += " GROUP BY channel, campaign_id"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "channel": row[0],
            "campaign_id": row[1],
            "impressions": row[2],
            "clicks": row[3],
            "cost": row[4],
        })
    return result

