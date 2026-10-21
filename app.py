import streamlit as st
import pandas as pd

st.set_page_config(page_title="Concessionária - Vendas", layout="wide")


# Catálogo de carros disponíveis na loja
CATALOGO = {
    "Fiat Mobi Like": {"marca": "Fiat", "categoria": "Hatch", "ano": 2025, "preco": 74990.00},
    "Fiat Strada Volcano": {"marca": "Fiat", "categoria": "Picape", "ano": 2025, "preco": 129990.00},
    "Chevrolet Onix LT": {"marca": "Chevrolet", "categoria": "Hatch", "ano": 2025, "preco": 98590.00},
    "Chevrolet Tracker Premier": {"marca": "Chevrolet", "categoria": "SUV", "ano": 2025, "preco": 164990.00},
    "Volkswagen Polo Highline": {"marca": "Volkswagen", "categoria": "Hatch", "ano": 2025, "preco": 119990.00},
    "Volkswagen T-Cross Comfortline": {"marca": "Volkswagen", "categoria": "SUV", "ano": 2025, "preco": 156990.00},
    "Hyundai HB20 Comfort": {"marca": "Hyundai", "categoria": "Hatch", "ano": 2025, "preco": 94290.00},
    "Toyota Corolla XEi": {"marca": "Toyota", "categoria": "Sedã", "ano": 2025, "preco": 172990.00},
    "Jeep Compass Longitude": {"marca": "Jeep", "categoria": "SUV", "ano": 2025, "preco": 199990.00},
}

DESCONTO_A_VISTA = 0.05   # 5% de desconto no pagamento à vista
ENTRADA_MINIMA = 0.20     # financiamento exige pelo menos 20% de entrada
JUROS_MENSAL = 0.0149     # 1,49% ao mês


def formatar_reais(valor):
    # deixa o número no formato brasileiro: R$ 1.234,56
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


# session_state guarda os dados entre os reruns da página
if "pedido" not in st.session_state:
    st.session_state.pedido = []

if "vendas" not in st.session_state:
    st.session_state.vendas = []

if "mensagem" not in st.session_state:
    st.session_state.mensagem = ""


# -----------------------------------------------------------------------------

st.title("Dashboard de Vendas - Concessionária")
st.markdown("---")

# mensagem que sobrevive ao st.rerun() depois de finalizar uma venda
if st.session_state.mensagem:
    st.success(st.session_state.mensagem)
    st.session_state.mensagem = ""

col1, col2 = st.columns([1, 1], gap="large")


with col1:
    st.subheader("Escolha do Veículo")

    with st.form("form_carro", clear_on_submit=False):
        modelo = st.selectbox("Modelo", list(CATALOGO.keys()))
        carro = CATALOGO[modelo]
        st.caption(
            f"Marca: **{carro['marca']}** | Categoria: **{carro['categoria']}** | "
            f"Ano: **{carro['ano']}** | Preço: **{formatar_reais(carro['preco'])}**"
        )

        cor = st.selectbox("Cor", ["Branco", "Preto", "Prata", "Cinza", "Vermelho", "Azul"])
        quantidade = st.number_input("Quantidade", min_value=1, max_value=10, value=1, step=1)

        btn_adicionar = st.form_submit_button("Adicionar ao Pedido", use_container_width=True)

        if btn_adicionar:
            subtotal = carro["preco"] * quantidade
            st.session_state.pedido.append({
                "Modelo": modelo,
                "Marca": carro["marca"],
                "Categoria": carro["categoria"],
                "Cor": cor,
                "Preço Unit. (R$)": carro["preco"],
                "Qtd": quantidade,
                "Subtotal (R$)": subtotal,
            })
            st.success(f"**{modelo}** ({cor}) adicionado ao pedido!")

    st.subheader("Pedido Atual")
    if st.session_state.pedido:
        df_pedido = pd.DataFrame(st.session_state.pedido)

        st.dataframe(
            df_pedido,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Preço Unit. (R$)": st.column_config.NumberColumn("Preço Unit.", format="R$ %.2f"),
                "Subtotal (R$)": st.column_config.NumberColumn("Subtotal", format="R$ %.2f"),
            },
        )

        if st.button("Limpar Pedido", use_container_width=True):
            st.session_state.pedido = []
            st.rerun()
    else:
        st.info("Nenhum veículo no pedido. Escolha um modelo acima.")


