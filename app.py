import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_partial_profits(initial_capital, num_takes, takes):
    """
    Calcula el rendimiento y ganancias de tomas parciales.

    Args:
        initial_capital (float): Capital inicial.
        num_takes (int): Número de tomas de ganancias.
        takes (list): Lista de tuplas (porcentaje_cierre, rendimiento).

    Returns:
        tuple: Ganancia total, rendimiento total, reporte detallado.
    """
    remaining_position = 1.0  # Posición inicial (100%)
    total_profit = 0.0
    report = []  # Para almacenar los detalles de cada toma
    accumulated_profit = 0.0

    # Calcular las ganancias en cada toma
    for i, (pct_close, pct_gain) in enumerate(takes[:-1], 1):
        take_size = pct_close / 100
        if take_size > remaining_position:
            st.error(f"Error: El porcentaje de cierre ({pct_close}%) excede la posición restante.")
            return None, None, None

        # Calcular la ganancia de esta toma
        profit = initial_capital * remaining_position * take_size * (pct_gain / 100)
        total_profit += profit
        accumulated_profit += profit

        # Agregar al reporte
        report.append({
            "Toma": i,
            "Porcentaje Cerrado (%)": pct_close,
            "Rendimiento (%)": pct_gain,
            "Ganancia ($)": profit,
            "Ganancia Acumulada ($)": accumulated_profit,
            "Posición Restante (%)": remaining_position * 100 - pct_close
        })

        # Reducir la posición restante
        remaining_position -= take_size

    # Calcular la ganancia de la última toma
    pct_gain_last = takes[-1][1]
    profit_last = initial_capital * remaining_position * (pct_gain_last / 100)
    total_profit += profit_last
    accumulated_profit += profit_last

    # Agregar al reporte la última toma
    report.append({
        "Toma": num_takes,
        "Porcentaje Cerrado (%)": remaining_position * 100,
        "Rendimiento (%)": pct_gain_last,
        "Ganancia ($)": profit_last,
        "Ganancia Acumulada ($)": accumulated_profit,
        "Posición Restante (%)": 0.0
    })

    # Calcular el rendimiento total
    profit_percentage = (total_profit / initial_capital) * 100

    return total_profit, profit_percentage, report, remaining_position

def plot_accumulated_gains(report):
    df = pd.DataFrame(report)
    plt.figure(figsize=(8, 6))
    plt.plot(df["Toma"], df["Ganancia Acumulada ($)"], marker="o", label="Ganancia Acumulada ($)")
    plt.xlabel("Toma")
    plt.ylabel("Ganancia Acumulada ($)")
    plt.title("Ganancia Acumulada por Toma")
    plt.grid()
    plt.legend()
    st.pyplot(plt)

def calculate_final_scenarios(initial_capital, remaining_position, pct_gain_last, accumulated_profit):
    scenarios = {
        "Al Target": pct_gain_last,
        "A Tres Cuartos del Target": pct_gain_last * 0.75,
        "A la Mitad del Target": pct_gain_last * 0.5,
        "A un Cuarto del Target": pct_gain_last * 0.25,
        "A 0": 0
    }

    profits = {
        scenario: accumulated_profit + (initial_capital * remaining_position * (pct_gain / 100))
        for scenario, pct_gain in scenarios.items()
    }

    return profits

def plot_final_scenarios(profits):
    df = pd.DataFrame(list(profits.items()), columns=["Escenario", "Ganancia Total ($)"])
    plt.figure(figsize=(8, 6))
    plt.bar(df["Escenario"], df["Ganancia Total ($)"], color="skyblue")
    plt.xlabel("Escenarios")
    plt.ylabel("Ganancia Total ($)")
    plt.title("Ganancia en Escenarios de la Última Toma")
    plt.xticks(rotation=45)  # Rotar etiquetas a 45 grados
    plt.grid(axis="y")
    st.pyplot(plt)

    # Mostrar tabla de porcentajes finales
    df["Porcentaje Ganancia (%)"] = (df["Ganancia Total ($)"] / initial_capital) * 100
    st.subheader("Ganancia Final por Escenario")
    st.table(df)

# Interfaz de Streamlit
st.title("Calculadora de Tomas Parciales de Ganancias")
st.write("Esta herramienta calcula el rendimiento final y el desglose de ganancias en tomas parciales.")

# Entrada de usuario
initial_capital = st.number_input("Introduce el capital inicial ($):", min_value=0.0, value=1000.0, step=100.0)
num_takes = st.number_input("Número de tomas de ganancias:", min_value=2, value=3, step=1)

takes = []
for i in range(1, num_takes):
    pct_close = st.number_input(f"Toma {i}: Porcentaje de cierre de la posición (%):", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
    pct_gain = st.number_input(f"Toma {i}: Rendimiento alcanzado (%):", min_value=-100.0, value=10.0, step=1.0)
    takes.append((pct_close, pct_gain))

# Última toma solo requiere rendimiento
pct_gain_last = st.number_input(f"Toma {num_takes}: Rendimiento alcanzado para la última toma (%):", min_value=-100.0, value=10.0, step=1.0)
takes.append((0.0, pct_gain_last))  # 0.0 para indicar que no se solicita porcentaje de cierre

# Calcular y mostrar resultados
if st.button("Calcular"):
    total_profit, profit_percentage, report, remaining_position = calculate_partial_profits(initial_capital, num_takes, takes)

    if report:
        st.subheader("Reporte Detallado")
        for entry in report:
            st.write(f"Toma {entry['Toma']}: Cerrado {entry['Porcentaje Cerrado (%)']:.2f}%, "
                     f"Rendimiento {entry['Rendimiento (%)']:.2f}%, "
                     f"Ganancia ${entry['Ganancia ($)']:.2f}, "
                     f"Ganancia Acumulada ${entry['Ganancia Acumulada ($)']:.2f}, "
                     f"Posición Restante {entry['Posición Restante (%)']:.2f}%")

        st.subheader("Resumen")
        st.write(f"**Capital inicial:** ${initial_capital:.2f}")
        st.write(f"**Ganancia total:** ${total_profit:.2f}")
        st.write(f"**Capital final:** ${initial_capital + total_profit:.2f}")
        st.write(f"**Rendimiento total:** {profit_percentage:.2f}%")

        st.subheader("Gráfico de Ganancia Acumulada")
        plot_accumulated_gains(report)

        st.subheader("Escenarios de la Última Toma")
        accumulated_profit = report[-2]["Ganancia Acumulada ($)"]  # Ganancia acumulada antes de la última toma
        profits = calculate_final_scenarios(initial_capital, remaining_position, pct_gain_last, accumulated_profit)
        plot_final_scenarios(profits)

