import streamlit as st
import pandas as pd
import plotly.graph_objects as go   
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard Fitness 2026",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Arquivo de dados
DATA_FILE = "fitness_data.json"

def load_data():
    """Carrega dados do arquivo JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "meta_anual": 200,
        "atividades": {}
    }

def save_data(data):
    """Salva dados no arquivo JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_month_data(data, month):
    """Retorna dados de um mês específico."""
    month_key = f"2026-{month:02d}"
    return data["atividades"].get(month_key, {})

def add_activity(data, date_str):
    """Adiciona uma atividade para uma data."""
    month_key = date_str[:7]  # YYYY-MM
    if month_key not in data["atividades"]:
        data["atividades"][month_key] = {}
    data["atividades"][month_key][date_str] = True
    save_data(data)

def remove_activity(data, date_str):
    """Remove uma atividade para uma data."""
    month_key = date_str[:7]
    if month_key in data["atividades"] and date_str in data["atividades"][month_key]:
        del data["atividades"][month_key][date_str]
        save_data(data)

# Carregar dados
data = load_data()

# Sidebar
st.sidebar.title("⚙️ Configurações")
meta_anual = st.sidebar.number_input(
    "Meta Anual (dias)",
    min_value=1,
    max_value=365,
    value=data["meta_anual"],
    step=10
)

if meta_anual != data["meta_anual"]:
    data["meta_anual"] = meta_anual
    save_data(data)

# Título
st.title("💪 Dashboard de Acompanhamento Fitness 2026")

# Calcular métricas
total_atividades = sum(len(month) for month in data["atividades"].values())
progresso_percentual = (total_atividades / meta_anual * 100) if meta_anual > 0 else 0
dias_faltantes = max(0, meta_anual - total_atividades)

# Exibir métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Meta Anual", f"{meta_anual} dias", delta=None)

with col2:
    st.metric("Dias Realizados", f"{total_atividades} dias", delta=f"+{total_atividades}")

with col3:
    st.metric("Progresso", f"{progresso_percentual:.1f}%", delta=f"{progresso_percentual:.1f}%")

with col4:
    st.metric("Dias Faltantes", f"{dias_faltantes} dias", delta=f"-{dias_faltantes}")

st.divider()

# Gráfico de Pizza - Progresso Anual
col1, col2 = st.columns(2)

with col1:
    fig_pizza = go.Figure(data=[go.Pie(
        labels=["Realizado", "Faltante"],
        values=[total_atividades, dias_faltantes],
        marker=dict(colors=["#48BB78", "#E53E3E"]),
        textposition="inside",
        textinfo="label+percent"
    )])
    fig_pizza.update_layout(
        title="Progresso da Meta Anual",
        height=400,
        showlegend=True
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

# Gráfico de Barras - Progresso Mensal
with col2:
    months_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
                    "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    monthly_data = []
    
    for m in range(1, 13):
        month_key = f"2026-{m:02d}"
        count = len(data["atividades"].get(month_key, {}))
        monthly_data.append(count)
    
    fig_barras = go.Figure(data=[go.Bar(
        x=months_names,
        y=monthly_data,
        marker=dict(color=monthly_data, colorscale="Greens"),
        text=monthly_data,
        textposition="auto"
    )])
    fig_barras.update_layout(
        title="Atividades por Mês",
        xaxis_title="Mês",
        yaxis_title="Dias com Atividade",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_barras, use_container_width=True)

st.divider()

# Resumo Mensal
st.subheader("📊 Resumo Mensal")

months_names_full = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

resumo_data = []
for m in range(1, 13):
    month_key = f"2026-{m:02d}"
    dias_ativos = len(data["atividades"].get(month_key, {}))
    percentual = (dias_ativos / meta_anual * 100) if meta_anual > 0 else 0
    status = "✅ Ativo" if dias_ativos > 0 else "⏳ Pendente"
    
    resumo_data.append({
        "Mês": months_names_full[m-1],
        "Dias Ativos": dias_ativos,
        "% da Meta": f"{percentual:.1f}%",
        "Status": status
    })

df_resumo = pd.DataFrame(resumo_data)
st.dataframe(df_resumo, use_container_width=True, hide_index=True)

st.divider()

# Calendário Interativo
st.subheader("📅 Calendário Interativo")

selected_month = st.selectbox(
    "Selecione o mês:",
    range(1, 13),
    format_func=lambda x: months_names_full[x-1]
)

# Criar calendário com dias da semana corretos (Dom-Sab)
cal_obj = calendar.Calendar(firstweekday=6)  # 6 = Domingo
cal = cal_obj.monthdayscalendar(2026, selected_month)
month_key = f"2026-{selected_month:02d}"
month_activities = data["atividades"].get(month_key, {})

# Exibir calendário em grid
st.write(f"**{months_names_full[selected_month-1]} de 2026**")

days_header = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
cols = st.columns(7)

for i, day in enumerate(days_header):
    with cols[i]:
        st.write(f"**{day}**")

for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.write("")
            else:
                date_str = f"2026-{selected_month:02d}-{day:02d}"
                is_active = date_str in month_activities
                
                # Botão para marcar/desmarcar
                button_label = f"✅ {day}" if is_active else f"⭕ {day}"
                button_color = "green" if is_active else "gray"
                
                if st.button(button_label, key=f"day_{selected_month}_{day}", use_container_width=True):
                    if is_active:
                        remove_activity(data, date_str)
                    else:
                        add_activity(data, date_str)
                    st.rerun()

st.divider()

# Instruções
st.info("""
    ### 📋 Como Usar:
    1. **Ajuste sua meta** na barra lateral (padrão: 200 dias)
    2. **Clique nos dias** no calendário para marcar atividades realizadas
    3. **Acompanhe o progresso** nos gráficos e métricas em tempo real
    4. Os dados são salvos automaticamente
""")

# Footer
st.markdown("""
    ---
    **Dashboard Fitness 2026** | Acompanhamento de Atividades Físicas
    
    Desenvolvido por Alef Oliveira
""")
