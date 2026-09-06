import json
from config import MOCK_PRODUCER_DATA, MOCK_CEPEA_DATA, MOCK_B3_DATA
from engine import analyze_marketing_strategy
from database import save_analysis, get_latest_analysis_for_producer, get_all_analyses

def run_test():
    print("Iniciando teste do Motor de Recomendação AgroCogito...")
    
    # Executar a recomendação em modo de validação bypass de horário já que usamos datas fixas do mock de 2026
    result = analyze_marketing_strategy(
        MOCK_PRODUCER_DATA, 
        MOCK_CEPEA_DATA, 
        MOCK_B3_DATA, 
        bypass_time_validation=True
    )
    
    print("\n--- RESULTADO DO MOTOR DETERMINÍSTICO ---")
    print(f"Status da Análise: {result['status']}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Testar persistência no SQLite relacional
    print("\nTestando gravação relacional no SQLite...")
    save_analysis(
        analysis_id=result["analysisId"],
        producer_id=result["producerId"],
        producer_name=result["producerName"],
        generated_at=result["generatedAt"],
        status=result["status"],
        inputs_json_str=json.dumps({
            "producer": MOCK_PRODUCER_DATA,
            "cepea": MOCK_CEPEA_DATA,
            "b3": MOCK_B3_DATA
        }),
        recommendations=result["recommendations"]
    )
    print("Gravação efetuada com sucesso.")
    
    # Testar leitura do banco relacional
    print("\nTestando leitura da última análise gravada...")
    saved_analysis = get_latest_analysis_for_producer(result["producerId"])
    if saved_analysis:
        print(f"Sucesso! Análise recuperada do SQLite: {saved_analysis['analysis_id']} com {len(saved_analysis['recommendations'])} recomendações.")
        for rec in saved_analysis["recommendations"]:
            print(f" - Rec ID {rec['id']}: {rec['type']} | Mês {rec['resource_need_month']} | Qtd {rec['quantity_bags']} sacas | Receita Est. R$ {rec['estimated_revenue']:.2f}")
    else:
        print("Erro: Nenhuma análise encontrada para o produtor.")

    print("\nLista de todas as análises gravadas no banco de auditoria:")
    for row in get_all_analyses():
        print(f" - {row['analysis_id']} | Gerado em: {row['generated_at']} | Status: {row['status']}")

if __name__ == "__main__":
    run_test()