with col2:
    st.subheader("Pagamento")

    total_pedido = sum(item["Subtotal (R$)"] for item in st.session_state.pedido)
    st.metric(label="VALOR DO PEDIDO", value=formatar_reais(total_pedido))

    st.markdown("---")

    if total_pedido == 0:
        st.warning("Adicione pelo menos um veículo ao pedido antes de escolher o pagamento.")
    else:
        cliente = st.text_input("Nome do Cliente")
        forma = st.radio("Forma de Pagamento", ["À vista", "Financiamento"], horizontal=True)

        pode_finalizar = False

        if forma == "À vista":
            desconto = total_pedido * DESCONTO_A_VISTA
            total_final = total_pedido - desconto

            c1, c2 = st.columns(2)
            c1.metric("Desconto (5%)", formatar_reais(desconto))
            c2.metric("Total à Vista", formatar_reais(total_final))

            valor_pago = st.number_input(
                "Valor Pago pelo Cliente (R$)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                format="%.2f",
            )

            if valor_pago == 0:
                st.info("Aguardando o pagamento...")
            elif valor_pago < total_final:
                falta = total_final - valor_pago
                st.error(f"**Valor insuficiente!** Faltam **{formatar_reais(falta)}**.")
            else:
                troco = valor_pago - total_final
                st.success("**Pagamento aprovado!**")
                if troco > 0:
                    st.metric("Troco a Devolver", formatar_reais(troco))
                parcelas = 1
                valor_parcela = total_final
                pode_finalizar = True

        else:
            entrada_minima = total_pedido * ENTRADA_MINIMA
            st.caption(f"Entrada mínima de 20%: **{formatar_reais(entrada_minima)}**")

            entrada = st.number_input(
                "Valor da Entrada (R$)",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                format="%.2f",
            )
            parcelas = st.select_slider("Número de Parcelas", options=[12, 24, 36, 48, 60], value=36)

            if entrada < entrada_minima:
                st.error(f"**Entrada muito baixa!** O mínimo é **{formatar_reais(entrada_minima)}**.")
            elif entrada >= total_pedido:
                st.warning("A entrada cobre o valor todo. Escolha o pagamento à vista para ganhar desconto.")
            else:
                valor_financiado = total_pedido - entrada
                # fórmula de parcela fixa (tabela Price)
                fator = (1 + JUROS_MENSAL) ** parcelas
                valor_parcela = valor_financiado * (JUROS_MENSAL * fator) / (fator - 1)
                total_final = entrada + valor_parcela * parcelas

                c1, c2 = st.columns(2)
                c1.metric("Valor Financiado", formatar_reais(valor_financiado))
                c2.metric(f"Parcela ({parcelas}x)", formatar_reais(valor_parcela))
                st.info(f"Juros de 1,49% ao mês. Total pago no final: **{formatar_reais(total_final)}**")
                pode_finalizar = True

        if pode_finalizar:
            with st.expander("Ver Resumo da Venda"):
                st.write(f"**Cliente:** {cliente if cliente else 'Não informado'}")
                st.write(f"**Veículos:** {sum(item['Qtd'] for item in st.session_state.pedido)}")
                st.write(f"**Forma de Pagamento:** {forma}")
                st.write(f"**Total:** {formatar_reais(total_final)}")

            if st.button("Finalizar Venda", type="primary", use_container_width=True):
                if not cliente:
                    st.error("Informe o nome do cliente para finalizar a venda.")
                else:
                    for item in st.session_state.pedido:
                        valor_item = item["Subtotal (R$)"]
                        if forma == "À vista":
                            valor_item = valor_item * (1 - DESCONTO_A_VISTA)

                        st.session_state.vendas.append({
                            "Cliente": cliente,
                            "Modelo": item["Modelo"],
                            "Marca": item["Marca"],
                            "Categoria": item["Categoria"],
                            "Qtd": item["Qtd"],
                            "Pagamento": forma,
                            "Valor (R$)": valor_item,
                        })
                    st.session_state.pedido = []
                    st.session_state.mensagem = f"Venda para {cliente} finalizada com sucesso!"
                    st.rerun()


# -----------------------------------------------------------------------------
# Painel com o resumo de todas as vendas feitas na sessão

st.markdown("---")
st.subheader("Resumo das Vendas")

if st.session_state.vendas:
    df_vendas = pd.DataFrame(st.session_state.vendas)

    m1, m2, m3 = st.columns(3)
    m1.metric("Faturamento", formatar_reais(df_vendas["Valor (R$)"].sum()))
    m2.metric("Carros Vendidos", int(df_vendas["Qtd"].sum()))
    m3.metric("Clientes Atendidos", df_vendas["Cliente"].nunique())

    g1, g2 = st.columns(2)
    with g1:
        st.write("**Faturamento por Marca**")
        por_marca = df_vendas.groupby("Marca")["Valor (R$)"].sum()
        st.bar_chart(por_marca)
    with g2:
        st.write("**Carros Vendidos por Categoria**")
        por_categoria = df_vendas.groupby("Categoria")["Qtd"].sum()
        st.bar_chart(por_categoria)

    st.dataframe(
        df_vendas,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Valor (R$)": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
        },
    )

    if st.button("Zerar Histórico de Vendas"):
        st.session_state.vendas = []
        st.rerun()
else:
    st.info("Nenhuma venda finalizada ainda.")
