from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "sena2026"

# ==========================
# Usuarios de prueba (Simulados con Roles)
# ==========================
usuarios = {
    "admin@sena.edu.co": {
        "password": "123",
        "rol": "admin"
    },
    "aprendiz@sena.edu.co": {
        "password": "123",
        "rol": "aprendiz",
        "ficha": "3407184"  # <-- Le asignamos una ficha fija para que tenga lógica de roles
    }
}

# ==========================
# Home
# ==========================
@app.route('/')
def home():
    return render_template('home.html')


# ==========================
# Login
# ==========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        if correo in usuarios and usuarios[correo]["password"] == password:
            session["usuario"] = correo
            session["rol"] = usuarios[correo]["rol"]
            
            # Si es aprendiz, guardamos su número de ficha en la sesión
            if usuarios[correo]["rol"] == "aprendiz":
                session["ficha"] = usuarios[correo]["ficha"]
                
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Correo o contraseña incorrectos.")
    return render_template("login.html")

# ==========================
# Logout
# ==========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==========================
# Instructores
# ==========================
@app.route('/instructores')
def instructores():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    return render_template('instructores.html')


@app.route('/crear_instructor')
def crear_instructor():
    if session.get("rol") != "admin":
        return redirect(url_for("home"))
    return render_template('crear_instructor.html')


@app.route('/actualizar_instructor')
def actualizar_instructor():
    if session.get("rol") != "admin":
        return redirect(url_for("home"))
    return render_template('actualizar_instructor.html')


@app.route('/eliminar_instructor')
def eliminar_instructor():
    if session.get("rol") != "admin":
        return redirect(url_for("home"))
    return render_template('eliminar_instructor.html')


# ==========================
# Contacto
# ==========================
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


# ==========================
# Evaluaciones
# ==========================
@app.route('/evaluaciones')
def evaluaciones():
    if not session.get("usuario"):
        return redirect(url_for("login"))
    return render_template("evaluaciones.html")


# NUEVA RUTA: Modificar preguntas (Solo Admin)
@app.route('/evaluaciones/editar')
def editar_preguntas():
    if session.get("rol") != "admin":
        return redirect(url_for("home"))
    # Aquí debes asegurarte de tener un archivo llamado 'editar_preguntas.html' dentro de templates/
    return render_template("editar_preguntas.html")


# ==========================
# Fichas
# ==========================
@app.route('/fichas')
def fichas():
    if session.get("rol") != "admin":
        return redirect(url_for("home"))
    return render_template('fichas.html')


# ==========================
# Reportes
# ==========================
@app.route('/reportes')
def reportes():
    if session.get("rol") != "admin":
        return redirect(url_for("home"))
    return render_template('reportes.html')


# ==========================
# Ejecutar aplicación
# ==========================
if __name__ == '__main__':
    app.run(debug=True)