import pandas as pd
import seaborn as sbn
import matplotlib.pyplot as plt

def calcular_volumenes(df):
    """
    Calculates the monthly volume (m³) per hectare of infiltration and runoff
    based on daily values in millimeters.

    Parameters:
        df (DataFrame): A pandas DataFrame containing daily data with the following columns:
            - 'YEAR' (int): Year of each record.
            - 'MON' (int): Month of each record (1 to 12).
            - 'PERCmm' (float): Daily infiltration values in millimeters.
            - 'SURQ_GENmm' (float): Daily surface runoff values in millimeters.

    Returns:
        DataFrame: A multi-indexed DataFrame (by year and month) with columns:
            - 'Volumen_Infiltración (m3)': Monthly infiltration volume per hectare.
            - 'Volumen_Escurrimiento (m3)': Monthly runoff volume per hectare.
    """
    años = df['YEAR'].unique()

    dataframes = []

    for i in años:
        df_filtrado = df[df['YEAR'] == i]
        suma = df_filtrado.groupby('MON').sum()
        vol = pd.DataFrame({
            'Volumen_Infiltración (m3)': (suma['PERCmm'] * 10000) / 1000,
            'Volumen_Escurrimiento (m3)': (suma['SURQ_GENmm'] * 10000) / 1000
        })

        dataframes.append(vol)

    años_str = [str(i) for i in años]
    df_final = pd.concat(dataframes, keys = años_str).round(2)
    df_final.index.names = ['Año', 'Mes']
    return(df_final)


def graficar_precipitacion(df, ruta_1, ruta_2):
    """
    Generates two plots based on daily precipitation data:

    1. A line plot showing the historical annual mean precipitation.
    2. A faceted time series plot showing the historical monthly mean precipitation per year.

    Parameters:
        df (pandas.DataFrame): DataFrame containing daily precipitation data with the following columns:
            - 'YEAR' (int): Year of each record.
            - 'MON' (int): Month of each record (1–12).
            - 'PRECIPmm' (float): Daily precipitation values in millimeters.
        ruta_1 (str): File path to save the first plot (annual mean).
        ruta_2 (str): File path to save the second plot (monthly means per year).

    Returns:
        None: The function saves the generated plots as image files at the specified paths.
    """

    años = df['YEAR'].unique()
    años_str = [str(i) for i in años]
    prom_año = df.groupby(by='YEAR')[['PRECIPmm']].mean().round(2)
    prom_año = prom_año.reset_index()

    sbn.set_theme(style="ticks")

    sbn.lineplot(x="YEAR", y="PRECIPmm",
                 data=prom_año)
    plt.xticks(prom_año["YEAR"].unique(), rotation=45)
    plt.title(f'Precipitación media anual histórica ({años_str[0]}-{años_str[-1]})',
              fontsize=14,
              fontweight="bold")
    plt.xlabel("Año")
    plt.ylabel("Precipitación (mm)")

    plt.tight_layout()
    plt.savefig(ruta_1);

    list_prom_mes = []

    for i in años:
        df_filtrado = df[df['YEAR'] == i]
        prom_año = df_filtrado.groupby(by='MON').mean().round(2)
        list_prom_mes.append(prom_año)

    df_prom_mes = pd.concat(list_prom_mes,
                            keys=años_str)
    df_prom_mes = df_prom_mes.reset_index()
    df_prom_mes = df_prom_mes.rename(columns={"level_0": "AÑO",
                                              'MON': 'MES'})
    df_prom_mes = df_prom_mes.drop(columns='YEAR')

    meses = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    df_prom_mes["MES"] = df_prom_mes["MES"].map(meses)

    #
    #

    sbn.set_theme(style="ticks")

    g = sbn.relplot(
        data=df_prom_mes,
        x="MES", y="PRECIPmm", col="AÑO", hue="AÑO",
        kind="line", palette="crest", linewidth=4, zorder=5,
        col_wrap=3, height=2, aspect=1.5, legend=False,
    )

    for year, ax in g.axes_dict.items():
        ax.text(.8, .85, year, transform=ax.transAxes, fontweight="bold")

        sbn.lineplot(
            data=df_prom_mes, x="MES", y="PRECIPmm", units="AÑO",
            estimator=None, color=".7", linewidth=1, ax=ax,
        )

    ax.set_xticks(ax.get_xticks()[::2])

    g.set_titles("")
    g.set_axis_labels("Meses", "Precipitación (mm)")
    g.fig.suptitle(f'Precipitación media mensual histórica ({años_str[0]}-{años_str[-1]})',
                   fontsize=14,
                   fontweight="bold")
    g.tight_layout()
    g.savefig(ruta_2);

