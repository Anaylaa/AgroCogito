import math
from datetime import datetime, timezone, timedelta
import json

def parse_iso_datetime(dt_str):
    """
    Analisa strings de data e hora ISO (com suporte a fusos horários como -03:00) 
    e retorna um objeto datetime consciente de timezone (timezone-aware).
    """
    # Remove dois pontos do fuso horário se necessário para versões antigas do Python (ex: -03:00 -> -0300)
    # Mas no Python 3.7+, datetime.fromisoformat lida muito bem com isso.
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        # Fallback manual em caso de falha de parser em ambientes exóticos
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str)

def validate_quote_timestamp(quote_timestamp_str, reference_time_str):
    """
    Valida se a cotação da B3 tem no máximo 60 minutos em relação ao horário da análise (12:00).
    Retorna (valido, diferenca_minutos).
    """
    try:
        quote_time = parse_iso_datetime(quote_timestamp_str)
        ref_time = parse_iso_datetime(reference_time_str)
        
        diff = ref_time - quote_time
        diff_minutes = diff.total_seconds() / 60.0
        
        # A cotação deve ser anterior ou igual ao horário de referência e ter diferença <= 60 minutos
        is_valid = 0 <= diff_minutes <= 60.0
        return is_valid, diff_minutes
    except Exception as e:
        return False, 0.0

