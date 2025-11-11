from flask import Flask, render_template, request
import requests
import plotly.graph_objs as go
import plotly.offline as pyo

app = Flask(__name__)
API_KEY = "16bc092eb7ca8f669c73bac989ab5b7f"  # Replace with your Marketstack API key

@app.route("/", methods=["GET", "POST"])
def index():
    stocks_data = []
    charts = []
    error = None

    if request.method == "POST":
        # Read input symbols
        symbols = request.form.get("symbols").upper().replace(" ", "").split(",")

        for symbol in symbols:
            url = f"http://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols={symbol}&limit=30"
            try:
                response = requests.get(url)
                data = response.json()

                if "data" not in data or len(data["data"]) == 0:
                    error = f"No data found for {symbol}."
                    continue
                latest = data["data"][0]
                stocks_data.append(latest)

                # Chart
                dates = [d["date"][:10] for d in reversed(data["data"])]
                closes = [d["close"] for d in reversed(data["data"])]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=closes,
                    mode='lines+markers',
                    name=symbol,
                    line=dict(width=3),
                    marker=dict(size=6)
                ))
                fig.update_layout(
                    title=f'{symbol} Closing Pricess (Last 30 Days)',
                    xaxis_title='Date',
                    yaxis_title='Close Price',
                    template="plotly_dark",
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                chart_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
                charts.append(chart_div)

            except Exception as e:
                error = f"Error fetching data: {e}"

    return render_template("index.html", stocks=stocks_data, charts=charts, error=error)

if __name__ == "__main__":
    app.run(debug=True)
