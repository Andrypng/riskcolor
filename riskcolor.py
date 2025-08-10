import logging
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime as dt
from keep_alive import keep_alive

BOT_TOKEN = "7804851171:AAEp5TCO3e_-RsWSwGnyaHVpuZU5XA3KQC4"

keep_alive()

# Diccionario para guardar cambios de color {fecha: color_hex}
cambios_color = {}

# Mapeo de nombres a colores reales (sin espacios y en minúsculas)
mapa_colores = {
    "morado": "#800080",
    "azul": "#0000FF",
    "celeste": "#00FFFF",
    "verdeoscuro": "#006400",
    "verdeclaro": "#90EE90",
    "amarillo": "#FFFF00",
    "naranja": "#FFA500",
    "rosado": "#FFC0CB",
    "rojo": "#FF0000",
    "negro": "#000000"
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Usa /color YYYY-MM-DD color para cambiar el color del gráfico desde esa fecha.\n"
        f"Opciones: {', '.join(mapa_colores.keys())}"
    )

async def color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Formato incorrecto. Usa: /color YYYY-MM-DD color")
        return

    fecha_str = context.args[0]
    color_nombre = context.args[1].lower()

    try:
        # Forzamos formato Año/Mes/Día
        fecha = dt.datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        await update.message.reply_text("Fecha inválida. Usa formato YYYY-MM-DD (Ej: 2025-08-09).")
        return

    if color_nombre not in mapa_colores:
        await update.message.reply_text(f"Color no válido. Opciones: {', '.join(mapa_colores.keys())}")
        return

    cambios_color[fecha] = mapa_colores[color_nombre]
    await update.message.reply_text(f"Color cambiado a {color_nombre} desde {fecha.strftime('%Y-%m-%d')}")
    await generar_grafico(update, context)

async def generar_grafico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = yf.download("BTC-USD", period="max", interval="1d")
    df.reset_index(inplace=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    color_actual = "#000000"  # negro por defecto

    for i in range(len(df) - 1):
        fecha_actual = df["Date"].iloc[i]

        for cambio_fecha in sorted(cambios_color.keys()):
            if fecha_actual >= cambio_fecha:
                color_actual = cambios_color[cambio_fecha]

        ax.plot(df["Date"].iloc[i:i+2], df["Close"].iloc[i:i+2], color=color_actual)

    ax.set_yscale("log")
    ax.set_title("Precio Histórico BTC con Cambios de Color")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Precio (USD) - Escala logarítmica")

    # Forzar formato Año/Mes/Día en el eje X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("grafico.png")
    plt.close()

    await update.message.reply_photo(photo=open("grafico.png", "rb"))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("color", color))

if __name__ == "__main__":
    app.run_polling()