def analyze_marketing_strategy(producer_data, cepea_data, b3_data, bypass_time_validation=False):
    """
    Motor de Recomendação Determinístico do AgroCogito.
    Retorna uma estrutura de dicionário contendo os resultados e recomendações,
    ou sinaliza erros de validação com status apropriados.
    """
    # 1. VALIDAÇÃO DE DADOS DO PRODUTOR (Regras de Negócio e consistência)
    costs = producer_data.get("costs", {})
    coe = costs.get("coePerBag")
    cot = costs.get("cotPerBag")
    ct = costs.get("ctPerBag")
    break_even = costs.get("financialBreakEvenPerBag")
    
    inventory_data = producer_data.get("inventory", {})
    available_inventory = inventory_data.get("availableBags")
    
    hedge_params = producer_data.get("hedgeParameters", {})
    expected_basis = hedge_params.get("expectedBasisPerBag")
    basis_risk = hedge_params.get("basisRiskPerBag")
    b3_op_cost = hedge_params.get("b3OperationalCostPerBag")
    
    future_production = producer_data.get("futureProduction", [])
    resource_needs = producer_data.get("resourceNeeds", [])
    
    # Lista de mensagens para registrar erros explícitos de validação
    validation_errors = []
    
    # Validação de custos obrigatórios
    if ct is None or ct <= 0:
        validation_errors.append("Custo Total (CT) inexistente, zero ou negativo.")
    if coe is None or coe <= 0:
        validation_errors.append("Custo Operacional Efetivo (COE) inexistente, zero ou negativo.")
    if cot is None or cot <= 0:
        validation_errors.append("Custo Operacional Total (COT) inexistente, zero ou negativo.")
        
    # Validação de estoque e parâmetros de mercado
    if available_inventory is None or available_inventory < 0:
        validation_errors.append("Quantidade de estoque negativa ou ausente.")
    if expected_basis is None:
        validation_errors.append("Parâmetro de base esperada ausente.")
    if basis_risk is None or basis_risk < 0:
        validation_errors.append("Risco de base ausente ou negativo.")
    if b3_op_cost is None or b3_op_cost < 0:
        validation_errors.append("Custo operacional do hedge ausente ou negativo.")
        
    # Validação de produções futuras
    for i, prod in enumerate(future_production):
        month = prod.get("availableFrom")
        bags = prod.get("expectedBags")
        if not month:
            validation_errors.append(f"Mês de disponibilidade ausente no item {i} de produção futura.")
        if bags is None or bags < 0:
            validation_errors.append(f"Quantidade de produção futura negativa no mês {month or i}.")
            
    # Validação de necessidades financeiras
    for i, need in enumerate(resource_needs):
        month = need.get("month")
        amount = need.get("amount")
        if not month:
            validation_errors.append(f"Mês ausente no item {i} de necessidade de recursos.")
        if amount is None or amount < 0:
            validation_errors.append(f"Necessidade financeira negativa no mês {month or i}.")

    if validation_errors:
        return {
            "status": "INVALID_PRODUCER_DATA",
            "errors": validation_errors,
            "disclaimer": "Os dados de entrada do produtor contêm erros ou inconsistências. A análise foi interrompida."
        }

    # 2. VALIDAÇÃO DOS DADOS DE MERCADO (CEPEA e B3)
    spot_price = cepea_data.get("price")
    if spot_price is None or spot_price <= 0:
        return {
            "status": "MARKET_DATA_UNAVAILABLE",
            "errors": ["Preço físico CEPEA de referência indisponível, zero ou negativo."],
            "disclaimer": "Dados de mercado físico (CEPEA) indisponíveis ou incorretos. A análise não pôde ser iniciada."
        }
        
    # Definir horário de execução da análise
    # Conforme especificação, a análise oficial é realizada às 12:00 do dia de referência do produtor.
    ref_date_str = producer_data.get("referenceDate", "2026-08-17")
    analysis_time_str = f"{ref_date_str}T12:00:00-03:00"
    
    # Processar cotações dos contratos B3 e filtrar elegíveis pelo tempo de atualização
    contracts_raw = b3_data.get("contracts", [])
    valid_b3_contracts = []
    outdated_b3_contracts = []
    
    for c in contracts_raw:
        symbol = c.get("symbol")
        price = c.get("price")
        quote_ts = c.get("quoteTimestamp")
        status_c = c.get("status")
        
        if not symbol or price is None or price <= 0 or not quote_ts:
            continue
            
        if status_c != "ACTIVE":
            continue
            
        # Validar idade da cotação
        if bypass_time_validation:
            is_valid_time = True
            diff_min = 0.0
        else:
            is_valid_time, diff_min = validate_quote_timestamp(quote_ts, analysis_time_str)
            
        if is_valid_time:
            valid_b3_contracts.append(c)
        else:
            outdated_b3_contracts.append({
                "symbol": symbol,
                "ageMinutes": diff_min,
                "quoteTimestamp": quote_ts
            })

    # Regra de negócio: Se TODAS as cotações B3 estiverem desatualizadas, o mercado futuro está indisponível
    if not valid_b3_contracts and contracts_raw:
        # Mas ainda podemos tentar fazer análise spot parcial se CEPEA estiver disponível
        # Vamos retornar o status MARKET_DATA_UNAVAILABLE se o usuário necessitar exclusivamente de futuros,
        # ou estruturar o aviso de mercado futuro desatualizado.
        pass

    # 3. CÁLCULO DAS MARGENS DO MERCADO SPOT
    spot_margins = {
        "overCoe": round(spot_price - coe, 2),
        "overCot": round(spot_price - cot, 2),
        "overCt": round(spot_price - ct, 2)
    }
    
    # 4. CÁLCULO DE CADA CONTRATO FUTURO E MARGENS
    futures_analysis = []
    for c in valid_b3_contracts:
        symbol = c["symbol"]
        market_price = c["price"]
        exp_month = c["expirationMonth"]
        
        # Preço Efetivo Futuro = Preço B3 + Base Esperada - Custo Operacional
        effective_price = round(market_price + expected_basis - b3_op_cost, 2)
        
        # Margens
        margins = {
            "overCoe": round(effective_price - coe, 2),
            "overCot": round(effective_price - cot, 2),
            "overCt": round(effective_price - ct, 2)
        }
        
        # Cenários de Risco de Base (Inferior, Central, Superior)
        lower_price = round(market_price + expected_basis - basis_risk - b3_op_cost, 2)
        central_price = effective_price
        upper_price = round(market_price + expected_basis + basis_risk - b3_op_cost, 2)
        
        futures_analysis.append({
            "symbol": symbol,
            "marketPrice": market_price,
            "effectivePrice": effective_price,
            "expirationMonth": exp_month,
            "margins": margins,
            "basisScenario": {
                "lower": lower_price,
                "central": central_price,
                "upper": upper_price
            }
        })
        
    # Selecionar o melhor contrato baseado no critério de maior Margem CT
    best_future = None
    if futures_analysis:
        best_future_item = max(futures_analysis, key=lambda x: x["margins"]["overCt"])
        best_future = {
            "symbol": best_future_item["symbol"],
            "effectivePrice": best_future_item["effectivePrice"],
            "marginOverCt": best_future_item["margins"]["overCt"],
            "expirationMonth": best_future_item["expirationMonth"]
        }

    # 5. ALOCAÇÃO CRONOLÓGICA DAS NECESSIDADES FINANCEIRAS DE CAIXA
    recommendations = []
    
    # Controladores de saldo (para evitar alocação dupla)
    remaining_inventory = available_inventory
    
    # Produção futura indexada por mês de disponibilidade
    prod_pool = {}
    for prod in future_production:
        month = prod["availableFrom"]
        prod_pool[month] = prod["expectedBags"]
        
    # Ordenar as necessidades de caixa cronologicamente (ex: '2026-08', '2026-10', '2026-12')
    sorted_needs = sorted(resource_needs, key=lambda x: x["month"])
    
    # Controlar se alguma necessidade futura não pôde ser coberta integralmente
    partially_covered = False
    fully_covered_all = True

    for need in sorted_needs:
        need_month = need["month"]
        amount = need["amount"]
        
        if amount == 0:
            continue
            
        # Verificar se é uma necessidade imediata (mês da análise ou anterior)
        # Exemplo: data de referência é 2026-08-17, então 2026-08 é imediata
        is_immediate = need_month <= ref_date_str[:7]
        
        if is_immediate:
            # Caso Spot: Atender necessidade financeira imediata usando estoque físico atual
            if remaining_inventory > 0:
                # Fórmula: Sacas Necessárias = ceil(Necessidade / Preço Spot Efetivo)
                required_bags = math.ceil(amount / spot_price)
                
                # Verificar se o estoque é suficiente
                if required_bags <= remaining_inventory:
                    # Cobertura completa via spot
                    revenue = round(required_bags * spot_price, 2)
                    recommendations.append({
                        "type": "SPOT_SALE",
                        "resourceNeedMonth": need_month,
                        "quantityBags": required_bags,
                        "pricePerBag": spot_price,
                        "estimatedRevenue": revenue,
                        "reason": f"Atender integralmente à necessidade de caixa de {need_month} através da venda no Spot."
                    })
                    remaining_inventory -= required_bags
                else:
                    # Cobertura parcial via spot (vende tudo que tem)
                    revenue = round(remaining_inventory * spot_price, 2)
                    recommendations.append({
                        "type": "SPOT_SALE",
                        "resourceNeedMonth": need_month,
                        "quantityBags": remaining_inventory,
                        "pricePerBag": spot_price,
                        "estimatedRevenue": revenue,
                        "reason": f"Atender parcialmente à necessidade de caixa de {need_month} (Estoque físico esgotado)."
                    })
                    remaining_inventory = 0
                    fully_covered_all = False
            else:
                fully_covered_all = False
                
        else:
            # Caso Futuro/Hedge: Atender necessidade futura usando produção futura planejada
            # 1. Identificar produções disponíveis ANTES ou NO MÊS da necessidade
            eligible_production_bags = 0
            eligible_months = []
            for m, qty in prod_pool.items():
                if m <= need_month:
                    eligible_production_bags += qty
                    eligible_months.append(m)
                    
            # 2. Filtrar contratos B3 elegíveis (vencimento >= mês de disponibilidade do produto)
            # Para simplificar, o contrato elegível deve vencer no mês da necessidade ou após o mês em que o milho está disponível
            if not valid_b3_contracts:
                # Se não há cotações futuras válidas de mercado, não podemos emitir recomendação futura
                fully_covered_all = False
                partially_covered = True
                continue
                
            # Identificar o melhor contrato elegível especificamente para as produções elegíveis encontradas
            # Filtro de elegibilidade: vencimento do contrato >= mês de disponibilidade do produto
            contract_candidates = []
            for item in futures_analysis:
                # Se pelo menos uma das produções elegíveis for anterior ou igual ao vencimento do contrato
                if any(m <= item["expirationMonth"] for m in eligible_months):
                    contract_candidates.append(item)
                    
            if not contract_candidates:
                # Sem contrato elegível
                fully_covered_all = False
                continue
                
            # Selecionar o melhor entre os elegíveis
            best_eligible_contract = max(contract_candidates, key=lambda x: x["margins"]["overCt"])
            eff_price = best_eligible_contract["effectivePrice"]
            contract_symbol = best_eligible_contract["symbol"]
            margin_ct = best_eligible_contract["margins"]["overCt"]
            
            # 3. Calcular quantidade necessária de sacas para cobrir a necessidade
            bags_needed = math.ceil(amount / eff_price)
            
            # Converter para contratos cheios de 450 sacas via CEIL
            contracts_needed = math.ceil(bags_needed / 450)
            bags_protected = contracts_needed * 450
            
            # Verificar se a quantidade de sacas protegidas é suportada pela produção futura disponível
            # Procurar abater sequencialmente das produções mais antigas no pool
            if bags_protected <= eligible_production_bags:
                # Sucesso: cabe na produção futura disponível
                revenue = round(bags_protected * eff_price, 2)
                recommendations.append({
                    "type": "FUTURE_HEDGE",
                    "resourceNeedMonth": need_month,
                    "contract": contract_symbol,
                    "contracts": contracts_needed,
                    "quantityBags": bags_protected,
                    "effectivePricePerBag": eff_price,
                    "estimatedProtectedRevenue": revenue,
                    "marginOverCtPerBag": margin_ct,
                    "reason": f"Proteger caixa de {need_month} via Hedge na B3 ({contract_symbol}) garantindo margem econômica CT de R$ {margin_ct:.2f}/sc."
                })
                
                # Abater a quantidade protegida sequencialmente das produções futuras elegíveis no pool
                temp_bags = bags_protected
                for m in sorted(eligible_months):
                    if prod_pool[m] >= temp_bags:
                        prod_pool[m] -= temp_bags
                        temp_bags = 0
                        break
                    else:
                        temp_bags -= prod_pool[m]
                        prod_pool[m] = 0
            else:
                # Cobertura parcial: Calcula o número máximo de contratos inteiros cabíveis via FLOOR
                max_contracts = math.floor(eligible_production_bags / 450)
                if max_contracts > 0:
                    bags_protected = max_contracts * 450
                    revenue = round(bags_protected * eff_price, 2)
                    recommendations.append({
                        "type": "FUTURE_HEDGE",
                        "resourceNeedMonth": need_month,
                        "contract": contract_symbol,
                        "contracts": max_contracts,
                        "quantityBags": bags_protected,
                        "effectivePricePerBag": eff_price,
                        "estimatedProtectedRevenue": revenue,
                        "marginOverCtPerBag": margin_ct,
                        "reason": f"Proteger parcialmente caixa de {need_month} devido ao limite de produção futura disponível."
                    })
                    
                    # Consumir todo o estoque elegível correspondente
                    temp_bags = bags_protected
                    for m in sorted(eligible_months):
                        if prod_pool[m] >= temp_bags:
                            prod_pool[m] -= temp_bags
                            temp_bags = 0
                            break
                        else:
                            temp_bags -= prod_pool[m]
                            prod_pool[m] = 0
                    fully_covered_all = False
                else:
                    fully_covered_all = False

    # 6. DEFINIÇÃO DO STATUS GERAL DA ANÁLISE
    # OPPORTUNITY: Há pelo menos uma recomendação economicamente atrativa (margem CT > 0) ou alocada para caixa.
    # WAIT: Não existe necessidade financeira imediata obrigatória e todas as alternativas têm margem CT <= 0.
    # PARTIAL: Parte das necessidades pode ser atendida, mas não todas. Or mercado futuro inválido.
    # MARKET_DATA_UNAVAILABLE: Se dados de mercado estiverem inválidos.
    
    # Determinar se temos alguma recomendação positiva
    has_recommendation = len(recommendations) > 0
    
    if not has_recommendation:
        # Se não há necessidades urgentes de caixa e todas as margens CT dos contratos e spot são negativas
        all_neg_margin = spot_margins["overCt"] <= 0 and all(x["margins"]["overCt"] <= 0 for x in futures_analysis)
        if all_neg_margin:
            status = "WAIT"
        else:
            status = "OPPORTUNITY"
    else:
        if fully_covered_all:
            status = "OPPORTUNITY"
        else:
            status = "PARTIAL"
            
    # Se todas as cotações da B3 expiraram/estão desatualizadas, definimos uma mensagem de erro ou status parcial
    market_warnings = []
    if outdated_b3_contracts and not valid_b3_contracts:
        market_warnings.append(
            "As cotações disponíveis para o mercado futuro excedem o limite máximo de uma hora definido para esta análise. "
            "Por segurança, nenhuma recomendação baseada em contratos futuros foi emitida."
        )
        if status in ["OPPORTUNITY", "PARTIAL"] and any(r["type"] == "FUTURE_HEDGE" for r in recommendations):
            # Se havia recomendações futuras mas as cotações expiraram, remove futuras e muda status
            recommendations = [r for r in recommendations if r["type"] == "SPOT_SALE"]
            status = "PARTIAL" if recommendations else "MARKET_DATA_UNAVAILABLE"

    disclaimer = (
        "Esta análise possui caráter exclusivamente informativo e constitui uma ferramenta de apoio à decisão. "
        "Os valores utilizados correspondem às informações disponíveis no momento da análise e podem sofrer alterações. "
        "As projeções e recomendações não representam garantia de preço, rentabilidade ou resultado. "
        "A decisão final de comercialização é de responsabilidade do produtor."
    )

    # 7. MONTAGEM DA SAÍDA E MEMÓRIA DE CÁLCULO COMPLETA
    analysis_id = f"AN-{ref_date_str.replace('-', '')}-{producer_data['producerId']}"
    
    return {
        "analysisId": analysis_id,
        "producerId": producer_data["producerId"],
        "producerName": producer_data["producerName"],
        "commodity": producer_data["commodity"],
        "generatedAt": f"{ref_date_str}T12:00:00-03:00",
        "status": status,
        "costs": {
            "coePerBag": coe,
            "cotPerBag": cot,
            "ctPerBag": ct,
            "financialBreakEvenPerBag": break_even
        },
        "spot": {
            "source": "CEPEA",
            "referenceDate": cepea_data.get("referenceDate"),
            "price": spot_price,
            "margins": spot_margins
        },
        "futures": futures_analysis,
        "bestFutureContract": best_future,
        "recommendations": recommendations,
        "warnings": market_warnings,
        "disclaimer": disclaimer
    }
