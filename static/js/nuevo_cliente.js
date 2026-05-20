// =========================================
// PLACEHOLDER DOCUMENTO
// =========================================
function actualizarPlaceholderDocumento() {

    const tipo =
        document.getElementById('tipo_documento').value;

    const input =
        document.getElementById('numero_documento');

    const label =
        document.getElementById('label_documento');

    if (tipo === 'RUC') {

        input.placeholder = '11 dígitos';
        label.innerHTML = 'RUC *:';

    }

    else if (tipo === 'DNI') {

        input.placeholder = '8 dígitos';
        label.innerHTML = 'DNI *:';

    }

    else {

        input.placeholder = 'Ingrese el número';
        label.innerHTML = 'Número de Documento *:';

    }

}

document.addEventListener('DOMContentLoaded', () => {

    let contadorContactos = 0;
    let contadorPuntos = 0;

    const listaContactos =
        document.getElementById('listaContactos');

    const listaPuntos =
        document.getElementById('listaPuntos');

    // =========================================
    // CONTADORES
    // =========================================
    function actualizarContadores() {
        return;
    }

    // =========================================
    // AGREGAR CONTACTO
    // =========================================
    function agregarContacto(data = {}) {

        contadorContactos++;

        const div =
            document.createElement('div');

        div.classList.add('item-agregable');

        div.innerHTML = `

        <button type="button" class="btn-eliminar">
            🗑️
        </button>

        <div class="row">

            <div class="col-md-6 mb-3">

                <label>Nombre</label>

                <input
                    class="form-control"
                    data-field="nombre_contacto"
                    value="${data.nombre_contacto || ''}"
                    required
                >

            </div>

            <div class="col-md-6 mb-3">

                <label>Cargo</label>

                <input
                    class="form-control"
                    data-field="cargo"
                    value="${data.cargo || ''}"
                >

            </div>

        </div>

        <div class="row">

            <div class="col-md-6 mb-3">

                <label>Email</label>

                <input
                    class="form-control"
                    data-field="email"
                    value="${data.email || ''}"
                >

            </div>

            <div class="col-md-6 mb-3">

                <label>Teléfono</label>

                <input
                    class="form-control"
                    data-field="telefono"
                    value="${data.telefono || ''}"
                >

            </div>

        </div>

        <div class="checkbox-group">

            <input
                type="checkbox"
                data-field="principal"
                ${data.principal ? 'checked' : ''}
            >

            <label>Principal</label>

        </div>
        `;

        listaContactos.appendChild(div);

        actualizarContadores();

    }

    // =========================================
    // AGREGAR PUNTO
    // =========================================
    function agregarPunto(data = {}) {

        contadorPuntos++;

        const div =
            document.createElement('div');

        div.classList.add('item-agregable');

        div.innerHTML = `

        <button type="button" class="btn-eliminar">
            🗑️
        </button>

        <div class="col-md-6 mb-3">

            <label>Punto de Entrega</label>

            <input
                class="form-control"
                data-field="nombre_punto"
                value="${data.nombre_punto || ''}"
                required
            >

        </div>

        <div class="col-md-6 mb-3">

            <label>Dirección</label>

            <input
                class="form-control"
                data-field="direccion"
                value="${data.direccion || ''}"
                required
            >

        </div>

        <div class="row">

            <!-- DEPARTAMENTO -->
            <div class="col-md-4 mb-3">

                <label class="form-label">
                    Departamento
                </label>

                <input
                    type="text"
                    class="form-control buscar-departamento"
                    placeholder="Buscar departamento..."
                >

                <select
                    class="form-select mt-2"
                    data-field="departamento"
                >

                    <option value="">Seleccione</option>

                    <option value="Amazonas">Amazonas</option>
                    <option value="Áncash">Áncash</option>
                    <option value="Apurímac">Apurímac</option>
                    <option value="Arequipa">Arequipa</option>
                    <option value="Ayacucho">Ayacucho</option>
                    <option value="Cajamarca">Cajamarca</option>
                    <option value="Callao">Callao</option>
                    <option value="Cusco">Cusco</option>
                    <option value="Huancavelica">Huancavelica</option>
                    <option value="Huánuco">Huánuco</option>
                    <option value="Ica">Ica</option>
                    <option value="Junín">Junín</option>
                    <option value="La Libertad">La Libertad</option>
                    <option value="Lambayeque">Lambayeque</option>
                    <option value="Lima">Lima</option>
                    <option value="Loreto">Loreto</option>
                    <option value="Madre de Dios">Madre de Dios</option>
                    <option value="Moquegua">Moquegua</option>
                    <option value="Pasco">Pasco</option>
                    <option value="Piura">Piura</option>
                    <option value="Puno">Puno</option>
                    <option value="San Martín">San Martín</option>
                    <option value="Tacna">Tacna</option>
                    <option value="Tumbes">Tumbes</option>
                    <option value="Ucayali">Ucayali</option>

                </select>

            </div>

            <!-- PROVINCIA -->
            <div class="col-md-4 mb-3">

                <label class="form-label">
                    Provincia
                </label>

                <input
                    type="text"
                    class="form-control buscar-provincia"
                    placeholder="Buscar provincia..."
                >

                <select
                    class="form-select mt-2"
                    data-field="provincia"
                >

                    <option value="">Seleccione</option>

                </select>

            </div>

            <!-- DISTRITO -->
            <div class="col-md-4 mb-3">

                <label class="form-label">
                    Distrito
                </label>

                <input
                    type="text"
                    class="form-control buscar-distrito"
                    placeholder="Buscar distrito..."
                >

                <select
                    class="form-select mt-2"
                    data-field="distrito"
                >

                    <option value="">Seleccione</option>

                </select>

            </div>

        </div>

        <div class="row">

            <div class="col-md-6 mb-3">

                <label>Contacto de Entrega</label>

                <input
                    class="form-control"
                    data-field="responsable"
                    value="${data.responsable || ''}"
                >

            </div>

            <div class="col-md-6 mb-3">

                <label>Teléfono</label>

                <input
                    class="form-control"
                    data-field="telefono"
                    value="${data.telefono || ''}"
                >

            </div>

        </div>

        <div class="col-md-6 mb-3">

            <label>Condición de Pago</label>

            <select
                data-field="condicion_pago"
                class="form-select select-condicion-pago"
            >

                <option value="">
                    Seleccione
                </option>

                <option
                    value="Contado"
                    ${data.condicion_pago === 'Contado' ? 'selected' : ''}
                >
                    Contado
                </option>

                <option
                    value="Credito"
                    ${data.condicion_pago === 'Credito' ? 'selected' : ''}
                >
                    Crédito
                </option>

            </select>

        </div>

        <div
            class="form-group campo-credito"
            style="display:${data.condicion_pago === 'Credito' ? 'block' : 'none'};"
        >

            <label>Tiempo de Crédito</label>

            <input
                type="text"
                class="form-control"
                data-field="tiempo_credito"
                placeholder="Ej: 30 días"
                value="${data.tiempo_credito || ''}"
            >

        </div>

        <div class="checkbox-group">

            <input
                type="checkbox"
                data-field="principal"
                ${data.principal ? 'checked' : ''}
            >

            <label>Principal</label>

        </div>
        `;

        listaPuntos.appendChild(div);

// =========================================
// UBIGEO PERÚ
// =========================================
const ubigeo = {

    Lima: {

        Lima: [

            'Ancón',
            'Ate',
            'Barranco',
            'Breña',
            'Carabayllo',
            'Chaclacayo',
            'Chorrillos',
            'Cieneguilla',
            'Comas',
            'El Agustino',
            'Independencia',
            'Jesús María',
            'La Molina',
            'La Victoria',
            'Lince',
            'Los Olivos',
            'Lurigancho',
            'Lurín',
            'Magdalena del Mar',
            'Miraflores',
            'Pachacámac',
            'Pueblo Libre',
            'Puente Piedra',
            'Rímac',
            'San Borja',
            'San Isidro',
            'San Juan de Lurigancho',
            'San Juan de Miraflores',
            'San Martín de Porres',
            'San Miguel',
            'Santa Anita',
            'Santiago de Surco',
            'Surquillo',
            'Villa El Salvador',
            'Villa María del Triunfo'

        ],

        Huaura: [
            'Huacho',
            'Hualmay',
            'Vegueta'
        ],

        Huaral: [
            'Huaral',
            'Chancay',
            'Aucallama'
        ]

    },

    Arequipa: {

        Arequipa: [
            'Cerro Colorado',
            'Yanahuara',
            'Cayma'
        ]

    },

    Cusco: {

        Cusco: [
            'Wanchaq',
            'Santiago',
            'San Sebastián'
        ]

    }

};

// =========================================
// SELECTS UBIGEO
// =========================================
const selectDepartamento =
    div.querySelector('[data-field="departamento"]');

const selectProvincia =
    div.querySelector('[data-field="provincia"]');

const selectDistrito =
    div.querySelector('[data-field="distrito"]');

// =========================================
// CAMBIO DEPARTAMENTO
// =========================================
selectDepartamento.addEventListener('change', function () {

    const departamento = this.value;

    selectProvincia.innerHTML =
        '<option value="">Seleccione</option>';

    selectDistrito.innerHTML =
        '<option value="">Seleccione</option>';

    if (!ubigeo[departamento]) return;

    Object.keys(ubigeo[departamento]).forEach(provincia => {

        selectProvincia.innerHTML += `
            <option value="${provincia}">
                ${provincia}
            </option>
        `;

    });

});

// =========================================
// CAMBIO PROVINCIA
// =========================================
selectProvincia.addEventListener('change', function () {

    const departamento =
        selectDepartamento.value;

    const provincia =
        this.value;

    selectDistrito.innerHTML =
        '<option value="">Seleccione</option>';

    if (
        !ubigeo[departamento] ||
        !ubigeo[departamento][provincia]
    ) return;

    ubigeo[departamento][provincia]
        .forEach(distrito => {

        selectDistrito.innerHTML += `
            <option value="${distrito}">
                ${distrito}
            </option>
        `;

    });

});

        // =========================================
        // CONDICION PAGO
        // =========================================
        const selectCondicionPago =
            div.querySelector('.select-condicion-pago');

        const campoCredito =
            div.querySelector('.campo-credito');

        selectCondicionPago.addEventListener('change', function () {

            if (this.value === 'Credito') {

                campoCredito.style.display = 'block';

            } else {

                campoCredito.style.display = 'none';

            }

        });

        actualizarContadores();

    }

    // =========================================
    // BOTONES
    // =========================================
    const btnAgregarContacto =
        document.getElementById('btnAgregarContacto');

    if (btnAgregarContacto) {

        btnAgregarContacto.addEventListener('click', () => {
            agregarContacto();
        });

    }

    const btnAgregarPunto =
        document.getElementById('btnAgregarPunto');

    if (btnAgregarPunto) {

        btnAgregarPunto.addEventListener('click', () => {
            agregarPunto();
        });

    }

    // =========================================
    // ELIMINAR
    // =========================================
    document.addEventListener('click', (e) => {

        if (e.target.classList.contains('btn-eliminar')) {

            e.target.closest('.item-agregable').remove();

            actualizarContadores();

        }

    });

    // =========================================
    // SOLO 1 PRINCIPAL
    // =========================================
    document.addEventListener('change', (e) => {

        if (e.target.dataset.field === 'principal') {

            const container =
                e.target.closest('#lista-contactos')
                    ? listaContactos
                    : listaPuntos;

            container.querySelectorAll('[data-field="principal"]')
                .forEach(cb => cb.checked = false);

            e.target.checked = true;

        }

    });

    // =========================================
// OBTENER DATA
// =========================================
function obtenerData() {

    // =====================================
    // CONTACTOS
    // =====================================
    const contactos = [];

    listaContactos
        .querySelectorAll('.item-agregable')
        .forEach(item => {

            contactos.push({

                nombre_contacto:
                    item.querySelector('[data-field="nombre_contacto"]')?.value.trim() || '',

                cargo:
                    item.querySelector('[data-field="cargo"]')?.value.trim() || '',

                email:
                    item.querySelector('[data-field="email"]')?.value.trim() || '',

                telefono:
                    item.querySelector('[data-field="telefono"]')?.value.trim() || '',

                principal:
                    item.querySelector('[data-field="principal"]')?.checked || false

            });

        });

    // =====================================
    // PUNTOS ENTREGA
    // =====================================
    const puntos = [];

    listaPuntos
        .querySelectorAll('.item-agregable')
        .forEach(item => {

            puntos.push({

                nombre:
                    item.querySelector('[data-field="nombre_punto"]')?.value.trim() || '',

                direccion:
                    item.querySelector('[data-field="direccion"]')?.value.trim() || '',

                departamento:
                    item.querySelector('[data-field="departamento"]')?.value || '',

                provincia:
                    item.querySelector('[data-field="provincia"]')?.value || '',

                distrito:
                    item.querySelector('[data-field="distrito"]')?.value || '',

                responsable:
                    item.querySelector('[data-field="responsable"]')?.value.trim() || '',

                telefono:
                    item.querySelector('[data-field="telefono"]')?.value.trim() || '',

                condicion_pago:
                    item.querySelector('[data-field="condicion_pago"]')?.value || '',

                tiempo_credito:
                    item.querySelector('[data-field="tiempo_credito"]')?.value.trim() || '',

                principal:
                    item.querySelector('[data-field="principal"]')?.checked || false

            });

        });

    console.log("📞 CONTACTOS:", contactos);
    console.log("📦 PUNTOS:", puntos);

    return {

        contactos,
        puntos_entrega: puntos

    };

}

    // =========================================
    // SUBMIT
    // =========================================
    const formCliente =
        document.getElementById('formCliente');

    if (formCliente) {

        formCliente.addEventListener('submit', async (e) => {

            e.preventDefault();

            const base = {

                tipo_documento:
                    document.getElementById('tipo_documento').value,

                numero_documento:
                    document.getElementById('numero_documento').value,

                razon_social:
                    document.getElementById('razon_social').value,

                nombre_comercial:
                    document.getElementById('nombre_comercial').value,

                direccion_fiscal:
                    document.getElementById('direccion_fiscal').value

            };

            const extra =
                obtenerData();

            const data = {
                ...base,
                ...extra
            };

            console.log("📤 ENVIANDO:", data);

            if (data.contactos.length === 0) {

                alert("Agrega al menos un contacto");
                return;

            }

            try {

                const res = await fetch('/api/clientes/guardar', {

                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json'
                    },

                    body: JSON.stringify(data)

                });

                const json = await res.json();

                console.log(json);

                if (json.success) {

                    alert("✅ Cliente guardado correctamente");

                    location.reload();

                } else {

                    alert(json.error || "Error al guardar");

                }

            } catch (err) {

                console.error(err);

                alert("Error del servidor");

            }

        });

    }

    // =========================================
    // INICIAL
    // =========================================
    agregarContacto();

    agregarPunto();

    actualizarContadores();

});
