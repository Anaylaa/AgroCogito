import os
from datetime import datetime

# Modo de execução: 'MOCK' ou 'REAL'
# No modo MOCK, a aplicação usa os dados mockados definidos na especificação funcional.
# No modo REAL, seriam feitas chamadas de API reais (a serem configuradas).
MARKET_DATA_MODE = os.getenv("MARKET_DATA_MODE", "MOCK")

# Caminho para o banco de dados de auditoria (SQLite)
DATABASE_PATH = os.getenv("DATABASE_PATH", "agrocogito_audit.db")

# DADOS MOCKADOS OFICIAIS (Conforme Especificação Funcional)
MOCK_PRODUCER_DATA = {
    "producerId": "PROD-001",
    "producerName": "Fazenda Horizonte",
    "commodity": "CORN",
    "referenceDate": "2026-08-17",
    "costs": {
        "coePerBag": 57.50,
        "cotPerBag": 62.00,
        "ctPerBag": 66.80,
        "financialBreakEvenPerBag": 65.40
    },
    "hedgeParameters": {
        "expectedBasisPerBag": -3.00,
        "basisRiskPerBag": 1.00,
        "b3OperationalCostPerBag": 0.20
    },
    "inventory": {
        "availableBags": 12000
    },
    "futureProduction": [
        {
            "availableFrom": "2026-09",
            "expectedBags": 9000
        },
        {
            "availableFrom": "2026-11",
            "expectedBags": 18000
        }
    ],
    "resourceNeeds": [
        {
            "month": "2026-08",
            "amount": 100000.00
        },
        {
            "month": "2026-10",
            "amount": 180000.00
        },
        {
            "month": "2026-12",
            "amount": 250000.00
        }
    ]
}

MOCK_CEPEA_DATA = {
    "commodity": "CORN",
    "source": "CEPEA",
    "price": 70.00,
    "unit": "BRL_PER_60KG_BAG",
    "referenceDate": "2026-08-14",
    "retrievedAt": "2026-08-17T11:50:00-03:00"
}

MOCK_B3_DATA = {
    "commodity": "CORN",
    "source": "B3",
    "contracts": [
        {
            "symbol": "CCMU26",
            "expirationMonth": "2026-09",
            "expirationDate": "2026-09-15",
            "price": 76.00,
            "unit": "BRL_PER_60KG_BAG",
            "quoteTimestamp": "2026-08-17T11:45:00-03:00",
            "status": "ACTIVE"
        },
        {
            "symbol": "CCMX26",
            "expirationMonth": "2026-11",
            "expirationDate": "2026-11-16",
            "price": 77.30,
            "unit": "BRL_PER_60KG_BAG",
            "quoteTimestamp": "2026-08-17T11:45:00-03:00",
            "status": "ACTIVE"
        },
        {
            "symbol": "CCMF27",
            "expirationMonth": "2027-01",
            "expirationDate": "2027-01-15",
            "price": 75.50,
            "unit": "BRL_PER_60KG_BAG",
            "quoteTimestamp": "2026-08-17T11:45:00-03:00",
            "status": "ACTIVE"
        }
    ]
}
