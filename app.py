# Import python package
from app import create_app

app = create_app()

# Run webserver
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)


# class Lietotajs(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     vards = db.Column(db.String(100), nullable=False)
#     uzvards = db.Column(db.String(100), nullable=False)

#     def __repr__(self):
#         return f"Lietotajs('{self.vards}', '{self.uzvards}')"

# @app.route("/lietotaji")
# def lietotaji():
#     lietotaji = Lietotajs.query.all()
#     return render_template("lietotaji.html", lietotaji=lietotaji)

# @app.route("/dati")
# def dati():
#     dati = pd.read_csv("dati.csv")
#     plt.figure(figsize=(10,6))
#     plt.plot(dati["x"], dati["y"])
#     plt.title("Datu vizualizācija")
#     plt.xlabel("x")
#     plt.ylabel("y")
#     plt.savefig("static/plot.png")
#     return render_template("dati.html")

# app.run(host="127.0.0.1", port=80)