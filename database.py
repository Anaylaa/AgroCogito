import sqlite3
import json
import os
from config import DATABASE_PATH

def get_connection():
    """Retorna uma conexão ativa com o banco SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome como dicts
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados relacional se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabela Principal de Análises (Snapshot)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        analysis_id TEXT PRIMARY KEY,
        producer_id TEXT NOT NULL,
        producer_name TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    
    # 2. Tabela de Insumos da Análise (Auditabilidade - Input + Market Data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses_inputs (
        analysis_id TEXT PRIMARY KEY,
        inputs_json TEXT NOT NULL,
        FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
    )
    """)
    
    # 3. Tabela de Recomendações Geradas (Relação 1:N)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id TEXT NOT NULL,
        type TEXT NOT NULL,                -- 'SPOT_SALE' ou 'FUTURE_HEDGE'
        resource_need_month TEXT NOT NULL, -- Mês de necessidade de caixa (ex: '2026-08')
        quantity_bags INTEGER NOT NULL,    -- Quantidade recomendada em sacas
        num_contracts INTEGER,             -- Número de contratos inteiros (para Hedge B3)
        contract_symbol TEXT,              -- Símbolo do contrato futuro usado (para Hedge B3)
        price_per_bag REAL NOT NULL,       -- Preço spot ou preço efetivo futuro utilizado
        estimated_revenue REAL NOT NULL,   -- Receita estimada (Preço * Sacas)
        reason TEXT NOT NULL,              -- Motivo/Justificativa da recomendação
        FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_analysis(analysis_id, producer_id, producer_name, generated_at, status, inputs_json_str, recommendations):
    """
    Grava de forma atômica e relacional um snapshot completo de análise e suas recomendações.
    Garante a auditabilidade histórica do MVP de acordo com a especificação técnica.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Inserir análise principal
        cursor.execute("""
        INSERT OR REPLACE INTO analyses (analysis_id, producer_id, producer_name, generated_at, status)
        VALUES (?, ?, ?, ?, ?)
        """, (analysis_id, producer_id, producer_name, generated_at, status))
        
        # Inserir JSON completo de insumos
        cursor.execute("""
        INSERT OR REPLACE INTO analyses_inputs (analysis_id, inputs_json)
        VALUES (?, ?)
        """, (analysis_id, inputs_json_str))
        
        # Limpar recomendações anteriores caso seja um REPLACE da mesma análise
        cursor.execute("DELETE FROM analyses_recommendations WHERE analysis_id = ?", (analysis_id,))
        
        # Inserir cada recomendação
        for rec in recommendations:
            num_contracts = rec.get("contracts") or rec.get("num_contracts")
            contract_symbol = rec.get("contract") or rec.get("contract_symbol")
            price_per_bag = rec.get("pricePerBag") or rec.get("effectivePricePerBag") or rec.get("price_per_bag")
            estimated_revenue = rec.get("estimatedRevenue") or rec.get("estimatedProtectedRevenue") or rec.get("estimated_revenue")
            
            cursor.execute("""
            INSERT INTO analyses_recommendations (
                analysis_id, type, resource_need_month, quantity_bags, num_contracts, contract_symbol, price_per_bag, estimated_revenue, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                rec["type"],
                rec["resourceNeedMonth"] if "resourceNeedMonth" in rec else rec["resource_need_month"],
                rec["quantityBags"] if "quantityBags" in rec else rec["quantity_bags"],
                num_contracts,
                contract_symbol,
                price_per_bag,
                estimated_revenue,
                rec["reason"]
            ))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_latest_analysis_for_producer(producer_id):
    """Busca a última análise realizada para um produtor específico."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM analyses 
    WHERE producer_id = ? 
    ORDER BY generated_at DESC LIMIT 1
    """, (producer_id,))
    
    analysis_row = cursor.fetchone()
    if not analysis_row:
        conn.close()
        return None
        
    analysis = dict(analysis_row)
    analysis_id = analysis["analysis_id"]
    
    # Buscar insumos JSON
    cursor.execute("SELECT inputs_json FROM analyses_inputs WHERE analysis_id = ?", (analysis_id,))
    input_row = cursor.fetchone()
    analysis["inputs"] = json.loads(input_row["inputs_json"]) if input_row else {}
    
    # Buscar recomendações
    cursor.execute("SELECT * FROM analyses_recommendations WHERE analysis_id = ?", (analysis_id,))
    recs = []
    for r in cursor.fetchall():
        recs.append(dict(r))
    analysis["recommendations"] = recs
    
    conn.close()
    return analysis

def get_analysis(analysis_id):
    """Busca os detalhes de uma análise específica por ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM analyses WHERE analysis_id = ?", (analysis_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    analysis = dict(row)
    
    cursor.execute("SELECT inputs_json FROM analyses_inputs WHERE analysis_id = ?", (analysis_id,))
    input_row = cursor.fetchone()
    analysis["inputs"] = json.loads(input_row["inputs_json"]) if input_row else {}
    
    cursor.execute("SELECT * FROM analyses_recommendations WHERE analysis_id = ?", (analysis_id,))
    recs = []
    for r in cursor.fetchall():
        recs.append(dict(r))
    analysis["recommendations"] = recs
    
    conn.close()
    return analysis

def get_all_analyses():
    """Retorna o histórico resumido de todas as análises ordenadas pela mais recente."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses ORDER BY generated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Inicializa o banco de dados na importação inicial
init_db()
