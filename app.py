from flask import Flask, render_template, request
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

def boole_rule(func_str, a, b):
    n = 4
    h = (b - a) / n

    x_vals = [a + i * h for i in range(n + 1)]

    def f(x):
        return eval(func_str, {"x": x, "math": math})

    y_vals = [f(xi) for xi in x_vals]

    result = (2 * h / 45) * (
        7 * y_vals[0] +
        32 * y_vals[1] +
        12 * y_vals[2] +
        32 * y_vals[3] +
        7 * y_vals[4]
    )

    return result, list(zip(x_vals, y_vals))


def generate_plot(func_str, a, b, table):
    def f(x):
        return eval(func_str, {"x": x, "math": math})

    # Smooth curve
    x_curve = np.linspace(a, b, 400)
    y_curve = np.array([f(xi) for xi in x_curve])

    # Fill x range for shading
    x_fill = np.linspace(a, b, 400)
    y_fill = np.array([f(xi) for xi in x_fill])

    # Node points from table
    x_nodes = [row[0] for row in table]
    y_nodes = [row[1] for row in table]

    fig, ax = plt.subplots(figsize=(8, 4.2))

    # Dark background matching the UI
    fig.patch.set_facecolor('#0b0f1a')
    ax.set_facecolor('#111827')

    # Shaded area under curve
    ax.fill_between(x_fill, y_fill, alpha=0.15, color='#4f8ef7', zorder=1)
    ax.fill_between(x_fill, y_fill, alpha=0.07, color='#38d9a9', zorder=1)

    # Main curve
    ax.plot(x_curve, y_curve, color='#4f8ef7', linewidth=2.2, zorder=3, label='f(x)')

    # Vertical lines at nodes
    for xi, yi in zip(x_nodes, y_nodes):
        ax.plot([xi, xi], [0, yi], color='#263549', linewidth=1, linestyle='--', zorder=2)

    # Node points
    ax.scatter(x_nodes, y_nodes, color='#38d9a9', s=60, zorder=5,
               edgecolors='#0b0f1a', linewidths=1.5, label='Nodes')

    # Zero baseline
    ax.axhline(0, color='#1f2d45', linewidth=1, zorder=1)

    # Spine and tick styling
    for spine in ax.spines.values():
        spine.set_edgecolor('#1f2d45')
        spine.set_linewidth(1)

    ax.tick_params(colors='#7a8fad', labelsize=9, length=4)
    ax.xaxis.label.set_color('#7a8fad')
    ax.yaxis.label.set_color('#7a8fad')

    ax.set_xlabel('x', fontsize=10, labelpad=8)
    ax.set_ylabel('f(x)', fontsize=10, labelpad=8)

    # Grid
    ax.grid(True, color='#1a2235', linewidth=0.8, linestyle='-', zorder=0)
    ax.set_axisbelow(True)

    # Legend
    legend = ax.legend(
        facecolor='#1a2235',
        edgecolor='#1f2d45',
        labelcolor='#7a8fad',
        fontsize=9,
        framealpha=1
    )

    plt.tight_layout(pad=1.5)

    # Encode to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                facecolor='#0b0f1a', edgecolor='none')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return img_b64


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    table = None
    error = None
    plot_img = None

    if request.method == "POST":
        try:
            func = request.form["function"]
            a = float(request.form["a"])
            b = float(request.form["b"])

            if a >= b:
                raise ValueError("Lower limit (a) must be less than upper limit (b).")

            result, table = boole_rule(func, a, b)
            plot_img = generate_plot(func, a, b, table)

        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template("index.html", result=result, table=table,
                           error=error, plot_img=plot_img)


if __name__ == "__main__":
    app.run(debug=True)