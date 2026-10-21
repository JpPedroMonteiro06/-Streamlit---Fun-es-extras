# Dashboard de Vendas - Concessionária

Atividade de Python: dashboard de vendas de carros feito com Streamlit.

## Funcionalidades

- Escolha do modelo, cor e quantidade em um `st.form`
- Pedido guardado no `st.session_state`
- Pagamento à vista (5% de desconto e cálculo de troco) ou financiado (entrada mínima de 20% e parcelas)
- Mensagens com `st.success`, `st.info`, `st.warning` e `st.error`
- `st.rerun()` para limpar o pedido e finalizar a venda
- Resumo das vendas com faturamento, carros vendidos e gráficos por marca e categoria

## Como rodar

```
pip install -r requirements.txt
streamlit run app.py
```
