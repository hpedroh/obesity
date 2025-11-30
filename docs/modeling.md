# 🧠 Inteligência e Modelagem

Nesta seção, abrimos a "caixa preta" do sistema. Explicamos como o algoritmo toma decisões e qual a confiabilidade esperada.

## 1. O Desafio: Além do Binário
A obesidade não é apenas "Sim" ou "Não". É um espectro.
O modelo foi treinado para identificar **7 categorias distintas** de classificação corporal, permitindo uma triagem muito mais precisa:

* 🟢 **Peso Insuficiente**
* 🟢 **Peso Normal**
* 🟡 **Sobrepeso** (Nível I e II)
* 🔴 **Obesidade** (Tipo I, II e III)

## 2. O Algoritmo: Random Forest

O modelo escolhido foi o **Random Forest Classifier** (Floresta Aleatória) por ser um algoritmo robusto que combina múltiplas árvores de decisão.

!!! success "Por que Random Forest?"
    Diferente de modelos lineares, ele entende relações complexas (ex: *comer pouco mas ser sedentário* vs. *comer muito mas ser atleta*). Além disso, possui alta resistência a *overfitting* quando bem calibrado.

## 3. Performance Real (Dados de Teste)

É crucial ser transparente sobre a precisão. Nos testes realizados com 20% dos dados (que o modelo nunca viu antes), obtivemos:

| Métrica | Resultado | O que significa? |
| :--- | :--- | :--- |
| **Acurácia** | **94%** | De cada 100 pacientes, o sistema acerta a categoria exata de 94. |
| **F1-Score** | **0.93** | O equilíbrio entre precisão e capacidade de detecção é muito alto. |

!!! warning "Onde o modelo confunde?"
    A matriz de confusão mostra que a maior parte dos erros ocorre entre categorias vizinhas (ex: classificar *Sobrepeso I* como *Sobrepeso II*). Erros grotescos (ex: classificar *Obeso* como *Magro*) são virtualmente inexistentes.

## 4. Explicabilidade (XAI com SHAP)

Não basta acertar, é preciso explicar. Utilizamos a biblioteca **SHAP** para calcular a contribuição marginal de cada resposta.

* **Impacto Positivo (+):** Hábitos que empurram o diagnóstico para obesidade (ex: Histórico Familiar, Alta Ingestão Calórica).
* **Impacto Negativo (-):** Fatores de proteção (ex: Alto consumo de vegetais, Atividade Física).

Essa abordagem transforma a IA em uma ferramenta educativa para o paciente.